# kgqa/utils/llm.py

import dashscope
from dashscope import Generation

# 设置你的 API Key（请替换为实际值）
DASHSCOPE_API_KEY = "sk-26e1273050cc4b3aa8ea1443cc139e9f"  # 从阿里云控制台获取

def ask_medical_question(user_query: str) -> str:
    """
    调用通义千问 API 回答医药相关问题
    """
    try:
        # 设置 API Key
        dashscope.api_key = DASHSCOPE_API_KEY

        prompt = f"""
        你是一位专业药师，请用简洁、准确的中文回答以下问题。
        如果不确定，请说“建议咨询医生或药师”，不要编造信息。
        如果问题与医药无关，请说：“我无法提供相关信息，我只能回答与医药相关的问题。”。
        如：提问“今天天气怎么样？”，请说，“我无法提供天气信息，我只能回答与医药相关的问题。”。

        问题：{user_query}
        """

        response = Generation.call(
            model="qwen-turbo",  # 使用便宜且快的模型
            prompt=prompt,
            temperature=0.3,     # 控制随机性
            max_tokens=500,       # 限制输出长度
            timeout=20  # ← 新增：10秒超时
        )

        if response.status_code == 200:
            return response.output.text.strip()
        else:
            return "抱歉，当前无法回答该问题。"

    except Exception as e:
        print(f"调用大模型失败：{e}")
        return "网络异常，请稍后再试。"

def ask_medical_question_with_history(current_query: str, history: list) -> str:
    """
    带对话历史的 LLM 调用，支持多轮上下文理解。
    :param current_query: 当前用户问题
    :param history: [{'user': str, 'bot': str}, ...] 最近若干轮对话
    :return: 回答字符串
    """
    try:
        dashscope.api_key = DASHSCOPE_API_KEY
        
        # 构建对话历史文本（只取最近2轮，避免超长）
        context_lines = []
        for turn in history[-2:]:
            context_lines.append(f"用户：{turn['user']}")
            context_lines.append(f"助手：{turn['bot']}")
        context_text = "\n".join(context_lines)
        
        prompt = f"""你是一位专业药师，请结合以下对话历史回答当前问题。
要求：
1. 若当前问题含指代（如“那”、“它”、“这个病”），请根据历史推断具体对象；
2. 若历史无关，则仅回答当前问题；
3. 回答简洁、准确，不编造信息。

对话历史：
{context_text}
当前问题：{current_query}
回答："""
        
        response = Generation.call(
            model="qwen-turbo",
            prompt=prompt,
            temperature=0.3,
            max_tokens=500,
            timeout=10
        )
        
        if response.status_code == 200:
            answer = response.output.text.strip()
            return answer if answer else "抱歉，模型返回了空答案。"
        else:
            return "抱歉，当前无法获取AI回答，请稍后再试。"

    except Exception as e:
        print(f"调用大模型（带历史）失败：{e}")
        return "网络或服务异常，AI助手暂时不可用。"