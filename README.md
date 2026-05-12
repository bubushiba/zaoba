# bushiba - 校园社交平台

基于 Django 5.0 开发的校园社交平台，提供任务发布、动态分享、作品展示和即时通讯等功能。

## 功能特性

### 🔐 用户系统
- 用户注册与登录（含验证码验证）
- 游客模式访问
- 个人信息编辑（头像、昵称、标签、爱好、性格）
- 多学校支持，用户关联学校

### 📋 任务大厅
- 任务发布与需求描述
- 需求图片上传
- 价格设置
- 任务状态流转（未接单 → 已接单 → 已完成）

### 📱 动态社区
- 图文动态发布（支持多图）
- 动态点赞与评论
- 评论点赞功能
- 用户动态流展示

### 🎨 作品中心
- 作品文件上传（文档、PPT等）
- 作品图片展示
- 作品点赞与评论

### 💬 即时通讯
- WebSocket 实时私信聊天
- 消息已读状态标记

### 👥 好友关系
- 好友申请与同意
- 好友列表管理
- 好友动态和作品浏览

### 🤖 AI 聊天助手
- 智能对话系统，支持自然语言交互
- Markdown 格式消息展示，支持代码、列表、引用等
- 基于阿里云通义千问大模型
- 实时响应，无需刷新页面
- 支持多轮对话上下文

## 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Django | 5.0.4 |
| 实时通讯 | Django Channels | - |
| 数据库 | MySQL | 5.7+ |
| 前端框架 | Bootstrap | 3.4.1 |
| 静态文件 | WhiteNoise | - |
| AI 大模型 | 通义千问 | qwen-turbo |
| AI 开发框架 | LangChain | latest |

## 环境要求

- Python 3.10+
- MySQL 5.7+
- pip 包管理工具

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd bushiba
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

创建 MySQL 数据库：

```sql
CREATE DATABASE bushiba CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 配置项目

修改 `bushiba/settings.py` 中的数据库配置（如需）：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bushiba',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}
```

### 6. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. 创建管理员账户

```bash
python manage.py createsuperuser
```

### 8. 运行项目

```bash
python manage.py runserver 0.0.0.0:8000
```

访问地址：http://localhost:8000

## 项目结构

```
bushiba/
├── bushiba/                 # 项目配置目录
│   ├── __init__.py
│   ├── asgi.py              # ASGI 配置（支持 WebSocket）
│   ├── settings.py          # 项目设置
│   ├── urls.py              # 路由配置
│   └── wsgi.py              # WSGI 配置
├── bushiba_app/             # 主应用
│   ├── __init__.py
│   ├── admin.py             # 后台管理
│   ├── admin_Model_Form.py  # 管理员表单
│   ├── apps.py              # 应用配置
│   ├── consumers.py         # WebSocket 消费者
│   ├── function.py          # 工具函数
│   ├── Middleware.py        # 自定义中间件
│   ├── models.py            # 数据库模型
│   ├── user_Model_Form.py   # 用户表单
│   ├── views.py             # 视图函数
│   ├── WebSocket.py         # WebSocket 工具
│   ├── migrations/          # 数据库迁移文件
│   ├── static/              # 静态文件
│   └── templates/           # HTML 模板
├── media/                   # 媒体文件存储
│   ├── activity_images/     # 动态图片
│   ├── production_file/     # 作品文件
│   ├── production_image/    # 作品图片
│   ├── task_images/         # 任务图片
│   └── user_avatar/         # 用户头像
├── static/                  # 静态文件（生产环境）
├── manage.py                # Django 管理命令
└── README.md               # 项目说明
```

## 数据库模型

### 核心数据表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| Users | 用户表 | id, name, avatar, password, school, level |
| School | 学校表 | id, school |
| Task | 任务表 | id, title, demand, price, state, user |
| Activity | 动态表 | id, text, image1-3, user |
| ActivityLike | 动态点赞表 | id, activity, liker |
| ActivityComment | 动态评论表 | id, activity, user, text |
| Production | 作品表 | id, title, description, file, user |
| ProductionImage | 作品图片表 | id, production, image |
| Message | 消息表 | id, from_user, to_user, text, state |
| Friend | 好友表 | id, from_user, to_user, state |

## 管理员账户

默认管理员账户：
- 用户名：`admin_bushiba`
- 密码：`sjksaf54ss13c3a`

后台管理地址：http://localhost:8000/admin/

## 开发说明

### 添加新功能

1. 在 `models.py` 中定义数据模型
2. 创建表单验证（`user_Model_Form.py` 或 `admin_Model_Form.py`）
3. 在 `views.py` 中编写视图逻辑
4. 在 `urls.py` 中配置路由
5. 创建对应的 HTML 模板

### WebSocket 开发

WebSocket 相关逻辑在 `consumers.py` 中实现，用于实时通讯功能。

## 许可证

MIT License

## 作者

- 作者：[Your Name]
- 邮箱：[Your Email]
