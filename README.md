# Host Management System (主机管理系统)

![LICENSE: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

本项目采用MIT许可证授权——详情请参见`LICENSE`文件。

## 🛠️ 技术栈

- **Web 框架**: Django 6.0
- **API 接口**: Django REST Framework (DRF)
- **异步任务队列**: Celery + Redis
- **定时任务**: django-celery-beat
- **加密库**: cryptography (Fernet 对称加密)
- **SSH 连接**: paramiko
- **数据库**: SQLite3 (开发环境，可轻易切换为 MySQL/PostgreSQL)

## ✨ 核心功能

1. **资产模型管理**: 完善的城市、机房、主机三级模型结构设计。
2. **RESTful API**: 提供城市、机房、主机的标准增删改查接口。
3. **主机连通性探测**: 独立的 API 接口探测主机 Ping 状态，跨平台兼容。
4. **自动化密码轮换**: 依托 Celery，每 8 小时自动生成强随机密码，通过 SSH 修改并使用 Fernet 加密入库。
5. **数据统计报表**: 每天 00:00 自动按“城市+机房”维度聚合统计主机数量，保证幂等性。
6. **性能监控中间件**: 自定义中间件，在响应头 (`X-Request-Time`) 中注入每个请求的耗时。
7. **Mock 测试模式**: 开启 `MOCK_SSH` 后，可在无真实主机环境下完整跑通密码加密轮改逻辑。

## 📁 项目结构

```text
/host_management_system
    ├── manage.py
    ├── middleware.py           # 全局请求耗时统计中间件
    ├── host_manage/
    │   ├── urls.py             # 主路由配置
    │   ├── celery.py           # Celery 实例初始化
    │   ├── settings.py         # 基础 Django 配置
    │   └── configs/            # 自定义配置
    │       ├── local.py        # 本地开发配置（含 Celery、加密密钥、Mock开关等）
    │		└── prod.py         # 生产环境配置文件 -- 正式上线就要用此配置文件
    └── hosts/
        ├── admin.py            # 后台管理配置（密码字段脱敏只读）
        ├── models.py           # 数据模型设计
        ├── serializers.py      # DRF 序列化器（密码字段 write_only 保护）
        ├── tasks.py            # Celery 异步与定时任务
        ├── urls.py             # API 路由注册
        └── views.py            # 视图集（含自定义 Ping Action）
```

## 🚀 快速开始

### 1. 环境准备

- Python 3.8+
- 运行中的 Redis 服务 (默认 `127.0.0.1:6379`)

### 2. 安装依赖

项目推荐使用虚拟环境，所需依赖如下：

```bash
pip install django djangorestframework django-celery-beat django-filter celery redis paramiko cryptography
```

也可以使用 uv 管理:

```bash
uv add django djangorestframework django-celery-beat django-filter celery redis paramiko cryptography
```

### 3. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
# (可选) 创建超级用户以访问 Django Admin 后台
python manage.py createsuperuser
```

### 4. 启动服务

> [!CAUTION]
>
> 在启动 `Django Web` 服务之前需要先启动 `Redis`.
>
> - 在 `MacOS/Linux` 下启动 `Redis` 服务 
>
>   ```bash
>   # MacOS/Linux
>   redis-server
>   ```
>
> - 在Windows下安装并启动 Redis
>   去 GitHub 下载基于 Windows 编译的 Redis：[tporadowski/redis](https://github.com/tporadowski/redis/releases)。下载 `.zip` 解压，进入文件夹，双击 `redis-server.exe` 启动（启动后保持黑框框不要关）。

需要开启三个终端分别运行以下命令：
**终端 1：启动 `Django Web` 服务**

```bash
python manage.py runserver
```

**终端 2：启动 `Celery Worker` (执行异步任务)**

```bash
# MacOS/Linux
celery -A host_manage worker -l info

# Windows
celery -A host_manage worker -l info -P solo
```

**终端 3：启动 `Celery Beat` (触发定时任务，可选)**

```bash
celery -A host_manage beat -l info
```

## ⚙️ 关键配置说明 (local_settings.py)

为了方便本地无主机环境测试，项目特别引入了 `MOCK_SSH` 开关：

```python
# 设置为 True 时，跳过真实 SSH 连接，仅模拟执行并执行加密入库逻辑
MOCK_SSH = True 
# Fernet 对称加密密钥（生产环境需要通过环境变量注入，不能写死在代码中！）
FERNET_SECRET_KEY = b'iW5rmRqMcbyhK_oImcVtMKAodb2VCTZDbqDWV_iBlbM='
```

## 📡 API 接口文档

基础路由前缀：`/api/`

| 模块     | HTTP 方法                  | 路径                    | 说明                                                         |
| :------- | :------------------------- | :---------------------- | :----------------------------------------------------------- |
| **城市** | GET / POST                 | `/api/cities/`          | 获取列表 / 创建城市                                          |
| **城市** | GET / PUT / PATCH / DELETE | `/api/cities/{id}/`     | 城市详情操作                                                 |
| **机房** | GET / POST                 | `/api/datacenters/`     | 获取列表 / 创建机房 (支持 `?city=1` 过滤)                    |
| **主机** | GET / POST                 | `/api/hosts/`           | 获取列表 / 创建主机 (创建时可通过 `encrypted_password` 传入初始密码) |
| **主机** | POST                       | `/api/hosts/{id}/ping/` | **[自定义]** 探测指定主机是否 Ping 可达                      |
| **统计** | GET                        | `/api/stats/`           | 获取每日主机统计报表 (只读)                                  |

### 接口特性说明：

1. **密码安全**：在 `Host` 接口中，`encrypted_password` 字段被设置为 `write_only`。即可以通过 POST 提交密码，但在 GET 列表中永远不会返回该字段，防止密文泄露。
2. **参数过滤**：由于配置了 `DjangoFilterBackend`，列表接口支持通过 URL Query 参数进行关联过滤（如 `/api/hosts/?city=1&datacenter=2`）。

## ⏱️ 定时任务机制

项目在 `local_settings.py` 中配置了两个核心定时任务：

1. **密码轮换 (`rotate-all-passwords`)**: 每 8 小时执行一次 (`0 */8 * * *`)。采用主任务分发子任务的设计，单台主机修改失败会自动重试（最多 2 次，间隔 60 秒），不会阻塞其他主机。
2. **生成统计 (`generate-daily-stats`)**: 每天 00:00 执行 (`0 0 * * *`)。利用 Django ORM 的 `annotate` 进行分组聚合，结合数据库的 `unique_together` 约束与 `update_or_create` 方法，确保统计数据绝对幂等，不会重复生成。







