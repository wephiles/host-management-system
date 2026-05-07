#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 wephiles.
# This software is licensed under the MIT license.
# See the LICENSE file for details.

"""
中间件, 用来统计每个请求的耗时.
"""

import time
import logging

logger = logging.getLogger(__name__)


class RequestTimeMiddleware:
    """统计每个请求的耗时, 并写入请求头"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        # 将耗时添加到响应头中, 保留三位小数
        response['X-Request-Time'] = f'{duration:3f}s'
        return response

# --END--
