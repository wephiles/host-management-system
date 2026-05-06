# 企业内部主机管理系统

![LICENSE: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

本项目采用MIT许可证授权——详情请参见`LICENSE`文件。

## 技术栈

- Python 3.x
- Django 5.x & Django REST Framework
- Celery & Redis
- Paramiko (SSH连接)
- Cryptography (密码加密)

## 功能实现说明

1. **模型设计**：包含 City、DataCenter、Host、HostDailyStat 四个模型。主机删除时城市机房保留。
2. **RESTful API**：提供城市、机房、主机的增删改查。
3. **Ping探测**：在 `hosts/{id}/ping/` 接口通过系统 `ping` 命令探测。
4. **密码轮转**：使用 Celery Beat 每8小时触发。通过 Paramiko SSH 登录后执行 `chpasswd` 修改。密码使用 Fernet 对称加密存入数据库 BinaryField。
5. **每日统计**：每天00:00触发，使用 Django ORM `annotate` 聚合查询，按城市和机房分组统计并写入 `HostDailyStat`。
6. **耗时中间件**：自定义 `RequestTimeMiddleware`，在响应头增加 `X-Request-Duration` 字段。

## 启动步骤

1. `pip install -r requirements.txt`
2. 确保 Redis 已启动
3. `python manage.py migrate`
4. 启动 Celery: `celery -A host_project worker -l info` 及 `celery -A host_project beat -l info`
5. 启动 Web: `python manage.py runserver`