# encoding=utf-8

"""
@desc:main函数，整合整个处理流程。
"""
import sys
import os
# 从 query_main.py 所在目录向上跳两级，到达项目根目录
sys.path.append(os.path.abspath("E:/QA_System/KGQA-Based-On-medicine-master"))  # 注意是三级跳转

from KGQA_Based_On_medicine.settings import fuseki,q2s

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

def extract_last_mentioned_entity(history, entity_type="disease"):
    """从对话历史中提取最近提到的疾病或药品"""
    if entity_type == "disease":
        target_set = _DISEASE_SET
    elif entity_type == "drug":
        target_set = _DRUG_SET
    elif entity_type == "symptom":
        target_set = _SYMPTOM_SET
    else:
        # 防御性编程：防止传入非法类型（如 None, "med", 拼写错误等）
        raise ValueError(f"Unsupported entity_type: {entity_type}")
    for turn in reversed(history):
        user_text = turn.get('user', '')
        # 精确匹配（避免部分匹配如“胃”匹配“胃炎”）
        for entity in target_set:
            if entity in user_text:
                return entity
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
    vague_words = ["它", "这个", "那个", "上述", "刚才", "怎么治", "怎么办", "有啥", "如何预防", "怎么预防", "能吃", "可以吃"]
    return any(w in question for w in vague_words) and not contains_medical_entity(question)

def _run_kb_query(question: str):
    """封装 KB 查询，统一异常处理"""
    return query_function(question)

def query_with_context(question: str, history: list):
    """
    支持多轮上下文的知识库查询主函数
    返回：有效答案字符串 或 None（表示 KB 无法回答）
    """
    # Step 1: 尝试原始问题
    answer = _run_kb_query(question)
    if answer is not None and 'ZHZ还小' not in answer:
        return answer

    # Step 2: 若问题含代词且无明确实体，尝试重写
    if is_pronoun_or_vague_question(question):
        last_disease = extract_last_mentioned_entity(history, "disease")
        if last_disease:
            rewritten = question
            for pronoun in ["它", "这个", "那个"]:
                rewritten = rewritten.replace(pronoun, last_disease)
            answer = _run_kb_query(rewritten)
            if answer is not None and 'ZHZ还小' not in answer:
                return answer

        last_drug = extract_last_mentioned_entity(history, "drug")
        if last_drug:
            rewritten = question
            for pronoun in ["它", "这个", "那个"]:
                rewritten = rewritten.replace(pronoun, last_drug)
            answer = _run_kb_query(rewritten)
            if answer is not None and 'ZHZ还小' not in answer:
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

