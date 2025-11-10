from django.shortcuts import render
import sys
from kgqa.KB_query import query_main
from django.http import JsonResponse
from .utils.llm import ask_medical_question

# Create your views here.

# def search_post(request):
#     ctx = {}
#     if request.POST:
#         question = request.POST['q']
#         ctx['rlt'] = query_main.query_function(question)
#         print(ctx['rlt'])
#     return render(request, "post.html", ctx)

# def search_post(request):
#     # 获取或初始化对话历史（存储在 session 中）
#     chat_history = request.session.get('chat_history', [])
    
#     if request.method == 'POST':
#         question = request.POST.get('q', '').strip()
#         if question:
#             # 调用知识图谱查询
#             answer = query_main.query_function(question)
#             # 保存问答对到历史
#             chat_history.append({
#                 'user': question,
#                 'bot': answer if answer else "抱歉，我暂时无法回答这个问题。"
#             })
#             # 更新 session（Django 会自动保存）
#             request.session['chat_history'] = chat_history
    
#     # 传递整个对话历史给模板
#     return render(request, "post.html", {'history': chat_history})


def is_kg_answer_valid(answer: str) -> bool:
    """判断知识图谱返回的答案是否有效"""
    if not isinstance(answer, str):
        return False
    # 检查是否包含“无答案”或“无法理解”的提示语
    invalid_phrases = [
        "ZHZ还小，知识库中并没有该问题的答案",
        "ZHZ还小，无法理解你的问题"
    ]
    return not any(phrase in answer for phrase in invalid_phrases)


def search_post(request):
    chat_history = request.session.get('chat_history', [])
    
    if request.method == 'POST':
        question = request.POST.get('q', '').strip()
        if question:
            # Step 1: 查询知识图谱
            kg_answer = query_main.query_function(question)
            
            # Step 2: 判断是否有效
            if is_kg_answer_valid(kg_answer):
                final_answer = kg_answer
                source = "知识库"  # 👈 新增这行
            else:
                # Step 3: 知识库无结果 → 调用大模型
                final_answer = ask_medical_question(question)
                source = "AI 助手"  # 👈 新增这行
            
            # 保存到历史
            chat_history.append({
                'user': question,
                'bot': final_answer,
                'source': source  # 👈 关键：传给模板
            })
            request.session['chat_history'] = chat_history
    
    return render(request, "post.html", {'history': chat_history})