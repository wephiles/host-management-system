#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""
Admin 管理后台
"""
from django.contrib import admin

# Register your models here.


from .models import City, DataCenter, HostDailyStat

from django.contrib import admin
from .models import Host


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    # 编辑页显示的字段
    fieldsets = (
        (None, {
            'fields': ('name', 'code')
        }),
    )


@admin.register(DataCenter)
class DataCenterAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('name', 'city')  # 添加更多字段
    # 编辑页显示的字段
    fieldsets = (
        (None, {
            'fields': ('name', 'city')
        }),
    )


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('hostname', 'ip_address', 'datacenter', 'created_at')
    # 编辑页显示的字段
    fieldsets = (
        (None, {
            'fields': ('hostname', 'ip_address', 'datacenter')
        }),
        ('安全信息', {
            'fields': ('encrypted_password', 'created_at'),
            'classes': ('collapse',)  # 可折叠
        }),
    )

    # 设置为只读字段（防止在Admin中修改）
    readonly_fields = [
        'encrypted_password',
        'created_at',
    ]

    # 可选：自定义字段的显示样式（二进制数据可能需要转换）
    def display_encrypted_password(self, obj):
        if obj.encrypted_password:
            # 将二进制密文转换为 Base64 字符串显示（更易读）
            import base64
            return base64.b64encode(obj.encrypted_password).decode('utf-8')
        return "未设置"

    display_encrypted_password.short_description = "加密密码（Base64）"


@admin.register(HostDailyStat)
class HostDailyStatAdmin(admin.ModelAdmin):
    list_display = ('date', 'city', 'datacenter', 'host_count')
