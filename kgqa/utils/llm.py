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
            timeout=10  # ← 新增：10秒超时
        )

        if response.status_code == 200:
            return response.output.text.strip()
        else:
            return "抱歉，当前无法回答该问题。"

    except Exception as e:
        print(f"调用大模型失败：{e}")
        return "网络异常，请稍后再试。"