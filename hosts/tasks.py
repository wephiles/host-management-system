#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""
异步任务
"""

import string
import random
import logging
from datetime import date
from cryptography.fernet import Fernet
from django.conf import settings
import paramiko
from celery import shared_task
from django.db.models import Count
from .models import Host, HostDailyStat, DataCenter

logger = logging.getLogger(__name__)


def get_fernet():
    return Fernet(settings.FERNET_SECRET_KEY)


def generate_random_password(length=16):
    """生成强随机密码"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))


@shared_task(bind=True, max_retries=2)
def change_host_password_task(self, host_id):
    """单台主机修改密码的子任务"""
    try:
        host = Host.objects.get(id=host_id)
        fernet = get_fernet()

        # 1. 生成新密码
        new_password = generate_random_password()

        # 2. 通过 SSH 连接主机修改密码
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 获取旧密码解密
        old_password = fernet.decrypt(host.encrypted_password).decode(
            'utf-8') if host.encrypted_password else 'old_default_pwd'

        ssh.connect(hostname=host.ip_address, username='root', password=old_password, timeout=5)

        # Linux下非交互式修改root密码命令
        cmd = f"echo 'root:{new_password}' | chpasswd"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()

        ssh.close()

        if exit_status != 0:
            raise Exception(f"SSH exec failed: {stderr.read().decode()}")

        # 3. 加密新密码并保存到数据库
        encrypted_pwd = fernet.encrypt(new_password.encode('utf-8'))
        host.encrypted_password = encrypted_pwd
        host.save(update_fields=['encrypted_password'])

        logger.info(f"Successfully changed password for host {host.ip_address}")
        return True

    except Exception as e:
        logger.error(f"Failed to change password for host {host_id}: {str(e)}")
        # 重试机制
        raise self.retry(exc=e, countdown=60)


@shared_task
def rotate_all_passwords():
    """定时任务：每8小时修改所有主机密码"""
    hosts = Host.objects.all()
    if not hosts.exists():
        logger.info("No hosts found for password rotation.")
        return

    for host in hosts:
        # 分发子任务，避免一台挂了影响全部
        change_host_password_task.delay(host.id)


@shared_task
def generate_daily_stats():
    """定时任务：每天00:00按城市和机房维度统计主机数量"""
    today = date.today()

    # 使用 Django ORM 按城市和机房进行分组聚合统计
    stats = Host.objects.values('city', 'datacenter').annotate(
        host_count=Count('id')
    )

    created_count = 0
    for stat in stats:
        city_id = stat.get('city')
        dc_id = stat.get('datacenter')

        # 过滤掉被物理删除但外键置空的数据
        if not city_id or not dc_id:
            continue

        # 使用 update_or_create 保证幂等性
        obj, created = HostDailyStat.objects.update_or_create(
            date=today,
            city_id=city_id,
            datacenter_id=dc_id,
            defaults={'host_count': stat['host_count']}
        )
        if created:
            created_count += 1

    logger.info(f"Daily stats generated for {today}. New records: {created_count}")
    