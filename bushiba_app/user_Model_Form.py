from django.core.validators import RegexValidator, ValidationError
from bushiba_app.models import Users, Task, Activity, School, ActivityComment, Production, ProductionComment
from bushiba_app.function import md5_data
from django import forms

import os


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


# 用户登录表单
class UserLoginForm(BaseForm):
    code = forms.CharField(label='验证码', widget=forms.TextInput, required=True)

    class Meta:
        model = Users  # 指定员工数据库
        fields = ['name', 'password', 'code']  # 各个字段
        widgets = {  # 特殊配置
            "password": forms.TextInput(attrs={"type": "password"}),
            "code": forms.TextInput(attrs={"type": "text"})
        }

    # 密码加密
    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5_data(pwd)


# 用户注册表单
class UserEnrollForm(BaseForm):
    again_pwd = forms.CharField(label="确认密码", widget=forms.PasswordInput)  # 新添加一个输入框

    class Meta:
        model = Users  # 指定员工数据库
        fields = ['name', 'password', 'again_pwd', 'school', 'age', 'sex']  # 各个字段
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

    # 检查确认密码是否一致
    def clean_again_pwd(self):
        pwd = self.cleaned_data.get("password")  # 获取password
        again_pwd = self.cleaned_data.get("again_pwd")  # 获取again_password
        again_pwd = md5_data(again_pwd)
        if pwd != again_pwd:
            raise ValidationError("密码不一致")
        return again_pwd

    # md5加密
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        pwd = md5_data(pwd)
        return pwd


# 用户修改表单
class UserEditForm(BaseForm):
    class Meta:
        model = Users  # 指定员工数据库
        fields = ['name', 'motto', 'hobby', 'nature', 'school', 'age', 'sex']  # 各个字段
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


# 添加任务表单
class TaskAddForm(BaseForm):
    class Meta:
        model = Task
        fields = ['title', 'demand', 'demand_image', 'price']

    # 限制图片格式
    def clean_demand_image(self):
        image = self.cleaned_data["demand_image"]
        return image_verify(image)


# 修改任务表单
class TaskEditFrom(BaseForm):
    class Meta:
        model = Task
        fields = ['title', 'demand', 'demand_image', 'price', 'state']

    # 限制图片格式
    def clean_demand_image(self):
        image = self.cleaned_data["demand_image"]
        return image_verify(image)


# 添加动态表单
class ActivityAddForm(BaseForm):
    class Meta:
        model = Activity  # 指定员工数据库
        fields = ['text', 'image1', 'image2', 'image3']

    # 验证图片大小
    def clean_image1(self):
        image = self.cleaned_data["image1"]
        return image_verify(image)

    def clean_image2(self):
        image = self.cleaned_data["image2"]
        return image_verify(image)

    def clean_image3(self):
        image = self.cleaned_data["image3"]
        return image_verify(image)


# 添加动态评论表单
class ActivityCommentForm(BaseForm):
    class Meta:
        model = ActivityComment  # 指定员工数据库
        fields = ['text']


# 添加作品表单
class ProductionAddForm(BaseForm):
    class Meta:
        model = Production  # 指定员工数据库
        fields = ['title', 'description', 'file']  # 各个字段

    def clean_file(self):
        file = self.cleaned_data['file']

        # 限制文件大小为 35MB（35 * 1024 * 1024 字节）
        max_size = 35 * 1024 * 1024  # 35MB in bytes
        if file and file.size > max_size:
            raise ValidationError("文件大小不能超过35MB，请压缩后上传")

        allowed_extensions = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt', 'zip', 'rar']
        if file:
            file_ext = os.path.splitext(file.name)[-1].lower().lstrip('.')
            if file_ext not in allowed_extensions:
                raise ValidationError("请上传规范文件（不能上传图片），别搞我")
        return file


# 添加作品评论表单
class ProductionCommentForm(BaseForm):
    class Meta:
        model = ProductionComment  # 指定数据库
        fields = ['text']