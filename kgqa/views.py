from django.shortcuts import render
import sys
from kgqa.KB_query import query_main

# Create your views here.

# def search_post(request):
#     ctx = {}
#     if request.POST:
#         question = request.POST['q']
#         ctx['rlt'] = query_main.query_function(question)
#         print(ctx['rlt'])
#     return render(request, "post.html", ctx)

def search_post(request):
    # 获取或初始化对话历史（存储在 session 中）
    chat_history = request.session.get('chat_history', [])
    
    if request.method == 'POST':
        question = request.POST.get('q', '').strip()
        if question:
            # 调用知识图谱查询
            answer = query_main.query_function(question)
            # 保存问答对到历史
            chat_history.append({
                'user': question,
                'bot': answer if answer else "抱歉，我暂时无法回答这个问题。"
            })
            # 更新 session（Django 会自动保存）
            request.session['chat_history'] = chat_history
    
    # 传递整个对话历史给模板
    return render(request, "post.html", {'history': chat_history})
