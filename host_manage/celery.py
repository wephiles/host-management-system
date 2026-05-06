#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""
Celery 实例
"""

from celery import Celery
import os

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'host_manage.settings')

app = Celery('host_manage')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
