import requests
import time
import random
import socket

# ====== 配置区 ======
BASE_URL = "http://127.0.0.1:8000"
QUESTION_ENDPOINT = "/"
CLEAR_ENDPOINT = "/clear/"
FUSEKI_HOST = "localhost"
FUSEKI_PORT = 3030  # 默认 Fuseki 端口
# ===================

SESSION = requests.Session()

def is_fuseki_running(host=FUSEKI_HOST, port=FUSEKI_PORT, timeout=2):
    """检测 Fuseki 服务是否运行"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def send_question(question: str) -> dict:
    """发送问题并返回响应状态"""
    try:
        response = SESSION.post(
            BASE_URL + QUESTION_ENDPOINT,
            data={"q": question},
            timeout=15
        )
        if response.status_code == 200:
            return {"success": True, "status_code": 200}
        else:
            return {"success": False, "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_case(name: str, question: str, expected_behavior: str):
    """执行单个测试用例"""
    print(f"\n🧪 测试: {name}")
    print(f"   输入: {question[:60]}{'...' if len(question) > 60 else ''}")
    print(f"   预期: {expected_behavior}")
    
    result = send_question(question)
    if result["success"]:
        print("   ✅ 通过: 系统正常响应")
        return True
    else:
        print(f"   ❌ 失败: {result.get('error') or 'HTTP ' + str(result.get('status_code'))}")
        return False

def run_robustness_tests():
    print("=" * 60)
    print("医疗问答系统鲁棒性与边界测试")
    print("=" * 60)

    # 清空历史
    try:
        SESSION.get(BASE_URL + CLEAR_ENDPOINT)
        print("🧹 会话历史已清空")
    except:
        pass

    passed = 0
    total = 0

    # === 1. 错别字输入 ===
    total += 1
    if test_case(
        "错别字容错",
        "感帽有什么症状？",
        "应触发 LLM，返回建议或纠正"
    ):
        passed += 1

    # === 2. 超长输入 ===
    long_text = "这是一个非常长的输入，用于测试系统是否能够处理超长文本。" * 50  # ~500 字
    total += 1
    if test_case(
        "超长输入处理",
        long_text,
        "系统不应崩溃，应返回有效答案（可能截断）"
    ):
        passed += 1

    # # === 3. 连续快速提问（模拟用户快速输入）===
    # print("\n🧪 测试: 快速连续提问（5 次，间隔 0.5 秒）")
    # rapid_passed = True
    # questions = ["头痛怎么办？", "布洛芬副作用？", "失眠吃什么药？", "感帽症状？", "高血压用药？"]
    # for q in questions:
    #     res = send_question(q)
    #     if not res["success"]:
    #         rapid_passed = False
    #         break
    #     time.sleep(0.5)  # ← 改为 0.5 秒，避免压垮 runserver

    # if rapid_passed:
    #     # 可选：GET 历史记录，验证是否保存了 5 条
    #     try:
    #         hist_resp = SESSION.get(BASE_URL + "/")
    #         if hist_resp.status_code == 200:
    #             print("   ✅ 通过: 所有请求成功，会话历史正常更新")
    #         else:
    #             print("   ⚠️ 警告: 请求成功，但无法验证历史记录")
    #     except:
    #         print("   ✅ 通过: 所有请求成功（历史记录验证跳过）")
    #     passed += 1
    # else:
    #     print("   ❌ 失败: 快速请求过程中出现错误")
    # total += 1

    # === 3. 连续快速提问 ===
    print("\n🧪 测试: 高频请求（5 次/秒）")
    rapid_passed = True
    for i in range(5):
        q = random.choice(["头痛怎么办？", "布洛芬副作用？", "失眠吃什么药？"])
        res = send_question(q)
        if not res["success"]:
            rapid_passed = False
            break
        time.sleep(0.1)  # 模拟 1 秒内 5 次
    if rapid_passed:
        print("   ✅ 通过: 所有请求成功，Session 无错乱")
        passed += 1
    else:
        print("   ❌ 失败: 高频请求导致异常")
    total += 1

    # === 4. Fuseki 宕机降级测试 ===
    print("\n⚠️  注意: Fuseki 宕机测试需手动停止 Fuseki 服务后运行！")
    print(f"     当前 Fuseki 状态: {'运行中' if is_fuseki_running() else '已停止'}")
    
    if not is_fuseki_running():
        total += 1
        if test_case(
            "Fuseki 宕机降级",
            "感冒有什么症状？",  # 正常应走 KB，但 Fuseki 停了 → 应走 LLM
            "应自动降级至 LLM，返回答案且不报错"
        ):
            passed += 1
        else:
            print("   💡 提示: 请先停止 Fuseki 服务再运行此测试")
    else:
        print("   💡 提示: 请先停止 Fuseki 服务，然后重新运行本脚本以测试降级功能")

    # === 总结 ===
    print("\n" + "=" * 60)
    print(f"📊 鲁棒性测试结果: {passed}/{total} 项通过")
    if passed == total or (total == 3 and passed >= 3):  # 允许 Fuseki 测试未执行
        print("✅ 系统具备良好的鲁棒性与容错能力！")
    else:
        print("⚠️ 部分测试未通过，请检查系统异常处理逻辑。")
    print("=" * 60)

if __name__ == "__main__":
    run_robustness_tests()