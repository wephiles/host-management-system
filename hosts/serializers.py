#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""
序列化器
"""

from rest_framework import serializers
from .models import City, DataCenter, Host, HostDailyStat


class CitySerializer(serializers.ModelSerializer):
    """序列化城市模型"""

    class Meta:
        model = City
        fields = '__all__'


class DataCenterSerializer(serializers.ModelSerializer):
    """序列化机房模型"""

    class Meta:
        model = DataCenter
        fields = '__all__'


class HostSerializer(serializers.ModelSerializer):
    """序列化主机"""
    # 将二进制密码转为字符串展示（仅用于内部查看，对外接口建议屏蔽）
    password_display = serializers.CharField(source='encrypted_password', read_only=True)

    class Meta:
        model = Host
        fields = ['id', 'hostname', 'ip_address', 'city', 'datacenter', 'encrypted_password', 'created_at']
        # 增删改查时允许传入密码进行初始加密，但不对外返回明文
        extra_kwargs = {
            'encrypted_password': {'write_only': True, 'required': False}
        }


class HostDailyStatSerializer(serializers.ModelSerializer):
    """序列化主机统计模型"""

    class Meta:
        model = HostDailyStat
        fields = '__all__'
