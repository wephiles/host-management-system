#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""路由配置"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cities', views.CityViewSet)
router.register(r'datacenters', views.DataCenterViewSet)
router.register(r'hosts', views.HostViewSet, basename='host')
router.register(r'stats', views.HostDailyStatViewSet, basename='stat')
router.register(r'counts', views.HostDailyStatViewSet, basename='stat')

urlpatterns = [
    path('', include(router.urls)),
]



# --END--
