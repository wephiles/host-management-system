#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

from django.shortcuts import render

# Create your views here.

import subprocess
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import City, DataCenter, Host, HostDailyStat
from .serializers import CitySerializer, DataCenterSerializer, HostSerializer, HostDailyStatSerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class DataCenterViewSet(viewsets.ModelViewSet):
    queryset = DataCenter.objects.all()
    serializer_class = DataCenterSerializer


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

    @action(detail=True, methods=['post'], url_path='ping')
    def check_ping(self, request, pk=None):
        """自定义API：探测主机是否 Ping 可达"""
        host = self.get_object()
        ip = host.ip_address

        # 跨平台Ping命令 (Linux/Mac用 -c, Windows用 -n)，这里默认服务器是Windows
        # -c 4 发送4个包，-W 2 超时2秒
        command = ['ping', '-n', '4', '-W', '2', ip]

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            is_reachable = result.returncode == 0
            status_msg = "Ping 可达" if is_reachable else "Ping 不可达"
            return Response({
                'ip': ip,
                'is_reachable': is_reachable,
                'message': status_msg
            }, status=status.HTTP_200_OK)
        except subprocess.TimeoutExpired:
            return Response({'ip': ip, 'is_reachable': False, 'message': 'Ping 超时'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HostDailyStatViewSet(viewsets.ReadOnlyModelViewSet):
    """统计接口只提供读取，不允许手动修改"""
    queryset = HostDailyStat.objects.all().order_by('-date')
    serializer_class = HostDailyStatSerializer
