from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import escape
from bushiba_app import function
from bushiba_app import models
from bushiba_app import user_Model_Form
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO  # 生成验证码图片
import os, json


# Create your views here.

# --------------------------------------------------------------------------------------
# 用户验证码
def image_code(request):
    img, captcha = function.Captcha()  # 生成图片和验证码
    stream = BytesIO()  # 创建内存对象
    img.save(stream, 'png')  # 保存到内存
    request.session['code'] = captcha
    request.session.set_expiry(60 * 60 * 24 * 7)
    return HttpResponse(stream.getvalue())  # 显示图片


# 用户登录
def login(request):
    if request.method == 'GET':
        form = user_Model_Form.UserLoginForm()
        return render(request, 'user/login.html', {'form': form})
    # POST
    form = user_Model_Form.UserLoginForm(data=request.POST)
    admin_pwd = request.POST.get('password')  # 单独验证管理员
    if form.is_valid():
        user_input_code = form.cleaned_data.pop('code')
        name = form.cleaned_data.get('name')
        pwd = form.cleaned_data.get('password')

        if name == 'admin_bushiba' and admin_pwd == 'sjksaf54ss13c3a' and user_input_code == request.session['code']:
            request.session['info'] = {'id': 0, 'user': name, 'pwd': admin_pwd}
            return redirect('/admin/welcome/')

        user_object = models.Users.objects.filter(name=name).first()
        if not user_object:  # 查询用户是否存在
            form.add_error('password', '用户名或密码错误')
            return render(request, 'user/login.html', {'form': form})
        else:  # 密码校验
            if pwd != user_object.password:
                form.add_error('password', '用户名或密码错误')
                return render(request, 'user/login.html', {'form': form})
            else:  # 验证码校验
                if user_input_code != request.session['code']:
                    form.add_error('code', '验证码错误')
                    return render(request, 'user/login.html', {'form': form})
                else:
                    scl_id = models.School.objects.filter(school=user_object.school).first().id
                    request.session['info'] = {'id': user_object.id,
                                               'user': name,
                                               'scl_id': scl_id,
                                               'avatar': str(user_object.avatar)
                                               }
                    return redirect('/user/welcome/')

    else:
        return render(request, 'user/login.html', {'form': form})


# 游客登入
def visitor(request):
    request.session['info'] = {'id': 0,
                               'user': '游客',
                               'scl_id': 0,
                               'avatar': '/user_avatar/0.png'
                               }
    return redirect('/user/welcome/')


# 用户注册
def enroll(request):
    if request.method == "GET":
        form = user_Model_Form.UserEnrollForm()
        return render(request, 'user/enroll.html', {'form': form})

    # POST
    scl = request.POST.get('school')  # 获取用户输入的学校
    name = request.POST.get('name')
    sex = request.POST.get('sex')
    form_data = request.POST.copy()
    school_obj, created = models.School.objects.get_or_create(school=scl)  # 获取或创建学校对象
    form_data['school'] = school_obj.id
    form = user_Model_Form.UserEnrollForm(data=form_data)  # 获取数据
    # 校验数据
    if form.is_valid():  # 如果不为空
        form.save()  # 保存数据
        if sex == '0':
            path = f'user_avatar/0.png'  # 默认女头
        elif sex == '1':
            path = f'user_avatar/1.png'  # 默认男头
        models.Users.objects.filter(name=name).update(avatar=path)
        enroll_bool = True
        return render(request, 'user/enroll.html', {'form': form, 'enroll_bool': enroll_bool})
    else:  # 如果为空
        form_data['school'] = school_obj.school
        return render(request, 'user/enroll.html', {"form": form})


# 退出登录
def logout(request):
    request.session.clear()  # 清除cookie
    return redirect('/user/login/')


# 首页
def welcome(request):
    return render(request, 'user/welcome.html')


# --------------------------------------------------------------------------------------
# 自己的主页(动态)
def myself(request):
    nid = request.session['info']['id']
    if nid == 0:
        return redirect('/user/welcome/')
    myself = models.Users.objects.filter(id=nid).first()
    activity = models.Activity.objects.filter(user=nid).order_by('-time')
    if myself:
        return render(request, 'user/myself/myself.html', {'myself': myself, 'activity': activity})


# 自己的主页(作品)
def myself_production(request):
    nid = request.session['info']['id']
    myself = models.Users.objects.filter(id=nid).first()
    production = models.Production.objects.filter(user=nid).order_by('-time')

    # 获取附加数据
    extras = []
    liker_id = request.session['info']['id']
    for d in production:
        extra = production_extra(liker_id, d.id)
        extras.append(extra)

    data = zip(production, extras)
    if myself:
        return render(request, 'user/myself/myself_production.html', {'myself': myself, 'data': data})


# 编辑个人信息
def edit(request):
    nid = request.session['info']['id']
    old_object = models.Users.objects.filter(id=nid).first()  # 获取数据
    if request.method == "GET":
        if old_object and old_object.school:
            old_object.school_id = str(old_object.school)
        # modelform 会自动填写数据
        form = user_Model_Form.UserEditForm(instance=old_object)  # 填入数据
        return render(request, "user/myself/edit.html", {"form": form})
    # POST
    scl = request.POST.get('school')  # 获取用户输入的学校
    form_data = request.POST.copy()
    school_obj, created = models.School.objects.get_or_create(school=scl)  # 获取或创建学校对象
    form_data['school'] = school_obj.id
    form = user_Model_Form.UserEditForm(data=form_data, instance=old_object)  # 获取数据
    # 校验数据
    if form.is_valid():  # 如果不为空
        form.save()  # 保存数据
        new_name = request.POST.get('name')
        request.session['info']['user'] = new_name
        edit_bool = True
        return render(request, 'user/myself/edit.html', {'form': form, 'edit_bool': edit_bool})
    else:  # 如果为空
        form_data['school'] = school_obj.school
        return render(request, 'user/myself/edit.html', {"form": form})


# 编辑头像
@csrf_exempt
def edit_avatar(request):
    if request.method == 'GET':
        return render(request, "user/myself/avatar.html")
    # POST
    data = {'status': False}  # status：表示用户提交的数据是否规范
    uploaded_file = request.FILES['cropped_image']
    if uploaded_file:
        # 5. 生成唯一文件名
        ext = os.path.splitext(uploaded_file.name)[1]
        new_filename = f"{request.session['info']['id']}_avatar{ext}"

        # 删除旧文件（如果存在）
        save_path = os.path.join('user_avatar', new_filename)
        if default_storage.exists(save_path):
            default_storage.delete(save_path)

        # 6. 保存到指定目录（示例保存到media/avatars/）
        save_path = os.path.join('user_avatar', new_filename)
        file_path = default_storage.save(save_path, uploaded_file)

        # 保存到数据库
        path = f"user_avatar/{new_filename}"
        models.Users.objects.filter(id=request.session['info']['id']).update(avatar=path)

        # 更新头像
        request.session['info']['avatar'] = path
        data['status'] = True
        return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps(data))


# --------------------------------------------------------------------------------------
# 任务列表
def task_list(request):
    keyword = request.GET.get('keyword', '').strip()  # 获取搜索内容
    status = request.GET.get('status', '')
    keyword = escape(keyword)[:50]  # 转义HTML字符并限制长度（防XSS）

    # 构建查询条件
    query_params = {}
    if keyword:
        query_params['Q_filter'] = Q(title__icontains=keyword) | Q(demand__icontains=keyword)
    if status.isdigit() and int(status) in [0, 1, 2]:
        query_params['state'] = int(status)

    # 组合查询
    queryset = models.Task.objects.all().order_by('-time')
    if 'Q_filter' in query_params:
        queryset = queryset.filter(query_params['Q_filter'])
    if 'state' in query_params:
        queryset = queryset.filter(state=query_params['state'])

    return render(request, 'user/task/task_list.html', {'data': queryset, 'search_keyword': keyword, 'status': status})


# 查看任务
def task_see(request, nid):
    # 获取任务对象
    task = models.Task.objects.filter(id=nid).first()
    if task:
        return render(request, 'user/task/task_see.html', {'task': task})
    else:
        return redirect('/user/task/')


# 添加任务
def task_add(request):
    default_user = request.session['info']['id']
    if request.method == 'GET':
        form = user_Model_Form.TaskAddForm()
        return render(request, 'user/task/task_add.html', {'form': form})
    # POST
    form = user_Model_Form.TaskAddForm(request.POST, request.FILES)
    add_bool = False
    if form.is_valid():
        task = form.save(commit=False)  # 创建数据对象但不保存
        # 手动设置用户ID
        task.user_id = default_user
        task.save()
        add_bool = True
        return render(request, 'user/task/task_add.html', {'form': form, 'add_bool': add_bool})
    return render(request, 'user/task/task_add.html', {'form': form})


# 查看自己的任务
def task_myself(request):
    my_id = request.session['info']['id']
    if my_id == 0:
        return redirect('/user/welcome/')
    my_obj = models.Users.objects.get(id=my_id)
    data = models.Task.objects.filter(user=my_obj)
    return render(request, 'user/task/task_myself.html', {'data': data})


# 删除任务
def task_del(request, nid):
    task = models.Task.objects.filter(id=nid).first()
    if task.user.id == request.session['info']['id']:
        function.task_image_del(models.Task, nid)  # 删除关联图片
        task.delete()
    return redirect('/user/myself/task/')


# 编辑任务
def task_edit(request, nid):
    old_object = models.Task.objects.filter(id=nid).first()
    my_id = request.session['info']['id']
    if old_object.user.id != my_id:
        return render('/user/task/')

    if request.method == "GET":
        # modelform 会自动填写数据
        form = user_Model_Form.TaskEditFrom(instance=old_object)  # 填入数据
        return render(request, "user/task/task_edit.html", {"form": form})
    # POST
    form = user_Model_Form.TaskEditFrom(request.POST, request.FILES, instance=old_object)  # 获取数据
    # 校验数据
    if form.is_valid():  # 如果不为空
        form.save()  # 保存数据
        edit_bool = True
        return render(request, 'user/task/task_edit.html', {'form': form, 'edit_bool': edit_bool})
    else:  # 如果为空
        return render(request, 'user/task/task_edit.html', {"form": form})



# --------------------------------------------------------------------------------------
# 好友状态
def friend_state(myself, friend):
    state = ''
    obj = models.Friend.objects.filter(from_user=myself, to_user=friend).first()
    if obj:
        if obj.state:
            state = '已添加'
        else:
            state = '等待回应'
    else:
        state = '添加好友'
    return state

# 交友列表
def friend_list(request):
    current_user_id = request.session['info']['id']  # 获取当前用户ID
    if current_user_id == 0:
        visitor = True
    else:
        visitor = False
    scl_id = request.session['info']['scl_id']

    # 获取查询参数并预处理
    keyword = request.GET.get('keyword', '').strip()
    sex = request.GET.get('sex', '')
    school = request.GET.get('school', '')
    if visitor:
        queryset = models.Users.objects.all()  # 排除当前用户
    else:
        queryset = models.Users.objects.exclude(id=current_user_id)  # 排除当前用户
    conditions = Q()  # 构建组合查询条件
    # 关键词搜索逻辑
    if keyword:
        name_condition = Q(name__icontains=keyword)  # 用户名模糊匹配（OR 连接）
        id_condition = Q()  # ID精确匹配（仅当keyword为数字时）
        if keyword.isdigit():
            id_condition = Q(id=int(keyword))
        conditions &= (name_condition | id_condition)  # 组合关键词条件
    # 性别筛选逻辑
    if sex.isdigit() and int(sex) in [0, 1]:
        conditions &= Q(sex=sex)
    # 筛选同校
    if school.isdigit():
        conditions &= Q(school=school)
    # 应用查询条件
    queryset = queryset.filter(conditions)

    # 筛选同校
    scl_bool = False
    try:
        school = int(school)
        if school == int(scl_id):
            scl_bool = True
    except Exception as e:
        pass

    states = []     # 好友状态列表
    if not visitor:
        myself = models.Users.objects.get(id=current_user_id)
        for data in queryset:
            friend = models.Users.objects.get(id=data.id)
            state = friend_state(myself, friend)
            states.append(state)
    else:
        states = ['添加好友'] * len(queryset)

    queryset = zip(queryset, states)
    return render(request, 'user/friend/friend_list.html', {'data': queryset, 'sex': sex, 'scl_bool': scl_bool})


# 查看TA的动态
def friend_see(request, nid):
    # 获取id
    friend = models.Users.objects.filter(id=nid).first()
    # 页码
    page = int(request.GET.get('page', 1))
    items_per_page = 5  # 每次请求5条数据
    start = (page - 1) * items_per_page
    end = start + items_per_page

    activity = models.Activity.objects.filter(user=nid).order_by('-time')
    data = activity[start:end]

    has_next = len(activity[end:end + 1]) > 0  # 判断还有没有数据
    # 如果是 AJAX 请求，返回 JSON 数据
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data_list = [
            {
                'id': activity.id,
                'text': activity.text,
                'time': activity.time.strftime('%Y年%m月%d日 %H:%M'),
                'user': {'name': activity.user.name, 'avatar': str(activity.user.avatar.url)},
                'image1': str(activity.image1) if activity.image1 else None,
                'image2': str(activity.image2) if activity.image2 else None,
                'image3': str(activity.image3) if activity.image3 else None
            } for activity in data
        ]
        return JsonResponse({
            'data': data_list,
            'has_next': has_next
        })
    my_id = request.session['info']['id']
    if my_id != 0:
        myself = models.Users.objects.get(id=request.session['info']['id'])
        state = friend_state(myself, friend)
    else:
        state = '添加好友'

    if friend:
        return render(request, 'user/friend/friend_see.html', {'friend': friend, 'activity': data, 'state': state})
    else:
        return redirect('/user/friend/')


# 查看TA的作品
def friend_production(request, nid):
    # 获取id
    friend = models.Users.objects.filter(id=nid).first()

    # 页码
    page = int(request.GET.get('page', 1))
    items_per_page = 5  # 每次请求5条数据
    start = (page - 1) * items_per_page
    end = start + items_per_page

    production = models.Production.objects.filter(user=nid).order_by('-time')
    data = production[start:end]

    # 获取附加数据
    extras = []
    liker_id = request.session['info']['id']
    for d in data:
        extra = production_extra(liker_id, d.id)
        extras.append(extra)

    # ajax
    has_next = len(production[end:end + 1]) > 0  # 判断还有没有数据
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 如果是 AJAX 请求，返回 JSON 数据
        data_list = [
            {
                'id': production.id,
                'title': production.title,
                'time': production.time.strftime('%Y年%m月%d日 %H:%M'),
                'description': production.description,
                'user': {'name': production.user.name, 'avatar': str(production.user.avatar.url)},
                'extra': extra
            } for production, extra in zip(data, extras)
        ]
        return JsonResponse({'data': data_list, 'has_next': has_next})

    my_id = request.session['info']['id']
    if my_id != 0:
        myself = models.Users.objects.get(id=request.session['info']['id'])
        state = friend_state(myself, friend)
    else:
        state = '添加好友'

    data = zip(data, extras)
    if friend:
        return render(request, 'user/friend/friend_production.html', {'friend': friend, 'data': data, 'state': state})
    else:
        return redirect('/user/friend/')


# 发送好友申请
def friend_add(request):
    data = {'status': False}
    my_id = request.session['info']['id']
    if my_id == 0:
        return HttpResponse(json.dumps(data))
    myself = models.Users.objects.get(id=my_id)
    nid = request.GET.get('nid')
    to_user = models.Users.objects.get(id=nid)
    # 发送好友请求
    models.Friend.objects.create(from_user=myself, to_user=to_user)
    data['status'] = True
    return HttpResponse(json.dumps(data))

# 同意添加好友
def friend_agree(request):
    data = {'status': False}
    my_id = request.session['info']['id']
    myself = models.Users.objects.get(id=my_id)
    nid = request.GET.get('nid')
    to_user = models.Users.objects.get(id=nid)
    # 同意添加好友
    obj = models.Friend.objects.filter(from_user=myself, to_user=to_user).first()
    if obj:
        models.Friend.objects.filter(id=obj.id).update(state=True)
    else:
        models.Friend.objects.create(from_user=myself, to_user=to_user, state=True)
    models.Friend.objects.filter(from_user=to_user, to_user=myself).update(state=True)
    data['status'] = True
    return HttpResponse(json.dumps(data))

# --------------------------------------------------------------------------------------
# 动态列表
def activity_list(request):
    current_user_id = request.session['info']['id']  # 获取当前用户ID
    scl_id = request.session['info']['scl_id']

    # 获取查询参数并预处理
    keyword = request.GET.get('keyword', '').strip()
    school = request.GET.get('school', '')
    # 页码
    page = int(request.GET.get('page', 1))
    items_per_page = 5  # 每次请求5条数据
    start = (page - 1) * items_per_page
    end = start + items_per_page

    conditions = Q()  # 构建组合查询条件
    # 关键词搜索逻辑
    if keyword:
        name_condition = Q(text__icontains=keyword)  # 搜索内容关键字
        conditions &= (name_condition)  # 组合关键词条件

    # 筛选同校
    if school.isdigit():
        conditions &= Q(user__school=scl_id)
    # 应用查询条件
    queryset = models.Activity.objects.filter(conditions).order_by('-time')
    data = queryset[start:end]

    scl_bool = False
    try:
        school = int(school)
        if school == int(scl_id):
            scl_bool = True
    except Exception as e:
        pass

    has_next = len(queryset[end:end + 1]) > 0  # 判断还有没有数据

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 如果是 AJAX 请求，返回 JSON 数据
        data_list = [
            {
                'id': activity.id,
                'text': activity.text,
                'time': activity.time.strftime('%Y年%m月%d日 %H:%M'),
                'user': {'name': activity.user.name, 'avatar': str(activity.user.avatar.url)},
                'image1': str(activity.image1) if activity.image1 else None,
                'image2': str(activity.image2) if activity.image2 else None,
                'image3': str(activity.image3) if activity.image3 else None
            } for activity in data
        ]
        return JsonResponse({
            'data': data_list,
            'scl_bool': scl_bool,
            'has_next': has_next
        })

    context = {
        'data': data,
        'scl_bool': scl_bool
    }

    return render(request, 'user/activity/activity_list.html', context)


# 发布动态
def activity_add(request):
    default_user = request.session['info']['id']
    if request.method == 'GET':
        form = user_Model_Form.ActivityAddForm()
        return render(request, 'user/activity/activity_add.html', {'form': form})
    # POST
    form = user_Model_Form.ActivityAddForm(request.POST, request.FILES)
    add_bool = False
    if form.is_valid():
        avtivity = form.save(commit=False)  # 创建数据对象但不保存
        # 手动设置用户ID
        avtivity.user_id = default_user
        avtivity.save()
        add_bool = True
        return render(request, 'user/activity/activity_add.html', {'form': form, 'add_bool': add_bool})
    return render(request, 'user/activity/activity_add.html', {'form': form})


# 删除动态
def activity_del(request, nid):
    activity = models.Activity.objects.filter(id=nid).first()
    if activity.user.id == request.session['info']['id']:
        function.activity_image_del(models.Activity, nid)  # 删除关联图片
        activity.delete()
    return redirect('/user/myself/')


# 获取动态点赞次数,评论数量和点赞状态
def activity_count(request, nid):
    data = {'status': False, 'isbool': False}  # status：数据正常/异常 isbool：当前用户有没有点赞
    liker_id = request.session['info']['id']
    liker = models.Users.objects.filter(id=liker_id).first()
    if models.Activity.objects.filter(id=nid).first():
        # 统计点赞数量
        like_count = models.ActivityLike.objects.filter(activity=nid).count()
        data['like_count'] = like_count

        # 统计评论数量
        comment_count = models.ActivityComment.objects.filter(activity=nid).count()
        data['comment_count'] = comment_count

        if models.ActivityLike.objects.filter(activity=nid, liker=liker).first():  # 检查当前用户有没有点过赞
            data['isbool'] = True
        data['status'] = True
    # 返回JSON响应
    return HttpResponse(json.dumps(data))


# 动态点赞动作
def activity_liker(request, nid):
    data = {'status': False}
    liker_id = request.session['info']['id']
    if liker_id == 0:
        return HttpResponse(json.dumps(data))
    activity = models.Activity.objects.filter(id=nid).first()  # 获取动态对象
    liker = models.Users.objects.filter(id=liker_id).first()
    if activity:  # 检查有没有这条动态
        like, created = models.ActivityLike.objects.get_or_create(activity=activity, liker=liker)
        if not created:  # 有记录
            like.delete()
        data['status'] = True
    return HttpResponse(json.dumps(data))


# --------------------------------------------------------------------------------------
# 查看动态+评论
def activity_see(request, nid):
    activity = models.Activity.objects.filter(id=nid).first()
    comment = models.ActivityComment.objects.filter(activity=nid).order_by('-time')

    page = int(request.GET.get('page', 1))
    items_per_page = 5  # 每次请求5条数据
    start = (page - 1) * items_per_page
    end = start + items_per_page
    data = comment[start:end]

    # ajax请求
    has_next = len(comment[end:end + 1]) > 0  # 判断还有没有数据
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 如果是 AJAX 请求，返回 JSON 数据
        data_list = [
            {
                'id': comment.id,
                'text': comment.text,
                'time': comment.time.strftime('%Y年%m月%d日 %H:%M'),
                'user': {'name': comment.user.name, 'avatar': str(comment.user.avatar.url)}
            } for comment in data
        ]
        return JsonResponse({
            'data': data_list,
            'has_next': has_next
        })

    if request.method == 'GET':
        form = user_Model_Form.ActivityCommentForm()
        if activity:
            return render(request, 'user/activity/activity_see.html',
                          {'activity': activity, 'comment': data, 'form': form})
        return redirect('user/activity/')

    # PSOT  发布评论
    if request.session['info']['id'] == 0:
        return redirect(f'/user/activity/{nid}/see/')  # 刷新
    form = user_Model_Form.ActivityCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user_id = request.session['info']['id']
        comment.activity_id = nid
        comment.save()
        return redirect(f'/user/activity/{nid}/see/')  # 刷新
    return render(request, 'user/activity/activity_see.html', {'activity': activity, 'comment': comment, 'form': form})


# 获取动态(评论)点赞次数,点赞状态
def activity_comment_count(request, nid):
    data = {'status': False, 'isbool': False}
    liker_id = request.session['info']['id']
    liker = models.Users.objects.filter(id=liker_id).first()
    if models.ActivityComment.objects.filter(id=nid).first():
        # 统计点赞数量
        like_count = models.ActivityCommentLike.objects.filter(comment=nid).count()
        data['like_count'] = like_count

        if models.ActivityCommentLike.objects.filter(comment=nid, liker=liker).first():  # 检查当前用户有没有点过赞
            data['isbool'] = True
        data['status'] = True
        # 返回JSON响应
        return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps(data))


# 动态(评论)点赞动作
def activity_comment_liker(request, nid):
    data = {'status': False}
    liker_id = request.session['info']['id']
    if liker_id == 0:
        return HttpResponse(json.dumps(data))
    comment = models.ActivityComment.objects.filter(id=nid).first()  # 获取动态评论对象
    liker = models.Users.objects.filter(id=liker_id).first()
    if comment:  # 检查有没有这条动态
        like, created = models.ActivityCommentLike.objects.get_or_create(comment=comment, liker=liker)
        if not created:  # 有记录
            like.delete()
        data['status'] = True
    return HttpResponse(json.dumps(data))


# --------------------------------------------------------------------------------------
# 获取作品点赞数量和状态，评论数量，图片
def production_extra(liker_id, nid):
    data = {'isbool': False}  # isbool：当前用户有没有点赞
    liker = models.Users.objects.filter(id=liker_id).first()
    if models.Production.objects.filter(id=nid).first():
        # 统计点赞数量
        like_count = models.ProductionLike.objects.filter(production=nid).count()
        data['like_count'] = like_count
        # 统计评论数量
        comment_count = models.ProductionComment.objects.filter(production=nid).count()
        data['comment_count'] = comment_count
        # 检查当前用户有没有点过赞
        if models.ProductionLike.objects.filter(production=nid, liker=liker).first():
            data['isbool'] = True

    images_obj = models.ProductionImage.objects.filter(production=nid)  # 获取图片列表
    images = []
    for image in images_obj:
        image_url = image.image.url
        images.append(image_url)
    data['images'] = images
    return data


# 作品列表
def production_list(request):
    current_user_id = request.session['info']['id']  # 获取当前用户ID
    scl_id = request.session['info']['scl_id']

    # 获取查询参数并预处理
    keyword = request.GET.get('keyword', '').strip()
    school = request.GET.get('school', '')
    # 页码
    page = int(request.GET.get('page', 1))
    items_per_page = 5  # 每次请求5条数据
    start = (page - 1) * items_per_page
    end = start + items_per_page

    conditions = Q()  # 构建组合查询条件
    # 关键词搜索逻辑
    if keyword:
        title_condition = Q(title__icontains=keyword)  # 标题关键字
        description_condition = Q(description__icontains=keyword)  # 描述关键字
        conditions &= (title_condition | description_condition)  # 组合关键词条件

    # 筛选同校
    if school.isdigit():
        conditions &= Q(user__school=scl_id)
    # 应用查询条件
    queryset = models.Production.objects.filter(conditions).order_by('-time')
    data = queryset[start:end]

    # 获取附加数据
    extras = []
    liker_id = request.session['info']['id']
    for d in data:
        extra = production_extra(liker_id, d.id)
        extras.append(extra)

    # 检查有没有设置同校
    scl_bool = False
    try:
        school = int(school)
        if school == int(scl_id):
            scl_bool = True
    except Exception as e:
        pass

    has_next = len(queryset[end:end + 1]) > 0  # 判断还有没有数据
    # ajax
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 如果是 AJAX 请求，返回 JSON 数据
        data_list = [
            {
                'id': production.id,
                'title': production.title,
                'time': production.time.strftime('%Y年%m月%d日 %H:%M'),
                'description': production.description,
                'user': {'name': production.user.name, 'avatar': str(production.user.avatar.url)},
                'extra': extra
            } for production, extra in zip(data, extras)
        ]
        return JsonResponse({'data': data_list, 'scl_bool': scl_bool, 'has_next': has_next})

    data = zip(data, extras)
    context = {'data': data, 'scl_bool': scl_bool}

    return render(request, 'user/production/production_list.html', context)


# 作品点赞动作
def production_liker(request, nid):
    data = {'status': False}
    liker_id = request.session['info']['id']
    if liker_id == 0:
        return HttpResponse(json.dumps(data))
    production = models.Production.objects.filter(id=nid).first()  # 获取作品对象
    liker = models.Users.objects.filter(id=liker_id).first()
    if production:  # 检查有没有这条作品
        like, created = models.ProductionLike.objects.get_or_create(production=production, liker=liker)
        if not created:  # 有记录
            like.delete()
        data['status'] = True
    return HttpResponse(json.dumps(data))


# 发布作品
def production_add(request):
    default_user = request.session['info']['id']
    if request.method == 'GET':
        form = user_Model_Form.ProductionAddForm()
        return render(request, 'user/production/production_add.html', {'form': form})
    # POST
    form = user_Model_Form.ProductionAddForm(request.POST, request.FILES)  # 获取数据
    add_bool = False
    # 校验数据
    if form.is_valid():  # 如果不为空
        production = form.save(commit=False)  # 创建数据对象但不保存
        production.user_id = default_user  # 手动设置当前用户
        production.save()
        # 处理图片上传
        images = request.FILES.getlist('images')
        if len(images) > 9:
            images = images[:9]
        for image in images:
            models.ProductionImage.objects.create(production=production, image=image)
        add_bool = True

        return render(request, 'user/production/production_add.html', {'form': form, 'add_bool': add_bool})
    else:  # 如果为空
        return render(request, "user/production/production_add.html", {"form": form})


# 删除作品
def production_del(request, nid):
    production = models.Production.objects.filter(id=nid).first()
    # 只能删除自己的作品
    if production.user.id == request.session['info']['id']:
        function.production_file_del(models.Production, nid)  # 删除文件
        function.production_image_del(models.ProductionImage, nid)  # 删除图片
        production.delete()
    return redirect('/user/myself/production/')
# --------------------------------------------------------------------------------------
# 获取作品(评论)点赞次数,点赞状态
def production_comment_extra(liker_id, nid):
    data = {'isbool': False}    # 有没有点赞
    liker = models.Users.objects.filter(id=liker_id).first()
    if models.ProductionComment.objects.filter(id=nid).first():
        # 统计点赞数量
        like_count = models.ProductionCommentLike.objects.filter(comment=nid).count()
        data['like_count'] = like_count

        if models.ProductionCommentLike.objects.filter(comment=nid, liker=liker).first():  # 检查当前用户有没有点过赞
            data['isbool'] = True
        data['status'] = True
    return data

# 查看作品
def production_see(request, nid):
    production = models.Production.objects.filter(id=nid).first()
    file_name = None
    if production.file:
        file_name = str(production.file).split('/')[-1]
    user_id = request.session['info']['id']
    extra = production_extra(user_id, nid)
    comment = models.ProductionComment.objects.filter(production=nid).order_by('-time')

    page = int(request.GET.get('page', 1))
    items_per_page = 5  # 每次请求5条数据
    start = (page - 1) * items_per_page
    end = start + items_per_page
    comments = comment[start:end]

    extra_comments = [] # 获取评论附加数据
    for d in comments:
        extra_comment = production_comment_extra(user_id, d.id)
        extra_comments.append(extra_comment)
    data = zip(comments, extra_comments)

    # ajax请求
    has_next = len(comment[end:end + 1]) > 0  # 判断还有没有数据
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 如果是 AJAX 请求，返回 JSON 数据
        data_list = [
            {
                'id': comment.id,
                'text': comment.text,
                'time': comment.time.strftime('%Y年%m月%d日 %H:%M'),
                'extra': extra,
                'user': {'name': comment.user.name, 'avatar': str(comment.user.avatar.url)}
            } for comment, extra in zip(comments, extra_comments)
        ]
        return JsonResponse({'data': data_list,'has_next': has_next})

    if request.method == 'GET':
        form = user_Model_Form.ProductionCommentForm()
        if production:
            return render(request, 'user/production/production_see.html',
                          {'production': production,'file': file_name, 'extra': extra, 'comment': data, 'form': form})
        return redirect('user/production/')

    # PSOT  发布评论
    if request.session['info']['id'] == 0:
        return redirect(f'/user/production/{nid}/see/')  # 刷新
    form = user_Model_Form.ProductionCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user_id = user_id
        comment.production_id = nid
        comment.save()
        return redirect(f'/user/production/{nid}/see/')  # 刷新
    return render(request, 'user/production/production_see.html',
                  {'production': production, 'extra': extra, 'comment': data, 'form': form})


# 作品评论点赞动作
def production_comment_liker(request, nid):
    data = {'status': False}
    liker_id = request.session['info']['id']
    if liker_id == 0:
        return HttpResponse(json.dumps(data))
    comment = models.ProductionComment.objects.filter(id=nid).first()  # 获取评论对象
    liker = models.Users.objects.filter(id=liker_id).first()
    if comment:  # 检查有没有这条评论
        like, created = models.ProductionCommentLike.objects.get_or_create(comment=comment, liker=liker)
        if not created:  # 有记录
            like.delete()
        data['status'] = True
    return HttpResponse(json.dumps(data))