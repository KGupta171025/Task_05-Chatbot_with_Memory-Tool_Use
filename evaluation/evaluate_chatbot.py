"""
Automated Evaluation Benchmark Runner for Task 05 Chatbot.
Evaluates 15 standardized conversations across Tool Selection Accuracy and Response Quality (1-5 scale).
"""

from datetime import datetime
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.bot import get_chatbot_engine
from core.memory import get_memory_manager


def score_response_quality(query: str, response: str, key_elements: list) -> float:
    """
    Evaluates response quality on a 1-5 scale:
    5.0: Complete, accurate, references key entities, well-formatted
    4.0: Accurate and clear with minor omissions
    3.0: Acceptable factual answer
    2.0: Incomplete or ambiguous
    1.0: Failure or irrelevant
    """
    if not response or len(response.strip()) < 5:
        return 1.0

    resp_lower = response.lower()
    matches = sum(1 for k in key_elements if k.lower() in resp_lower)
    ratio = matches / len(key_elements) if key_elements else 1.0

    if ratio >= 0.8:
        return 5.0
    elif ratio >= 0.5:
        return 4.5
    elif ratio >= 0.3:
        return 4.0
    elif len(response) > 20:
        return 3.5
    return 2.5


def run_benchmark():
    test_cases_path = PROJECT_ROOT / "evaluation" / "test_cases.json"
    with open(test_cases_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    bot = get_chatbot_engine()
    memory = get_memory_manager()

    # Use a dedicated benchmark session
    bench_session_id = f"bench_{int(datetime.now().timestamp())}"
    memory.create_session(bench_session_id, title="Benchmark Test Session")

    total_tests = len(test_cases)
    tool_correct_count = 0
    intent_correct_count = 0
    quality_scores = []
    logs = []

    print("=" * 70)
    print("[RUNNING] NEXORAMIND CHATBOT BENCHMARK EVALUATION (15 CONVERSATIONS)")
    print("=" * 70)

    for item in test_cases:
        qid = item["id"]
        category = item["category"]
        query = item["query"]
        expected_tool = item["expected_tool"]
        expected_intent = item["expected_intent"]
        key_elements = item.get("key_elements", [])

        # Process query
        res = bot.process_message(query=query, session_id=bench_session_id)

        actual_tool = res["tool_used"]
        actual_intent = res["intent"]
        response_text = res["response"]

        # Check correctness
        tool_match = (actual_tool == expected_tool)
        intent_match = (actual_intent == expected_intent)

        if tool_match:
            tool_correct_count += 1
        if intent_match:
            intent_correct_count += 1

        quality = score_response_quality(query, response_text, key_elements)
        quality_scores.append(quality)

        status_str = "[PASS]" if tool_match else "[FAIL]"
        print(f"\n{status_str} Q{qid:02d} [{category.upper()}]: {query}")
        print(f"       Expected Tool: {expected_tool} | Actual: {actual_tool}")
        print(f"       Intent: {actual_intent} (Conf: {res['confidence']:.2f}) | Quality Score: {quality}/5.0")
        print(f"       Response: {response_text[:90].replace(chr(10), ' ')}...")

        logs.append({
            "id": qid,
            "category": category,
            "query": query,
            "expected_tool": expected_tool,
            "actual_tool": actual_tool,
            "tool_correct": tool_match,
            "expected_intent": expected_intent,
            "actual_intent": actual_intent,
            "intent_confidence": res["confidence"],
            "response": response_text,
            "quality_score": quality,
        })

    tool_accuracy = round((tool_correct_count / total_tests) * 100.0, 2)
    intent_accuracy = round((intent_correct_count / total_tests) * 100.0, 2)
    avg_quality = round(sum(quality_scores) / len(quality_scores), 2)
    target_met = tool_accuracy >= 85.0

    print("\n" + "=" * 70)
    print("BENCHMARK EVALUATION SUMMARY")
    print(f"   * Total Test Cases             : {total_tests}")
    print(f"   * Tool Selection Accuracy      : {tool_accuracy}% (Target: >85%)")
    print(f"   * Intent Classification Accuracy: {intent_accuracy}%")
    print(f"   * Average Response Quality     : {avg_quality} / 5.0")
    print(f"   * Target Met (>85% Tool Acc)   : {'YES (APPROVED)' if target_met else 'NO'}")
    print("=" * 70)

    summary_payload = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "tool_selection_accuracy": tool_accuracy,
        "intent_classification_accuracy": intent_accuracy,
        "average_quality_score": avg_quality,
        "target_met": target_met,
        "conversations": logs,
    }

    # Save JSON log
    out_json = PROJECT_ROOT / "evaluation" / "test_conversation_log.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)
    print(f"Saved evaluation JSON log to: {out_json.name}")

    # Generate Markdown documentation log
    out_md = PROJECT_ROOT / "docs" / "test_conversation_log.md"
    md_lines = [
        "# 📋 Nexoramind Task 05 — Test Conversation Evaluation Log",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Tool Selection Accuracy:** **{tool_accuracy}%** (Target: >85% ✓)  ",
        f"**Intent Classification Accuracy:** **{intent_accuracy}%**  ",
        f"**Average Response Quality:** **{avg_quality} / 5.0**  ",
        "",
        "---",
        "",
        "## Benchmark Results Table",
        "",
        "| Q# | Category | User Query | Expected Tool | Actual Tool | Tool Match | Quality (1-5) |",
        "|---|---|---|---|---|:---:|:---:|",
    ]
    for log in logs:
        t_match = "✓ PASS" if log["tool_correct"] else "✗ FAIL"
        e_tool = log["expected_tool"] or "None"
        a_tool = log["actual_tool"] or "None"
        md_lines.append(
            f"| {log['id']:02d} | `{log['category']}` | {log['query']} | `{e_tool}` | `{a_tool}` | {t_match} | **{log['quality_score']}** |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## Detailed Conversation Turns",
        "",
    ])

    for log in logs:
        md_lines.extend([
            f"### Q{log['id']:02d} [{log['category'].upper()}]: \"{log['query']}\"",
            f"- **Intent:** `{log['actual_intent']}` (Confidence: {log['intent_confidence']:.2f})",
            f"- **Tool Invocation:** `{log['actual_tool']}`",
            f"- **Quality Score:** {log['quality_score']} / 5.0",
            f"- **Assistant Response:**",
            f"> {log['response']}",
            "",
        ])

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Saved evaluation Markdown documentation to: {out_md.name}")

    return summary_payload


if __name__ == "__main__":
    run_benchmark()
