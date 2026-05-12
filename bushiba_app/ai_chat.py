from django.shortcuts import render, HttpResponse, redirect
import json
from langchain_openai import ChatOpenAI


API_KEY = "you_key"

# getAI聊天前端页面
def ai_chat(request):
    if request.method == 'GET':
        return render(request, 'user/ai_chat/ai_chat.html')


# ai回答
def chat_with_openai(user_message):
    """使用 OpenAI 进行对话"""
    try:
        # 初始化 OpenAI 客户端（key 先放空，后续配置）
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
            print(user_message)
            
            if not user_message:
                response = {
                    'success': False,
                    'answer': '请输入有效的问题。'
                }
                return HttpResponse(json.dumps(response), content_type='application/json')
                
            response_content = chat_with_openai(user_message)
            print(response_content)
            
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
        
