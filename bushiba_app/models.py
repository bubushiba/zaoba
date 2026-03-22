import os
import base64
from django.utils import timezone
from django.db import models
from django.core.validators import MaxLengthValidator
import random


# Create your models here.
# 用户表
class Users(models.Model):
    name = models.CharField(max_length=128, verbose_name="用户名")
    avatar = models.ImageField(upload_to='user_avatar/', verbose_name="头像", default='user_avatar/default.png')
    password = models.CharField(max_length=128, verbose_name="密码")
    motto = models.TextField(verbose_name="标签", max_length=100, null=True, blank=True)
    hobby = models.TextField(verbose_name="爱好", max_length=1000, null=True, blank=True)
    nature = models.TextField(verbose_name="性格", max_length=1000, null=True, blank=True)
    age = models.IntegerField(verbose_name="年龄")
    school = models.ForeignKey(to="School", verbose_name="学校", to_field="id", null=True, blank=True,
                               on_delete=models.CASCADE, db_index=True)
    level_list = ((1, "Lv1"), (2, "Lv2"), (3, "Lv3"), (4, "Lv4"), (5, "Lv5"))
    level = models.SmallIntegerField(choices=level_list, verbose_name="等级", default=1)
    sex_list = ((1, "男"), (0, "女"))
    sex = models.SmallIntegerField(choices=sex_list, verbose_name="性别")

    def __str__(self):
        return self.name


# 学校表
class School(models.Model):
    school = models.CharField(max_length=128, verbose_name="学校")

    def __str__(self):
        return self.school


# 重命名文件(任务表)
def rename_image_task(instance, filename):
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 生成新的文件名（例如：使用时间戳）
    new_filename = f"{timezone.now().strftime('%d%H%M%S%f')}.{ext}"
    # 返回完整的文件路径
    return os.path.join('task_images', timezone.now().strftime('%Y/%m'), new_filename)


# 任务表
class Task(models.Model):
    title = models.CharField(max_length=128, verbose_name="标题", default=" ")
    time = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    user = models.ForeignKey(to="Users", verbose_name="发布人", to_field="id", on_delete=models.CASCADE, db_index=True)
    demand = models.TextField(verbose_name="需求", max_length=2000)  # 限制两千字

    demand_image = models.ImageField(upload_to=rename_image_task, verbose_name="需求图片", null=True, blank=True)
    price = models.DecimalField(verbose_name="定价", max_digits=15, decimal_places=2, default=0)
    state_list = (
        (0, "未接单"),
        (1, "已接单"),
        (2, "已完成"),
    )
    state = models.SmallIntegerField(choices=state_list, verbose_name="状态", default=0)


# 重命名文件(动态表)
def rename_image_activity(instance, filename):
    num = random.randint(0, 9)
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 生成新的文件名（例如：使用时间戳）
    new_filename = f"{timezone.now().strftime('%d%H%M%S%f')}{str(num)}.{ext}"

    # 返回完整的文件路径
    return os.path.join('activity_images', timezone.now().strftime('%Y/%m'), new_filename)

# 动态表
class Activity(models.Model):
    time = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    user = models.ForeignKey(to="Users", verbose_name="发布人", to_field="id", on_delete=models.CASCADE, db_index=True)
    text = models.TextField(verbose_name="你想说什么", max_length=2000)  # 限制两千字
    image1 = models.ImageField(upload_to=rename_image_activity, verbose_name="需求图片", null=True, blank=True)
    image2 = models.ImageField(upload_to=rename_image_activity, verbose_name="需求图片", null=True, blank=True)
    image3 = models.ImageField(upload_to=rename_image_activity, verbose_name="需求图片", null=True, blank=True)


# 动态点赞表
class ActivityLike(models.Model):
    time = models.DateTimeField(verbose_name="点赞时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    activity = models.ForeignKey(to="Activity", verbose_name="动态", to_field="id", on_delete=models.CASCADE,db_index=True)
    liker  = models.ForeignKey(to="Users", verbose_name="点赞人", to_field="id", on_delete=models.CASCADE)


# 动态评论表
class ActivityComment(models.Model):
    time = models.DateTimeField(verbose_name="评论发布时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    activity = models.ForeignKey(to="Activity", verbose_name="动态", to_field="id", on_delete=models.CASCADE,db_index=True)
    user = models.ForeignKey(to="Users", verbose_name="评论人", to_field="id", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="评论内容", max_length=200)


# 动态评论点赞表
class ActivityCommentLike(models.Model):
    time = models.DateTimeField(verbose_name="点赞时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    comment = models.ForeignKey(to="ActivityComment", verbose_name="动态评论", to_field="id", on_delete=models.CASCADE,db_index=True)
    liker  = models.ForeignKey(to="Users", verbose_name="点赞人", to_field="id", on_delete=models.CASCADE)


# 重命名文件(作品表)
def rename_file_production(instance, filename):
    user_id = instance.user.id
    # 返回完整路径
    return os.path.join('production_file', timezone.now().strftime(f'{user_id}'), filename)

# 作品表
class Production(models.Model):
    user = models.ForeignKey(to="Users", verbose_name="作者", to_field="id", on_delete=models.CASCADE)
    time = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    title = models.TextField(verbose_name="标题", max_length=20)
    description = models.TextField(verbose_name="描述", max_length=1000)
    file = models.FileField(upload_to=rename_file_production, verbose_name="文件", null=True, blank=True)


# 重命名作品图片
def production_image_path(instance, filename):
    """生成作品图片存储路径：production_image/月/作品ID_序号.扩展名"""
    production = instance.production
    # 使用作品的创建时间生成目录
    date_str = production.time.strftime("%m")  # 格式化为 月

    # 获取当前作品已有图片数量作为序号
    count = ProductionImage.objects.filter(production=production).count() + 1

    # 提取文件扩展名
    ext = filename.split('.')[-1]

    # 生成文件名：作品ID_序号.扩展名
    new_filename = f"{production.id}_{count}.{ext}"

    # 完整路径：production_image/月/日/文件名
    return f"production_image/{date_str}/{new_filename}"

# 作品图片表
class ProductionImage(models.Model):
    production = models.ForeignKey(to='Production', verbose_name='作品编号', to_field='id', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=production_image_path, verbose_name="需求图片", null=True, blank=True)


# 作品点赞表
class ProductionLike(models.Model):
    time = models.DateTimeField(verbose_name="点赞时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    production = models.ForeignKey(to="Production", verbose_name="动态", to_field="id", on_delete=models.CASCADE,db_index=True)
    liker  = models.ForeignKey(to="Users", verbose_name="点赞人", to_field="id", on_delete=models.CASCADE)


# 作品评论表
class ProductionComment(models.Model):
    time = models.DateTimeField(verbose_name="评论发布时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    production = models.ForeignKey(to="Production", verbose_name="作品", to_field="id", on_delete=models.CASCADE,db_index=True)
    user = models.ForeignKey(to="Users", verbose_name="评论人", to_field="id", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="评论内容", max_length=200)


# 作品评论点赞表
class ProductionCommentLike(models.Model):
    time = models.DateTimeField(verbose_name="点赞时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    comment = models.ForeignKey(to="ProductionComment", verbose_name="作品评论", to_field="id", on_delete=models.CASCADE,db_index=True)
    liker  = models.ForeignKey(to="Users", verbose_name="点赞人", to_field="id", on_delete=models.CASCADE)


# 聊天记录
class Message(models.Model):
    from_user = models.ForeignKey(to="Users", verbose_name="发送人", to_field="id", related_name="from_messages", on_delete=models.CASCADE, db_index=True)
    time = models.DateTimeField(verbose_name="时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    text = models.TextField(verbose_name="内容", max_length=2000)
    to_user = models.ForeignKey(to='Users', verbose_name="接收人", to_field='id', related_name="to_messages", on_delete=models.CASCADE, db_index=True)
    state = models.BooleanField(verbose_name="是否已读", default=False)


# 好友表
class Friend(models.Model):
    from_user = models.ForeignKey(to="Users", verbose_name="发送人", to_field="id", related_name="from_friend",on_delete=models.CASCADE, db_index=True)
    to_user = models.ForeignKey(to='Users', verbose_name="接收人", to_field='id', related_name="to_friend", on_delete=models.CASCADE, db_index=True)
    time = models.DateTimeField(verbose_name="时间", auto_now_add=True)  # auto_now_add自动保存当前时间
    state = models.BooleanField(verbose_name="是否同意", default=False)