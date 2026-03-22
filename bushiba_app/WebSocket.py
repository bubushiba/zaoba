from django.shortcuts import render, HttpResponse, redirect
from bushiba_app import function
from bushiba_app import models
from bushiba_app import user_Model_Form
from django.utils import timezone
import json


# 聊天界面
def chat(request):
    user_id = request.session['info']['id']
    if user_id == 0:
        return redirect('/user/welcome/')
    myself = models.Users.objects.get(id=user_id)

    # 获取好友列表（直接获取User对象）
    user_list_id = models.Friend.objects.filter(from_user=myself,state=True).select_related('to_user').all()
    user_list = [friend.to_user for friend in user_list_id]     # 直接访问关联的User对象

    # 获取好友申请列表
    request_list_id = models.Friend.objects.filter(to_user=myself,state=False).select_related('from_user').all()
    request_list = [request.from_user for request in request_list_id]   # 直接访问关联的User对象

    # 未读消息
    msgs_count_list = []
    for user in user_list:
        msgs = models.Message.objects.filter(from_user=user, to_user=myself, state=False).count()
        msgs_count_list.append(msgs)

    user_list = zip(user_list, msgs_count_list)

    return render(request, 'user/websocket/chat.html', {'from_user': user_id,
                                                        'user_list': user_list,
                                                        'user_requests': request_list,
                                                        'req_count': len(request_list)
                                                        })


# ajax请求加载聊天记录
def chat_history(request):
    data = {'status': True, 'messages': []}
    from_user, to_user = request.GET.get('from_user'),  request.GET.get('to_user')
    from_user_obj, to_user_obj = models.Users.objects.get(id=from_user), models.Users.objects.get(id=to_user)
    from_user_message = models.Message.objects.filter(from_user=from_user_obj, to_user=to_user_obj)
    to_user_message = models.Message.objects.filter(from_user=to_user_obj, to_user=from_user_obj)
    # 更新消息已读
    models.Message.objects.filter(from_user=to_user_obj, to_user=from_user_obj).update(state=True)

    combined_messages = (from_user_message | to_user_message).order_by('time')
    # 序列化消息对象
    for msg in combined_messages:
        local_time = timezone.localtime(msg.time)
        data['messages'].append({
            'from_user': msg.from_user.id,
            'to_user': msg.to_user.id,
            'text': msg.text,
            'time': local_time.strftime('%Y年%m月%d日 %H:%M')
        })
    return HttpResponse(json.dumps(data))

