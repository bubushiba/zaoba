"""
URL configuration for bushiba project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from bushiba_app import admin
from bushiba_app import views
from bushiba_app import ai_chat
from bushiba_app import WebSocket
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 后台管理
    path('admin/login/', admin.login),
    path('admin/image/code/', admin.image_code),
    path('admin/welcome/', admin.welcome),
    path('admin/logout/', admin.logout),

    # 学校管理
    path('admin/school/list/', admin.school_list),
    path('admin/school/del/', admin.school_del),

    # 用户管理
    path('admin/user/list/', admin.user_list),
    path('admin/user/add/', admin.user_add),
    path('admin/user/del/', admin.user_del),
    path('admin/user/<int:nid>/edit/', admin.user_edit),

    # 任务管理
    path('admin/task/list/', admin.task_list),
    path('admin/task/add/', admin.task_add),
    path('admin/task/del/', admin.task_del),
    path('admin/task/<int:nid>/edit/', admin.task_edit),

    # 动态管理
    path('admin/activity/list/', admin.activity_list),
    path('admin/activity/add/', admin.activity_add),
    path('admin/activity/del/', admin.activity_del),

    # 作品管理
    path('admin/production/list/', admin.production_list),
    path('admin/production/add/', admin.production_add),
    path('admin/production/del/', admin.production_del),

    path('admin/test/', admin.test),

# --------------------------------------------------------------------------------------

    # 用户界面
    path('user/login/', views.login),                           # 登录
    path('user/image/code/', views.image_code),                 # 验证码
    path('user/enroll/', views.enroll),                         # 注册
    path('user/myself/', views.myself),                         # 自己的信息(动态)
    path('user/myself/production/', views.myself_production),   # 自己的信息(作品)
    path('user/edit/', views.edit),                             # 修改信息
    path('user/logout/', views.logout),                         # 退出登录
    path('user/welcome/', views.welcome),                       # 首页
    path('user/avatar/', views.edit_avatar),                    # 更换头像
    path('user/visitor/', views.visitor),                       # 游客登入

    # 任务广场
    path('user/task/', views.task_list),
    path('user/task/<int:nid>/see/', views.task_see),
    path('user/task/add/', views.task_add),
    path('user/myself/task/', views.task_myself),
    path('user/task/<int:nid>/edit/', views.task_edit),
    path('user/task/<int:nid>/del/', views.task_del),

    # 交友大厅
    path('user/friend/', views.friend_list),
    path('user/friend/add/', views.friend_add),
    path('user/friend/agree/', views.friend_agree),
    path('user/friend/<int:nid>/see/', views.friend_see),
    path('user/friend/<int:nid>/see/production/', views.friend_production),

    # 动态瞬间
    path('user/activity/', views.activity_list),
    path('user/activity/add/', views.activity_add),
    path('user/activity/<int:nid>/see/', views.activity_see),
    path('user/activity/<int:nid>/del/', views.activity_del),
    path('user/activity/<int:nid>/likes/', views.activity_count),   # 获取动态点赞次数
    path('user/activity/<int:nid>/liker/', views.activity_liker),   # 改变动态点赞状态
    path('user/activity/comment/<int:nid>/likes/', views.activity_comment_count),   # 获取动态(评论)点赞次数
    path('user/activity/comment/<int:nid>/liker/', views.activity_comment_liker),  # 改变动态(评论)点赞状态

    # 作品展
    path('user/production/', views.production_list),
    path('user/production/<int:nid>/liker/', views.production_liker),   # 改变作品点赞状态
    path('user/production/add/', views.production_add),                 # 发布作品
    path('user/production/<int:nid>/see/', views.production_see),       # 查看作品
    path('user/production/<int:nid>/del/', views.production_del),       # 删除作品
    path('user/production/comment/<int:nid>/liker/', views.production_comment_liker),  # 改变作品(评论)点赞状态
    
    # AI聊天
    path('user/ai_chat/', ai_chat.ai_chat),                           # AI聊天
    path('user/ai_chat/api/', ai_chat.ai_chat_api),                   # AI聊天API接口

    # 聊天
    path('user/chat/', WebSocket.chat),
    path('user/chat/message/', WebSocket.chat_history),     # 加载聊天记录
]

# 用于加载图片
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
