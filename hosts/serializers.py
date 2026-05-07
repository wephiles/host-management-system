#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""
序列化器
"""

from rest_framework import serializers
from cryptography.fernet import Fernet
from django.conf import settings
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
    encrypted_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    # 主机模型没有 city 字段, 此处显式写出
    city = serializers.CharField(source="datacenter.city", read_only=True)

    class Meta:
        model = Host
        fields = ['id', 'hostname', 'ip_address', 'city', 'datacenter', 'encrypted_password', 'created_at']

    def create(self, validated_data):
        # 新增记录时 自定义加密逻辑
        password = validated_data.pop("encrypted_password", None)
        if password:
            fernet = Fernet(settings.FERNET_SECRET_KEY)
            validated_data["encrypted_password"] = fernet.encrypt(
                password.encode("utf-8")
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 更新记录时修改密码
        password = validated_data.pop("encrypted_password", None)
        if password:
            fernet = Fernet(settings.FERNET_SECRET_KEY)
            instance.encrypted_password = fernet.encrypt(password.encode("utf-8"))
        return super().update(instance, validated_data)


class HostDailyStatSerializer(serializers.ModelSerializer):
    """序列化主机统计模型"""

    class Meta:
        model = HostDailyStat
        fields = '__all__'
