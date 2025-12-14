# kgqa/core_pipeline.py （建议新增）

from kgqa.KB_query import query_main
from kgqa.utils.llm import ask_medical_question
from typing import Optional

def is_kg_answer_valid(answer: Optional[str]) -> bool:
    if answer is None:
        return False
    return "ZHZ还小" not in answer and "无法理解" not in answer

def answer_question(question: str, chat_history=None):
    """
    纯函数：输入问题，返回 (answer: str, source: str)
    不依赖 request/session/Django
    """
    if chat_history is None:
        chat_history = []

    # Step 1: 查询知识库（可带上下文）
    kg_answer = query_main.query_with_context(question, chat_history)

    if is_kg_answer_valid(kg_answer):
        return kg_answer, "知识库（上下文增强）"

    # Step 2: KB 失败 → 调用 LLM
    try:
        # 如果有共指消解逻辑，可在此处调用
        # resolved_q = query_main.resolve_coreference(question, chat_history)
        # final_answer = ask_medical_question_with_history(resolved_q, chat_history)
        # return final_answer, "AI 助手（多轮理解）"
        pass
    except Exception:
        pass

    # 兜底：基础 LLM
    llm_answer = ask_medical_question(question)
    return llm_answer, "AI 助手（基础）"