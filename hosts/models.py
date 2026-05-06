#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.


"""
主机模型
"""

from django.db import models


# Create your models here.


class City(models.Model):
    """城市模型"""
    name = models.CharField(
        '城市名称',
        max_length=50,
        unique=True,
        null=False,
        blank=False,
    )
    code = models.CharField(
        '城市编号',
        max_length=10,
        unique=True,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f'{self.name}({self.code})'


class DataCenter(models.Model):
    """机房模型"""
    name = models.CharField(
        '机房名称',
        max_length=50,
        unique=True,
        null=False,
        blank=False
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='datacenters',
        verbose_name='所在城市',
    )

    def __str__(self):
        return f'{self.city.name}-{self.name}'


class Host(models.Model):
    """主机模型"""
    hostname = models.CharField(
        '主机名',
        max_length=100,
        unique=True,
        null=False,
        blank=False
    )

    ip_address = models.GenericIPAddressField(
        'IP地址',
        unique=True,
    )

    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        related_name='hosts',
        verbose_name='所在城市',
    )

    datacenter = models.ForeignKey(
        DataCenter,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='所在机房',
        related_name='hosts',
    )

    encrypted_password = models.BinaryField(
        '加密后的ROOT密码',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.hostname}({self.ip_address})'


class HostDailyStat(models.Model):
    """主机每日统计模型"""
    date = models.DateField(
        verbose_name='统计日期',
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name='城市',
    )

    datacenter = models.ForeignKey(
        DataCenter,
        on_delete=models.CASCADE,
        verbose_name='机房',
    )

    host_count = models.PositiveIntegerField(
        default=0,
        verbose_name='主机数量'
    )

    class Meta:
        verbose_name = '主机日统计'
        # 联合唯一约束 同一天、同一城市、同一机房只能有一条记录
        unique_together = ('date', 'city', 'datacenter')

    def __str__(self):
        return f'{self.date} | {self.city.name} | {self.datacenter.name} | 数量 {self.host_count}'
