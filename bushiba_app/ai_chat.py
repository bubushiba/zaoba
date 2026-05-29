from django.shortcuts import render, HttpResponse, redirect
import json
import os
from langchain_openai import ChatOpenAI


# 从环境变量读取API Key
API_KEY = os.environ.get('OPENAI_API_KEY', '')
# getAI聊天前端页面
def ai_chat(request):
    if request.method == 'GET':
        return render(request, 'user/ai_chat/ai_chat.html')


# ai回答
def chat_with_openai(user_message):
    """使用 OpenAI 进行对话"""
    try:
        # 检查API Key是否配置
        if not API_KEY:
            return 'Error: API Key未配置，请在Render环境变量中设置OPENAI_API_KEY'
            
        # 初始化 OpenAI 客户端
        llm = ChatOpenAI(
            api_key=API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-turbo"
        )
        
        # 直接调用，不添加额外处理
        response = llm.invoke(user_message)
        return response.content
        
    except Exception as e:
        # 如果 OpenAI 不可用，返回原始错误
        return f'Error: {str(e)}'


# post 返回ai回答
def ai_chat_api(request):
    if request.method == 'POST':
        try:
            user_message = request.POST.get('message', '').strip()
            
            if not user_message:
                response = {
                    'success': False,
                    'answer': '请输入有效的问题。'
                }
                return HttpResponse(json.dumps(response), content_type='application/json')
                
            response_content = chat_with_openai(user_message)
            
            # 检查是否是错误信息
            if response_content.startswith('Error:'):
                response = {
                    'success': False,
                    'answer': response_content
                }
            else:
                response = {
                    'success': True,
                    'answer': response_content
                }
            
            return HttpResponse(json.dumps(response), content_type='application/json')
            
        except Exception as e:
            response = {
                'success': False,
                'answer': f'服务器错误：{str(e)}'
            }
            return HttpResponse(json.dumps(response), content_type='application/json')
        
