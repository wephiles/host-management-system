#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""
Django local configs for hosts project.
"""

import os
from pathlib import Path

from celery.schedules import crontab

from host_manage.settings import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
                            'django-insecure-test-key-for-interview-please-change-in-prod')

# ==================== 测试模式开关 ====================
# 设置为 True 时，跳过真实SSH连接，用于本地无主机环境测试
MOCK_SSH = True

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方App
    'rest_framework',
    'django_celery_beat',
    # 本地App
    'hosts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 注册自定义耗时中间件（放在最后，统计视图执行时间）
    'middleware.RequestTimeMiddleware',
]

ROOT_URLCONF = 'host_manage.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==================== Celery 配置 ====================
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = False

# ==================== 定时任务配置 ====================
CELERY_BEAT_SCHEDULE = {
    'rotate-root-password-every-8-hours': {
        'task': 'hosts.tasks.rotate_all_passwords',
        'schedule': crontab(hour='*/8', minute=0),  # 每8小时执行
    },
    'generate-daily-stats': {
        'task': 'hosts.tasks.generate_daily_stats',
        'schedule': crontab(hour=0, minute=0),  # 每天 00:00 执行
    },
}

# ==================== 加密配置 ====================
FERNET_SECRET_KEY = os.environ.get('FERNET_SECRET_KEY',
                                   b'iW5rmRqMcbyhK_oImcVtMKAodb2VCTZDbqDWV_iBlbM=')

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    # 分页 -- 直接使用 Django 封装好的分页类
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # 默认每页20条
}

# --END--
