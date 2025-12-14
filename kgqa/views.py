from django.shortcuts import render, redirect
import sys
from kgqa.KB_query import query_main
from django.http import JsonResponse
from .utils.llm import ask_medical_question, ask_medical_question_with_history

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
    if request.method == 'POST':
        question = request.POST.get('q', '').strip()
        if not question:
            return redirect('home')
        
        # 获取当前会话历史
        chat_history = request.session.get('chat_history', [])
        
        # === Step 1: 尝试带上下文的知识库查询 ===
        kg_answer = query_main.query_with_context(question, chat_history)
        
        if kg_answer is not None and is_kg_answer_valid(kg_answer):
            final_answer = kg_answer
            source = "知识库（上下文增强）"
        else:
            # === Step 2: 知识库失败 → 调用带历史的 LLM ===
            try:
                llm_q = query_main.resolve_coreference(question, chat_history)
                final_answer = ask_medical_question_with_history(llm_q, chat_history)
                source = "AI 助手（多轮理解）"
            except Exception as e:
                # 兜底：调用原始 LLM（无历史）
                final_answer = ask_medical_question(question)
                source = "AI 助手（基础）"
        
        # 更新会话历史（保留最近20轮）
        chat_history.append({
            'user': question,
            'bot': final_answer,
            'source': source
        })
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        request.session['chat_history'] = chat_history
        request.session.modified = True
        # if question:
        #     # Step 1: 查询知识图谱
        #     kg_answer = query_main.query_function(question)
            
        #     # Step 2: 判断是否有效
        #     if kg_answer is None:
        #         # ✅ 新增：Fuseki 宕机 → 强制走 LLM
        #         final_answer = ask_medical_question(question)
        #         source = "AI 助手 (知识库服务不可用)"
        #     elif is_kg_answer_valid(kg_answer):
        #         final_answer = kg_answer
        #         source = "知识库"
        #     else:
        #         # Step 3: 知识库无结果 → 调用大模型
        #         final_answer = ask_medical_question(question)
        #         source = "AI 助手"

        #     # 保存到历史（限制最多 20 条，避免 session 过大）
        #     chat_history = request.session.get('chat_history', [])
        #     chat_history.append({
        #         'user': question,
        #         'bot': final_answer,
        #         'source': source
        #     })
        #     if len(chat_history) > 20:
        #         chat_history = chat_history[-20:]  # 只保留最近 20 条
        #     request.session['chat_history'] = chat_history

        # ✅ 关键：POST 后重定向，防止刷新重复提交
        return redirect('home')

    else:  # GET 请求
        chat_history = request.session.get('chat_history', [])
        return render(request, "post.html", {'history': chat_history})

def clear_history(request):
    """
    清空 session 中的聊天历史
    """
    if 'chat_history' in request.session:
        del request.session['chat_history']
    return redirect('home')  # 重定向回问答页面
