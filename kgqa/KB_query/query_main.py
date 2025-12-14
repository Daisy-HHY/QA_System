# encoding=utf-8

"""
@desc:main函数，整合整个处理流程。
"""
import sys
import os
import re
# 从 query_main.py 所在目录向上跳两级，到达项目根目录
sys.path.append(os.path.abspath("E:/QA_System/KGQA-Based-On-medicine-master"))  # 注意是三级跳转

from KGQA_Based_On_medicine.settings import fuseki,q2s
from kgqa.KB_query.question_drug_template import pos_disease, pos_drug, pos_symptom

# === 加载疾病和药品词典（用于实体提取）===
_DISEASE_SET = set()
_DRUG_SET = set()
_SYMPTOM_SET = set()

def _load_entity_set():
    global _DISEASE_SET, _DRUG_SET, _SYMPTOM_SET
    try:
        with open(r"E:\QA_System\KGQA-Based-On-medicine-master\kgqa\KB_query\dict\jibing_pos_name.txt", "r", encoding="utf-8") as f:
            _DISEASE_SET = set(line.strip() for line in f if line.strip())
        with open(r"E:\QA_System\KGQA-Based-On-medicine-master\kgqa\KB_query\dict\drug_pos_name.txt", "r", encoding="utf-8") as f:
            _DRUG_SET = set(line.strip() for line in f if line.strip())
        with open(r"E:\QA_System\KGQA-Based-On-medicine-master\kgqa\KB_query\dict\symptom_pos.txt", "r", encoding="utf-8") as f:
            _SYMPTOM_SET = set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"加载实体词典失败: {e}")

# 初始化词典
_load_entity_set()

def contains_medical_entity(text: str) -> bool:
    """判断文本是否包含已知疾病或药品或症状"""
    return any(entity in text for entity in _DISEASE_SET | _DRUG_SET | _SYMPTOM_SET)

def extract_entities_by_tagger(text: str):
    words = q2s.tw.get_word_objects(text)
    diseases = []
    drugs = []
    symptoms = []
    for w in words:
        if w.pos == pos_disease:
            diseases.append(w.token.decode('utf-8'))
        elif w.pos == pos_drug:
            drugs.append(w.token.decode('utf-8'))
        elif w.pos == pos_symptom:
            symptoms.append(w.token.decode('utf-8'))
    return {'diseases': diseases, 'drugs': drugs, 'symptoms': symptoms}

def get_last_entity(history, prefer_type=None):
    for turn in reversed(history):
        user_text = turn.get('user', '')
        bot_text = turn.get('bot', '')
        ents = extract_entities_by_tagger(user_text)
        bot_ents = extract_entities_by_tagger(bot_text)
        if prefer_type == 'symptom':
            if ents['symptoms']:
                return ents['symptoms'][-1], 'symptom'
            if bot_ents['symptoms']:
                return bot_ents['symptoms'][-1], 'symptom'
        if prefer_type == 'drug':
            if ents['drugs']:
                return ents['drugs'][-1], 'drug'
            if bot_ents['drugs']:
                return bot_ents['drugs'][-1], 'drug'
        if prefer_type == 'disease':
            if ents['diseases']:
                return ents['diseases'][-1], 'disease'
            if bot_ents['diseases']:
                return bot_ents['diseases'][-1], 'disease'
        if ents['diseases']:
            return ents['diseases'][-1], 'disease'
        if ents['drugs']:
            return ents['drugs'][-1], 'drug'
        if ents['symptoms']:
            return ents['symptoms'][-1], 'symptom'
    return None

def extract_last_mentioned_entity(history, entity_type="disease"):
    if entity_type == "disease":
        target_set = _DISEASE_SET
    elif entity_type == "drug":
        target_set = _DRUG_SET
    elif entity_type == "symptom":
        target_set = _SYMPTOM_SET
    else:
        raise ValueError(f"Unsupported entity_type: {entity_type}")
    for turn in reversed(history):
        user_text = turn.get('user', '')
        for entity in target_set:
            if entity in user_text:
                return entity
        if entity_type == "disease":
            patterns = [
                r"^(?P<e>[\u4e00-\u9fa5]{2,})(?:.*?)(有什么症状|有哪些症状|症状是什么|并发症|概述|怎么治|如何治疗|治疗措施|需要什么药治|应该用什么药治疗|有什么药可以治疗)",
                r"(?:怎么预防|如何预防)(?P<e>[\u4e00-\u9fa5]{2,})",
                r"(?P<e>[\u4e00-\u9fa5]{2,})(?:需要什么药治|应该用什么药治疗|有什么药可以治疗)"
            ]
        elif entity_type == "drug":
            patterns = [
                r"^(?P<e>[\u4e00-\u9fa5A-Za-z0-9]{2,})(?:的疗效是什么|有什么用|的批准文号是什么)",
                r"(?P<e>[\u4e00-\u9fa5A-Za-z0-9]{2,})(?:疗效是什么|有什么用)"
            ]
        else:
            patterns = [
                r"^(?P<e>[\u4e00-\u9fa5]{2,})(?:的概述是什么|有什么特征)"
            ]
        for p in patterns:
            m = re.search(p, user_text)
            if m:
                return m.group("e")
    return None

def query_function(question):

        question = question
        #print(question.encode('utf-8'))
        #isinstance(question.encode('utf-8'))
        my_query = q2s.get_sparql(question.encode('utf-8'))
        #print(my_query)
        if my_query is not None:
            try:
                result = fuseki.get_sparql_result(my_query)
                value = fuseki.get_sparql_result_value(result)

                # TODO 查询结果为空，根据OWA，回答“不知道”
                if len(value) == 0:
                    return 'ZHZ还小，知识库中并没有该问题的答案！！！'
                elif len(value) == 1:
                    print(len(value[0]))
                    if len(value[0]) != 1:
                        return value[0]
                    else:
                        return value[0]
                else:
                    output = ''
                    for v in value:
                        output += v + u'、'
                    return output
            # ===================
            except Exception as e:
                # Fuseki 宕机或网络错误 → 返回特殊标记
                print(f"Fuseki 查询失败: {e}")
                return None  # ← 关键：返回 None 表示“知识库不可用”
        else:
            # TODO 自然语言问题无法匹配到已有的正则模板上，回答“无法理解”
            return 'ZHZ还小，无法理解你的问题！！！'

        #print('#' * 100)

# === 新增：上下文感知查询 ===
def is_pronoun_or_vague_question(question: str) -> bool:
    vague_words = ["它", "这个", "那个", "这", "那", "该病", "该药", "该症状", "这病", "那病", "这药", "那药", "这种症状", "这种情况", "刚才", "上述", "怎么治", "怎么办", "如何预防", "怎么预防", "能吃", "可以吃"]
    return any(w in question for w in vague_words) and not contains_medical_entity(question)

def _run_kb_query(question: str):
    """封装 KB 查询，统一异常处理"""
    return query_function(question)

def resolve_coreference(question: str, history: list) -> str:
    ents = extract_entities_by_tagger(question)
    if ents['diseases'] or ents['drugs'] or ents['symptoms']:
        return question
    if not is_pronoun_or_vague_question(question):
        return question
    prefer_type = None
    if '症状' in question:
        prefer_type = 'symptom'
    elif ('药' in question) or ('治疗' in question):
        prefer_type = 'disease'
    last = get_last_entity(history, prefer_type)
    if not last:
        return question
    entity = last[0]
    if prefer_type == 'symptom' and entity in _DISEASE_SET:
        return question
    rewritten = question
    for pronoun in ["它", "这个", "那个", "这", "那", "该病", "这病", "那病", "该药", "这药", "那药", "该症状", "这种症状", "这种情况"]:
        rewritten = rewritten.replace(pronoun, entity)
    return rewritten

def query_with_context(question: str, history: list):
    """
    支持多轮上下文的知识库查询主函数
    返回：有效答案字符串 或 None（表示 KB 无法回答）
    """
    rewritten = resolve_coreference(question, history)
    answer = _run_kb_query(rewritten)
    if answer is not None and 'ZHZ还小' not in answer and '无法理解' not in answer:
        return answer

    return None  # KB 无法回答

if __name__ == '__main__':
    while True:
        question = input('请输入你的问题：')
        #print(question.encode('utf-8'))
        #isinstance(question.encode('utf-8'))
        my_query = q2s.get_sparql(question.encode('utf-8'))
        #print(my_query)
        if my_query is not None:
            result = fuseki.get_sparql_result(my_query)
            value = fuseki.get_sparql_result_value(result)

            # TODO 判断结果是否是布尔值，是布尔值则提问类型是"ASK"，回答“是”或者“不知道”。
            if isinstance(value, bool):
                if value is True:
                    print('Yes')
                else:
                    print('I don\'t know. :(')
            else:
                # TODO 查询结果为空，根据OWA，回答“不知道”
                if len(value) == 0:
                    print('I don\'t know. :(')
                elif len(value) == 1:
                    print(len(value[0]))
                    print(value[0])
                else:
                    output = ''
                    for v in value:
                        output += v + u'、'
                    print(output)

        else:
            # TODO 自然语言问题无法匹配到已有的正则模板上，回答“无法理解”
            print('I can\'t understand. :(')

        print('#' * 100)
