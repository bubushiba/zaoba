from django.shortcuts import render, HttpResponse, redirect
from bushiba_app import function
from bushiba_app import admin_Model_Form
from bushiba_app.models import Users, School, Task, Activity, ActivityLike, ActivityComment, Production, ProductionImage
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import json, os

# Register your models here.

# --------------------------------------------------------------------------------------
# 生成验证码图片
from io import BytesIO


# 管理员验证码
def image_code(request):
    img, captcha = function.Captcha()  # 生成图片和验证码
    stream = BytesIO()  # 创建内存对象
    img.save(stream, 'png')  # 保存到内存
    request.session['code'] = captcha
    request.session.set_expiry(60 * 60 * 24 * 1)
    return HttpResponse(stream.getvalue())  # 显示图片


# 管理员登录(假的)
def login(request):
    if request.method == 'GET':
        return render(request, 'admin/adminlogin.html')
    # POST
    return redirect('/user/login/')


# 退出登录
def logout(request):
    request.session.clear()  # 清除cookie
    return redirect('/user/login/')


# 首页
def welcome(request):
    return render(request, 'admin/welcome.html')


# --------------------------------------------------------------------------------------
# 学校管理
def school_list(request):
    data = School.objects.all()
    return render(request, "admin/school/list.html", {'data': data})


# 删除学校
def school_del(request):
    nid = request.GET.get('nid')
    School.objects.filter(id=nid).delete()
    return redirect("/admin/school/list/")


# --------------------------------------------------------------------------------------
# 用户列表
def user_list(request):
    data = Users.objects.all()
    return render(request, "admin/user/user_list.html", {'data': data})


# 添加用户
@csrf_exempt
def user_add(request):
    if request.method == "GET":
        form = admin_Model_Form.UserForm()
        return render(request, "admin/user/user_add_edit.html", {"form": form, "name": "添加", "url": "add"})
    # POST
    data = {'status': False}  # status：表示用户提交的数据是否规范
    scl = request.POST.get('school')  # 获取用户输入的学校
    form_data = request.POST.copy()
    school_obj, created = School.objects.get_or_create(school=scl)  # 获取或创建学校对象
    form_data['school'] = school_obj.id
    form = admin_Model_Form.UserForm(data=form_data)  # 使用新的表单数据重新创建表单实例
    if form.is_valid():
        form.save()  # 保存数据
        data['status'] = True
        return HttpResponse(json.dumps(data))
    # 将错误信息传到前端
    data['error'] = form.errors
    return HttpResponse(json.dumps(data))


# 编辑用户
@csrf_exempt
def user_edit(request, nid):
    if request.method == "GET":
        # 根据 id 获取数据
        old_object = Users.objects.filter(id=nid).first()  # 获取数据
        if old_object and old_object.school:
            old_object.school_id = str(old_object.school)
        # modelform 会自动填写数据
        form = admin_Model_Form.UserForm(instance=old_object)  # 填入数据
        return render(request, "admin/user/user_add_edit.html", {"form": form, "name": "编辑", "url": f"{nid}/edit"})
    # POST
    data = {'status': False}  # status：表示用户提交的数据是否规范
    # 获取数据
    old_object = Users.objects.filter(id=nid).first()
    scl = request.POST.get('school')  # 获取用户输入的学校
    form_data = request.POST.copy()
    school_obj, created = School.objects.get_or_create(school=scl)
    form_data['school'] = school_obj.id
    form = admin_Model_Form.UserForm(data=form_data, instance=old_object)
    if form.is_valid():
        form.save()
        data['status'] = True
        return HttpResponse(json.dumps(data))
    # 将错误信息传到前端
    data['error'] = form.errors
    return HttpResponse(json.dumps(data))


# 删除用户
def user_del(request):
    nid = request.GET.get('nid')

    # 删除头像
    filename = f'{nid}_avatar.png'
    save_path = os.path.join('user_avatar', filename)
    if default_storage.exists(save_path):
        default_storage.delete(save_path)

    Users.objects.filter(id=nid).delete()
    return redirect("/admin/user/list/")


# --------------------------------------------------------------------------------------
# 任务列表
def task_list(request):
    data = Task.objects.all()
    return render(request, 'admin/task/task_list.html', {"data": data})


# 添加任务
@csrf_exempt
def task_add(request):
    if request.method == "GET":
        form = admin_Model_Form.TaskForm()
        return render(request, "admin/task/task_add_edit.html", {"form": form, "name": "添加", "url": "add"})
    # POST
    data = {'status': False}  # status：表示用户提交的数据是否规范

    # 保存数据
    form = admin_Model_Form.TaskForm(request.POST, request.FILES)  # 使用新的表单数据重新创建表单实例
    if form.is_valid():
        form.save()  # 保存数据
        data['status'] = True
        return HttpResponse(json.dumps(data))
    # 将错误信息传到前端
    data['error'] = form.errors
    return HttpResponse(json.dumps(data))


# 编辑任务
@csrf_exempt
def task_edit(request, nid):
    if request.method == "GET":
        old_object = Task.objects.filter(id=nid).first()
        form = admin_Model_Form.TaskForm(instance=old_object)
        return render(request, "admin/task/task_add_edit.html", {"form": form, "name": "编辑", "url": f"{nid}/edit"})
    # POST
    data = {'status': False}  # status：表示用户提交的数据是否规范
    image = request.POST.get("demand_image")
    if image == "":  # 如果没有图片
        function.image_del(Task, nid)  # 删除旧图片
    # 提交数据
    old_object = Task.objects.filter(id=nid).first()
    form = admin_Model_Form.TaskForm(request.POST, request.FILES, instance=old_object)  # 使用新的表单数据重新创建表单实例
    if form.is_valid():
        if 'demand_image' in request.FILES:  # 如果有新图片
            function.image_del(Task, nid)  # 删除旧图片
        form.save()  # 保存数据
        data['status'] = True
        return HttpResponse(json.dumps(data))
    # 将错误信息传到前端
    data['error'] = form.errors
    return HttpResponse(json.dumps(data))


# 删除任务
def task_del(request):
    nid = request.GET.get('nid')
    function.task_image_del(Task, nid)  # 删除图片
    Task.objects.filter(id=nid).delete()
    return redirect("/admin/task/list/")


# --------------------------------------------------------------------------------------
# 动态列表
def activity_list(request):
    data = Activity.objects.all()  # 获取所有动态及其关联的图片
    return render(request, 'admin/activity/activity_list.html', {"data": data})


# 添加动态
def activity_add(request):
    if request.method == "GET":
        form = admin_Model_Form.ActivityForm()
        return render(request, "admin/activity/activity_add.html", {"form": form})

    # POST
    form = admin_Model_Form.ActivityForm(request.POST, request.FILES)  # 获取数据
    # 校验数据
    if form.is_valid():  # 如果不为空
        form.save()  # 保存数据
        return redirect("/admin/activity/list/")
    else:  # 如果为空
        return render(request, "admin/activity/activity_add.html", {"form": form})


# 删除动态
def activity_del(request):
    nid = request.GET.get('nid')
    function.activity_image_del(Activity, nid)
    Activity.objects.filter(id=nid).delete()
    return redirect("/admin/activity/list/")

# --------------------------------------------------------------------------------------
# 作品列表
def production_list(request):
    data = Production.objects.all()
    return render(request, 'admin/production/production_list.html', {'data':data})

# 添加作品
def production_add(request):
    if request.method == "GET":
        form = admin_Model_Form.ProductionForm()
        return render(request, "admin/production/production_add.html", {"form": form})

    # POST
    form = admin_Model_Form.ProductionForm(request.POST, request.FILES)  # 获取数据
    # 校验数据
    if form.is_valid():  # 如果不为空
        production = form.save()  # 保存数据
        # 处理图片上传
        images = request.FILES.getlist('images')
        for image in images:
            ProductionImage.objects.create(production=production, image=image)

        return redirect("/admin/production/list/")
    else:  # 如果为空
        return render(request, "admin/production/production_add.html", {"form": form})


# 删除作品
def production_del(request):
    nid = request.GET.get('nid')
    function.production_file_del(Production, nid)   # 删除文件
    function.production_image_del(ProductionImage, nid) # 删除图片
    Production.objects.filter(id=nid).delete()
    return redirect("/admin/production/list/")
# --------------------------------------------------------------------------------------
def test(request):
    if request.method == "GET":
        return render(request, "admin/test.html")

    # POST
    images = request.FILES.getlist('images')
    print(images)
    return redirect("/admin/production/list/")
