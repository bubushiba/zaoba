from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, redirect


class Middleware_1(MiddlewareMixin):
    def process_request(self, request):
        info = request.session.get('info')  # 获取cookie
        if request.path_info in ['/admin/login/', '/admin/image/code/', '/user/login/', '/user/image/code/', '/user/enroll/', '/user/visitor/']:
            return None
        elif request.path_info == '/':
            if info:
                return redirect('/user/welcome/')
            else:
                return redirect('/user/login/')

        if not info:
            return redirect('/user/login/')

        if 'add' in request.path_info and info['id'] == 0:
            return redirect('/user/welcome/')
        else:
            if 'admin' in request.path_info and ('pwd' not in info):
                return redirect('/user/welcome/')
                if info['pwd'] != 'sjksaf54ss13c3a':
                    return redirect('/user/welcome/')



