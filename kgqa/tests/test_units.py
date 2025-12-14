# kgqa/tests/test_units.py
import sys
import os
import pytest

# --- 必须放在最前面 ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from kgqa.KB_query.word_tagging import Tagger, Word
from kgqa.KB_query.question2sparql import Question2Sparql

# 使用相对路径构建词典路径
DICT_DIR = os.path.join(PROJECT_ROOT, 'kgqa', 'KB_query', 'dict')
DICT_PATHS = [
    os.path.join(DICT_DIR, 'jibing_pos_name.txt'),
    os.path.join(DICT_DIR, 'drug_pos_name.txt')
]

class TestTagger:
    def test_load_dict_and_tag(self):
        """测试：外部词典是否被加载（通过 suggest_freq 生效）"""
        tagger = Tagger(DICT_PATHS)
        
        # 测试 "喉插管损伤" 是否被正确切分（这是你在 word_tagging.py 中 suggest_freq 的词）
        words = tagger.get_word_objects("喉插管损伤需要什么药？")
        tokens = [w.token for w in words]
        
        # 应该作为一个整体被识别，而不是 ["喉", "插管", "损伤"]
        assert "喉插管损伤".encode('utf-8') in tokens
        
        # 验证返回的是 Word 对象列表
        assert all(isinstance(w, Word) for w in words)
        assert all(hasattr(w, 'token') and hasattr(w, 'pos') for w in words)

class TestQuestionParser:
    def setup_method(self):
        self.q2s = Question2Sparql(DICT_PATHS)

    def test_get_sparql_for_symptom(self):
        """测试：生成症状查询的 SPARQL"""
        sparql = self.q2s.get_sparql("感冒有什么症状？")
        
        # 根据你的规则模板，应包含以下关键词
        assert "haszhengzhuang" in sparql
        assert "jibingname" in sparql
        assert "'感冒'" in sparql

    def test_get_sparql_for_drug(self):
        """测试：生成药品查询的 SPARQL"""
        sparql = self.q2s.get_sparql("马来酸罗格列酮片的批准文号是什么?")
        assert "proname" in sparql
        assert "pzwh" in sparql
        assert "'马来酸罗格列酮片'" in sparql

    def test_get_sparql_no_match_returns_none(self):
        """测试：无法匹配的问题返回 None"""
        sparql = self.q2s.get_sparql("今天天气怎么样？")
        assert sparql is None

# # 注意：Jena 测试保留，但建议标记为集成测试
# @pytest.mark.skip(reason="需 Fuseki 服务运行，属于集成测试")
# class TestJenaFuseki:
#     def test_sparql_query_success(self):
#         from kgqa.KB_query.jena_sparql_endpoint import JenaFuseki
#         fuseki = JenaFuseki()
#         query = """
#         PREFIX : <http://www.kgdrug.com#>
#         SELECT ?x WHERE { ?s :jibingname '感冒'. ?s :haszhengzhuang ?m. ?m :zzname ?x }
#         """
#         results = fuseki.get_sparql_result(query)
#         bindings = fuseki.parse_result(results)
#         assert len(bindings) > 0