import sys
import os
import pytest

# --- 必须放在最前面 ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from kgqa.KB_query import query_main

class MockSession:
    def __init__(self):
        self._store = {}
        self.modified = False

    def get(self, key, default=None):
        return self._store.get(key, default)

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value
        self.modified = True  # Django 会在赋值时自动设为 True

    def __contains__(self, key):
        return key in self._store

class TestKnowledgeBaseIntegration:
    """测试 NLU + KB 全链路"""
    
    def test_kb_hit_flow(self):
        answer = query_main.query_function("头孢氨苄胶囊有什么功效？")
        assert answer is not None
        assert "ZHZ还小" not in answer  # 有效答案不应含占位符

    def test_kb_miss_returns_none(self):
        answer = query_main.query_function("量子纠缠能治高血压吗？")
        assert answer is None or "ZHZ还小" in answer

from kgqa.core_pipeline import answer_question  # ← 纯逻辑入口


class TestLLMFallbackIntegration:
    def test_llm_fallback_triggered(self, mocker):
        mocker.patch('kgqa.KB_query.query_main.query_function', return_value="ZHZ还小...")
        mocker.patch('kgqa.KB_query.query_main.query_with_context', return_value="ZHZ还小...")
        mocker.patch('kgqa.core_pipeline.ask_medical_question', return_value="AI 回答")

        answer, source = answer_question("如何缓解焦虑？")

        assert answer == "AI 回答"
        assert source == "AI 助手（基础）"

# class TestLLMFallbackIntegration:
#     """测试 KB 失败后 LLM 兜底（需 mock API 避免真实调用）"""
    
#     def test_llm_fallback_triggered(self, mocker):
#         # Mock 知识库返回无效
#         mocker.patch('kgqa.KB_query.query_main.query_function', return_value="ZHZ还小，无法理解")
        
#         from kgqa.utils.llm import ask_medical_question
#         mocker.patch('kgqa.utils.llm.ask_medical_question', return_value="这是一个模拟的AI回答。")
        
#         from kgqa.views import search_post
#         # 模拟 request.POST
#         class MockRequest:
#             def __init__(self):
#                 self.method = 'POST'
#                 self.POST = {'q': '如何缓解焦虑？'}
#                 self.session = MockSession()

#         # 执行函数
#         search_post(MockRequest())

#         # 验证 session 被正确更新
#         assert 'chat_history' in MockRequest().session
#         history = MockRequest().session['chat_history']
#         assert len(history) == 1
#         assert history[0]['bot'] == "这是一个模拟的AI回答。"
#         assert MockRequest().session.modified is True