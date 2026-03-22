from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
import json


class ChatConsumer(WebsocketConsumer):
    # 接收客户端连接时，触发
    def websocket_connect(self, message):
        self.accept()   # 允许连接
        print(message, "连接了")

        # 获取群号
        from_user = self.scope['url_route']['kwargs'].get('from')
        to_user = self.scope['url_route']['kwargs'].get('to')
        print(from_user, to_user)
        # 将这个客户端的连接加入内存，房间号为 from_user
        async_to_sync(self.channel_layer.group_add)(from_user, self.channel_name)

    # 接收websocket请求时，触发
    def websocket_receive(self, message):
        from bushiba_app import models
        # 获取群号
        to_user = self.scope['url_route']['kwargs'].get('to')
        from_user = self.scope['url_route']['kwargs'].get('from')
        # 通知房间号为 to_user 的所有客户端，执行sending的方法
        async_to_sync(self.channel_layer.group_send)(to_user, {'type': 'sending', 'from_user': from_user, 'to_user': to_user, 'message': message})
        # 保存聊天记录
        from_uer_obj, to_user_obj = models.Users.objects.get(id=from_user), models.Users.objects.get(id=to_user)
        models.Message.objects.create(from_user=from_uer_obj, text=message['text'], to_user=to_user_obj)

    def sending(self, event):
        from_user = event.get('from_user')
        text = event['message']['text']
        data = {'from_user': from_user, 'text': text}
        self.send(json.dumps(data))

    # 客户端要断开连接时，触发
    def websocket_disconnect(self, message):
        # 获取群号
        from_user = self.scope['url_route']['kwargs'].get('from')
        # 移除客户端
        async_to_sync(self.channel_layer.group_discard)(from_user, self.channel_name)
        print(message, "断开连接了")
        raise StopConsumer()    # 断开连接
