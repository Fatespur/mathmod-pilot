from __future__ import annotations

import re
from typing import Any


TYPE_RULES: dict[str, dict[str, list[str]]] = {
    "优化类": {
        "goals": ["最优", "最低", "最大", "最小", "调度", "路径", "方案", "决策", "配置", "选址", "成本"],
        "methods": ["规划", "遗传算法", "粒子群", "模拟退火", "整数规划", "动态规划"],
    },
    "预测类": {
        "goals": ["预测", "未来", "趋势", "补全", "估计未来", "预报", "外推"],
        "methods": ["时间序列", "回归", "lstm", "svm", "arima", "prophet"],
    },
    "评价类": {
        "goals": ["评价", "评分", "排序", "等级", "优劣", "综合得分", "排名"],
        "methods": ["ahp", "topsis", "熵权", "灰色关联", "模糊综合", "主成分"],
    },
    "数理统计类": {
        "goals": ["显著", "分布", "相关", "差异", "置信区间", "检验", "统计规律", "概率"],
        "methods": ["假设检验", "方差分析", "统计", "回归", "bootstrap", "卡方"],
    },
    "机理分析类": {
        "goals": [
            "机理", "机制", "演化", "动力学", "状态变化", "物理规律", "传播规律",
            "系统行为", "参数反演", "厚度反演", "干涉机理", "多次反射",
        ],
        "methods": [
            "微分方程", "守恒", "仿真", "系统动力学", "偏微分", "马尔可夫",
            "snell", "光程差", "双光束", "airy", "fft", "非线性最小二乘",
            "峰谷检测", "嵌套模型",
        ],
    },
}


def split_questions(text: str) -> list[tuple[str, str]]:
    """Split plain text or Markdown problem headings into stable sequential Q IDs."""
    pattern = (
        r"(?mi)^\s*#{0,6}\s*"
        r"(?:问题\s*[一二三四五六七八九十\d]+|"
        r"第\s*[一二三四五六七八九十\d]+\s*问|"
        r"Q\s*\d+)"
        r"\s*[:：、.．]?\s*"
    )
    matches = list(re.finditer(pattern, text))
    if not matches:
        return [("Q1", text.strip())]
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((f"Q{index + 1}", text[match.end() : end].strip()))
    return result


def classify_question(question_id: str, text: str) -> dict[str, Any]:
    normalized = text.lower()
    scores: dict[str, float] = {}
    evidence: dict[str, list[str]] = {}
    for question_type, rules in TYPE_RULES.items():
        goal_hits = [keyword for keyword in rules["goals"] if keyword.lower() in normalized]
        method_hits = [keyword for keyword in rules["methods"] if keyword.lower() in normalized]
        scores[question_type] = len(goal_hits) * 3.0 + len(method_hits)
        evidence[question_type] = goal_hits + method_hits
    ranked = sorted(scores, key=lambda key: (-scores[key], list(TYPE_RULES).index(key)))
    primary = ranked[0]
    best = scores[primary]
    second = scores[ranked[1]]
    if best <= 0:
        confidence = 0.35
        uncertainties = ["未找到明确的最终输出目标；分类需要人工复核"]
    else:
        confidence = min(0.98, 0.58 + 0.08 * best + 0.04 * max(0.0, best - second))
        uncertainties = [] if confidence >= 0.65 else ["题型证据不足"]
    goal_match = re.split(r"[。；;\n]", text.strip())[0][:80]
    return {
        "question_id": question_id,
        "primary_type": primary,
        "confidence": round(confidence, 3),
        "goal": goal_match,
        "inputs": [],
        "outputs": [],
        "auxiliary_methods": evidence[primary],
        "reason": f"根据最终输出目标关键词判定；证据：{', '.join(evidence[primary]) or '无明确关键词'}",
        "uncertainties": uncertainties,
    }


def classify_document(text: str) -> list[dict[str, Any]]:
    return [classify_question(question_id, content) for question_id, content in split_questions(text)]
