from django.core.validators import RegexValidator, ValidationError
from bushiba_app.models import Users, Task, Activity, ActivityLike, ActivityComment, Production
from django import forms
import os, imghdr
from bushiba_app.function import md5_data


# 图片验证
def image_verify(image):
    if image:
        if image.size > 5 * 1024 * 1024:
            raise ValidationError("文件大小不能超过5MB")
    return image


# 给每个插件都添加css样式
class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有插件
        for name, field in self.fields.items():
            # 给每个插件都添加css样式
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


# 添加用户表单
class UserForm(BaseForm):
    class Meta:
        model = Users  # 指定员工数据库
        fields = '__all__'  # 各个字段
        exclude = ['avatar']  # 排除avatar字段
        widgets = {  # 特殊配置
            "password": forms.TextInput(attrs={"type": "password"}),
            "school": forms.TextInput(attrs={"type": "text"})
        }

    # 验证用户名是否存在
    def clean_name(self):
        text_user = self.cleaned_data["name"]
        # 获取当前编辑的用户实例（编辑时存在，新建时可能为新建状态）
        current_user = self.instance
        # 检查除当前用户外，是否还有其他用户使用该用户名
        exists = Users.objects.filter(name=text_user).exclude(id=current_user.id).exists()
        if exists:
            raise ValidationError("用户名已存在")
        return text_user

    # md5加密
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        pwd = md5_data(pwd)
        return pwd


# 添加任务表单
class TaskForm(BaseForm):
    class Meta:
        model = Task  # 指定员工数据库
        fields = '__all__'  # 各个字段


    # 限制图片格式
    def clean_demand_image(self):
        image = self.cleaned_data["demand_image"]
        return image_verify(image)


# 添加动态表单
class ActivityForm(BaseForm):
    class Meta:
        model = Activity  # 指定员工数据库
        fields = '__all__'  # 各个字段

    def clean_image1(self):
        image = self.cleaned_data["image1"]  # 获取输入的号码
        return image_verify(image)

    def clean_image2(self):
        image = self.cleaned_data["image2"]  # 获取输入的号码
        return image_verify(image)

    def clean_image3(self):
        image = self.cleaned_data["image3"]  # 获取输入的号码
        return image_verify(image)


# 添加动态点赞
class ActivityLikeForm(BaseForm):
    class Meta:
        model = ActivityLike  # 指定员工数据库
        fields = '__all__'  # 各个字段


# 添加动态评论
class ActivityCommentForm(BaseForm):
    class Meta:
        model = ActivityComment  # 指定员工数据库
        fields = '__all__'  # 各个字段


# 添加作品
class ProductionForm(BaseForm):
    class Meta:
        model = Production  # 指定员工数据库
        fields = '__all__'  # 各个字段

    def clean_file(self):
        file = self.cleaned_data['file']
        allowed_extensions = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt', 'zip', 'rar']
        if file:
            file_ext = os.path.splitext(file.name)[-1].lower().lstrip('.')
            if file_ext not in allowed_extensions:
                raise ValidationError("请上传规范文件（不能上传图片），别搞我")
        return file