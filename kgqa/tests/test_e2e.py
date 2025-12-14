# # test_e2e.py
# import os
# import django
# from pathlib import Path

# # 手动设置 Django 环境
# BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 到项目根目录
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KGQA_Based_On_medicine.settings')
# django.setup()

from django.test import TestCase, Client
from django.urls import reverse

class TestEndToEndFlow(TestCase):
    def setUp(self):
        self.client = Client()

    # def test_knowledge_base_answer_flow(self):
    #     # 发送 POST 请求
    #     response = self.client.post('/', {'q': '胃炎有什么症状？'})
    #     print("\n=== POST Response ===")
    #     print("Status code:", response.status_code)
    #     if response.get('Location'):
    #         print("Redirect to:", response.get('Location'))

    #     # 如果是重定向（302），再发 GET
    #     if response.status_code == 302:
    #         response = self.client.get('/')
        
    #     print("\n=== Final Response Content (first 500 chars) ===")
    #     content = response.content.decode('utf-8')
    #     print(content[:500])
    #     print("\n=== End ===\n")

    #     # 暂时注释掉断言，先看输出
    #     # self.assertIn("[知识库]", content)

    def test_knowledge_base_answer_flow(self):
        """测试：用户提问 → KB 返回 → 页面渲染"""
        response = self.client.post('/', {'q': '胃炎有什么症状？'})
        self.assertEqual(response.status_code, 302)  # PRG 重定向
        
        # 跟随重定向获取最终页面
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        self.assertIn("上腹痛", content)  # 胃炎典型症状
        self.assertIn("知识库（上下文增强）", content)

    def test_llm_fallback_flow(self):
        """测试：用户提问 → KB 无结果 → LLM 回答"""
        response = self.client.post('/', {'q': '如何向暗恋的人表白？'})
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        self.assertIn("AI 助手（多轮理解）", content)
        self.assertNotIn("知识库（上下文增强）", content)

    def test_context_rewriting_flow(self):
        """测试多轮上下文重写"""
        # 第一轮
        self.client.post('/', {'q': '糖尿病怎么治疗？'})
        # 第二轮（代词）
        self.client.post('/', {'q': '它有什么并发症？'})
        
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        self.assertIn("视网膜病变", content)  # 糖尿病并发症
        self.assertIn("知识库（上下文增强）", content)