from __future__ import annotations

import re
from typing import Any, Callable

from utils import stable_id, unique_preserving


METHOD_PATTERNS: dict[str, dict[str, list[tuple[str, str]]]] = {
    "优化类": {
        "model": [
            (r"混合整数(?:线性)?规划|MILP", "混合整数规划"),
            (r"整数规划", "整数规划"),
            (r"线性规划", "线性规划"),
            (r"非线性规划", "非线性规划"),
            (r"多目标(?:优化|规划)|NSGA-?II", "多目标优化"),
            (r"动态规划", "动态规划"),
        ],
        "solver": [
            (r"遗传算法|\bGA\b", "遗传算法"),
            (r"粒子群|\bPSO\b", "粒子群算法"),
            (r"模拟退火", "模拟退火"),
            (r"分支定界", "分支定界"),
            (r"禁忌搜索", "禁忌搜索"),
            (r"强化学习", "强化学习"),
        ],
    },
    "预测类": {
        "model": [
            (r"\bLSTM\b|长短期记忆", "LSTM"),
            (r"\bARIMA\b", "ARIMA"),
            (r"\bProphet\b", "Prophet"),
            (r"\bSVM\b|支持向量", "SVM"),
            (r"\bXGBoost\b", "XGBoost"),
            (r"随机森林", "随机森林"),
            (r"\bTransformer\b", "Transformer"),
            (r"\bCNN\b|卷积神经网络", "CNN"),
            (r"\bGAM\b|广义加性", "GAM"),
            (r"灰色预测|GM\s*\(\s*1\s*,\s*1\s*\)", "GM(1,1)"),
        ],
        "metric": [
            (r"\bMAE\b", "MAE"),
            (r"\bRMSE\b", "RMSE"),
            (r"\bMAPE\b", "MAPE"),
            (r"\bR\^?2\b|决定系数", "R²"),
        ],
    },
    "评价类": {
        "weight": [
            (r"\bAHP\b|层次分析", "AHP"),
            (r"熵权", "熵权法"),
            (r"\bCRITIC\b", "CRITIC"),
            (r"变异系数", "变异系数法"),
            (r"组合赋权", "组合赋权"),
        ],
        "model": [
            (r"\bTOPSIS\b", "TOPSIS"),
            (r"灰色关联", "灰色关联分析"),
            (r"模糊综合", "模糊综合评价"),
            (r"主成分|\bPCA\b", "主成分分析"),
            (r"\bDEA\b|数据包络", "DEA"),
        ],
    },
    "数理统计类": {
        "method": [
            (r"方差分析|\bANOVA\b", "方差分析"),
            (r"\bBootstrap\b|自助法", "Bootstrap"),
            (r"正态性检验|Shapiro", "正态性检验"),
            (r"卡方检验", "卡方检验"),
            (r"\bt[\s-]*检验|t检验", "t 检验"),
            (r"秩和检验|Mann.?Whitney", "秩和检验"),
            (r"回归分析", "回归分析"),
        ],
    },
    "机理分析类": {
        "equation": [
            (r"Snell(?:['’]s)?\s*(?:定律|law)?|斯涅尔定律", "Snell 定律"),
            (r"光程差", "光程差关系"),
            (r"相位(?:差|关系|累积)", "相位关系"),
            (r"双光束(?:干涉)?", "双光束干涉模型"),
            (r"\bAiry\b|多光束(?:干涉)?", "Airy 多光束模型"),
            (r"偏微分|PDE", "偏微分方程"),
            (r"常微分|ODE", "常微分方程"),
            (r"系统动力学", "系统动力学"),
            (r"马尔可夫", "马尔可夫模型"),
            (r"质量守恒", "质量守恒"),
            (r"能量守恒", "能量守恒"),
        ],
        "solver": [
            (r"\bFFT\b|快速傅里叶", "FFT 周期初始化"),
            (r"峰谷(?:检测|回归|拟合)", "峰谷检测与拟合"),
            (r"非线性最小二乘", "非线性最小二乘"),
            (r"参数反演|联合反演", "参数联合反演"),
            (r"轮廓拟合|曲线拟合", "光谱轮廓拟合"),
            (r"有限差分", "有限差分"),
            (r"有限元", "有限元"),
            (r"龙格.?库塔|Runge.?Kutta", "Runge–Kutta"),
            (r"数值求解|数值模拟", "数值求解"),
        ],
        "validation": [
            (r"\bBootstrap\b|重抽样", "Bootstrap 重抽样"),
            (r"窗口(?:敏感性|检验|稳定性)", "窗口敏感性"),
            (r"残差(?:诊断|检验|分析)", "残差诊断"),
            (r"角度一致性|一致性(?:检验|验证)", "角度一致性检验"),
            (r"物理边界|物理一致性", "物理边界复核"),
            (r"留块(?:验证|检验)", "留块验证"),
            (r"Si\s*对照|对照实验", "Si 对照实验"),
            (r"信息准则|AIC|BIC", "信息准则"),
            (r"嵌套模型(?:比较|检验)", "嵌套模型比较"),
        ],
    },
}


INDICATOR_DIMENSIONS = [
    ("经济", "经济维度"),
    ("生态", "生态维度"),
    ("环境", "环境维度"),
    ("基础设施", "基础设施维度"),
    ("治理", "治理维度"),
    ("技术", "技术维度"),
    ("管理", "管理维度"),
    ("社会", "社会维度"),
    ("风险", "风险维度"),
]


def detect_methods(text: str, question_type: str) -> dict[str, list[str]]:
    detected: dict[str, list[str]] = {}
    for category, patterns in METHOD_PATTERNS.get(question_type, {}).items():
        values = [label for pattern, label in patterns if re.search(pattern, text, flags=re.IGNORECASE)]
        values = unique_preserving(values)
        detected[category] = [
            value
            for value in values
            if not any(value != other and value in other for other in values)
        ]
    return detected


class _FrameworkBuilder:
    def __init__(
        self,
        question: dict[str, Any],
        source_reference: str,
    ) -> None:
        self.question = question
        self.question_id = question["question_id"]
        self.source_reference = source_reference
        self.low_confidence = question.get("confidence", 0) < 0.65
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.by_key: dict[str, dict[str, Any]] = {}

    def add(
        self,
        key: str,
        semantic_type: str,
        label: str,
        stage: int,
        framework_role: str,
        module: str,
        *,
        branch: str = "main",
        parent: str | None = None,
        inferred: bool = False,
    ) -> str:
        node_id = stable_id("node", self.question_id, key)
        importance = "primary" if framework_role == "main_method" else "secondary"
        if framework_role in {"context", "evidence"}:
            importance = "auxiliary"
        node = {
            "id": node_id,
            "label": label,
            "short_label": label if len(label) <= 14 else label[:13] + "…",
            "description": "",
            "semantic_type": semantic_type,
            "question_id": self.question_id,
            "importance": importance,
            "level": stage,
            "stage": stage,
            "framework_role": framework_role,
            "module": module,
            "branch": branch,
            "parent_key": parent,
            "source_reference": self.source_reference,
            "inferred": bool(inferred or self.low_confidence),
        }
        self.nodes.append(node)
        self.by_key[key] = node
        return key

    def link(
        self,
        source: str,
        target: str,
        *,
        edge_type: str = "method_dependency",
        label: str = "",
        feedback: bool = False,
        key: bool = True,
    ) -> None:
        source_id, target_id = self.by_key[source]["id"], self.by_key[target]["id"]
        self.edges.append(
            {
                "id": stable_id("edge", source_id, target_id, edge_type),
                "source": source_id,
                "target": target_id,
                "edge_type": edge_type,
                "label": label,
                "feedback": feedback,
                "key": key,
            }
        )

    def finish(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        for node in self.nodes:
            parent_key = node.pop("parent_key", None)
            node["parent_id"] = self.by_key[parent_key]["id"] if parent_key in self.by_key else None
        return self.nodes, self.edges


def _optimization(
    builder: _FrameworkBuilder,
    text: str,
    methods: dict[str, list[str]],
    compact: bool,
) -> None:
    builder.add("context", "input", "任务场景与输入参数", 0, "context", "context")
    builder.add("variable", "decision_variable", "路径与调度决策变量", 1, "component", "formulation", branch="variable")
    builder.add("objective", "objective", "总成本最小化目标", 1, "component", "formulation", branch="objective")
    builder.add("constraint", "constraint", "容量·时间窗·守恒约束", 1, "component", "formulation", branch="constraint")
    model_names = methods.get("model") or ["目标—约束优化模型"]
    model_label = " / ".join(model_names[:2])
    builder.add("main_model", "model", model_label, 2, "main_method", "modeling", inferred=not methods.get("model"))
    for key in ("variable", "objective", "constraint"):
        builder.link("context", key, key=False)
        builder.link(key, "main_model")
    solver_names = methods.get("solver") or ["精确求解", "智能优化"]
    if compact:
        solver_names = solver_names[:2]
    solver_keys = []
    for index, name in enumerate(solver_names[:3]):
        key = f"solver_{index}"
        builder.add(key, "solver", name, 3, "submethod", "solution", branch=f"solver-{index}", parent="main_model", inferred=not methods.get("solver"))
        builder.link("main_model", key, edge_type="method_branch")
        solver_keys.append(key)
    builder.add("convergence", "convergence", "收敛与终止判定", 4, "validation", "validation")
    builder.add("feasibility", "validation", "可行性与约束复核", 4, "validation", "validation")
    for key in solver_keys:
        builder.link(key, "convergence")
        builder.link(key, "feasibility", key=False)
    builder.add("output", "output", "最优调度方案", 5, "output", "result")
    builder.link("convergence", "output")
    builder.link("feasibility", "output")
    if not compact:
        builder.add("sensitivity", "sensitivity", "参数敏感性与稳健性", 5, "validation", "result")
        builder.link("output", "sensitivity", edge_type="validation_flow", key=False)
    if re.search(r"迭代|反馈|不通过|更新参数", text):
        builder.link("convergence", "main_model", edge_type="feedback", label="未收敛", feedback=True, key=False)


def _prediction(
    builder: _FrameworkBuilder,
    text: str,
    methods: dict[str, list[str]],
    compact: bool,
) -> None:
    data_specs = [("history", "历史目标序列")]
    if re.search(r"气象|外生|环境|宏观", text):
        data_specs.append(("external", "外生影响变量"))
    if re.search(r"图像|文本|多模态", text):
        data_specs.append(("multimodal", "图像与文本信息"))
    for key, label in data_specs:
        builder.add(f"data_{key}", "data", label, 0, "context", "data", branch=key)
    builder.add("preprocess", "preprocessing", "缺失·异常·尺度处理", 1, "component", "data")
    for key, _ in data_specs:
        builder.link(f"data_{key}", "preprocess")
    feature_specs = [("temporal", "趋势·周期·滞后特征")]
    if len(data_specs) > 1:
        feature_specs.append(("external", "外生与交互特征"))
    if re.search(r"图像|文本|多模态", text):
        feature_specs.append(("semantic", "空间与语义特征"))
    if compact:
        feature_specs = feature_specs[:2]
    for key, label in feature_specs:
        node_key = f"feature_{key}"
        builder.add(node_key, "feature", label, 2, "component", "feature", branch=key)
        builder.link("preprocess", node_key, edge_type="feature_branch")
    model_names = methods.get("model") or ["统计预测子模型", "机器学习子模型"]
    if compact:
        model_names = model_names[:2]
    model_keys = []
    for index, name in enumerate(model_names[:4]):
        key = f"model_{index}"
        builder.add(key, "model", f"{name} 预测", 3, "submethod", "modeling", branch=f"model-{index}", inferred=not methods.get("model"))
        for feature_key, _ in feature_specs:
            builder.link(f"feature_{feature_key}", key, edge_type="model_input", key=False)
        model_keys.append(key)
    core_label = "多模型融合预测框架" if len(model_keys) > 1 else "预测模型推理框架"
    builder.add("fusion", "model", core_label, 4, "main_method", "modeling")
    for key in model_keys:
        builder.link(key, "fusion", edge_type="model_fusion")
    builder.add("prediction", "prediction", "未来趋势与预测区间", 5, "output", "result")
    builder.link("fusion", "prediction")
    metric_names = methods.get("metric") or ["误差指标"]
    metric_label = " / ".join(metric_names[:3])
    builder.add("metric", "metric", f"{metric_label}评价", 6, "validation", "validation")
    builder.add("residual", "diagnosis", "残差结构诊断", 6, "validation", "validation")
    builder.add("rolling", "validation", "滚动验证与泛化检验", 6, "validation", "validation")
    for key in ("metric", "residual", "rolling"):
        builder.link("prediction", key, edge_type="validation_branch", key=False)


def _evaluation(
    builder: _FrameworkBuilder,
    text: str,
    methods: dict[str, list[str]],
    compact: bool,
) -> None:
    builder.add("object", "object", "评价对象与目标层", 0, "context", "indicator")
    dimensions = [label for keyword, label in INDICATOR_DIMENSIONS if keyword in text]
    dimensions = unique_preserving(dimensions) or ["资源维度", "效益维度", "风险维度"]
    if compact:
        dimensions = dimensions[:3]
    dimension_keys = []
    for index, label in enumerate(dimensions[:5]):
        key = f"dimension_{index}"
        builder.add(key, "indicator", label, 1, "component", "indicator", branch=f"dimension-{index}")
        builder.link("object", key, edge_type="indicator_branch")
        dimension_keys.append(key)
    builder.add("indicator_system", "indicator", "多层级指标体系", 2, "submethod", "indicator")
    for key in dimension_keys:
        builder.link(key, "indicator_system", edge_type="indicator_merge")
    prep_specs = [
        ("screening", "screening", "相关性与冗余筛选"),
        ("direction", "direction", "指标正向化"),
        ("normalization", "normalization", "无量纲标准化"),
    ]
    if compact:
        prep_specs = prep_specs[-2:]
    for index, (key, semantic, label) in enumerate(prep_specs):
        builder.add(key, semantic, label, 3, "component", "preprocessing", branch=f"prep-{index}")
        builder.link("indicator_system", key, edge_type="preprocess_branch", key=False)
    weight_names = methods.get("weight") or ["主观赋权", "客观赋权"]
    weight_names = [name for name in weight_names if name != "组合赋权"] or ["组合赋权"]
    weight_keys = []
    for index, name in enumerate(weight_names[:3]):
        key = f"weight_{index}"
        builder.add(key, "weight", name, 4, "submethod", "weighting", branch=f"weight-{index}", inferred=not methods.get("weight"))
        for prep_key, _, _ in prep_specs:
            builder.link(prep_key, key, edge_type="weight_input", key=False)
        weight_keys.append(key)
    builder.add("combined_weight", "weight", "组合权重向量", 5, "component", "weighting")
    for key in weight_keys:
        builder.link(key, "combined_weight", edge_type="weight_fusion")
    model_names = methods.get("model") or ["综合评价模型"]
    main_label = " + ".join(model_names[:2])
    builder.add("evaluation_model", "model", main_label, 6, "main_method", "modeling", inferred=not methods.get("model"))
    builder.link("combined_weight", "evaluation_model")
    for prep_key, _, _ in prep_specs:
        builder.link(prep_key, "evaluation_model", edge_type="standardized_data", key=False)
    builder.add("output", "output", "综合得分·排序·分级", 7, "output", "result")
    builder.link("evaluation_model", "output")
    builder.add("consistency", "validation", "一致性与合理性检验", 8, "validation", "validation")
    builder.add("sensitivity", "sensitivity", "权重敏感性分析", 8, "validation", "validation")
    builder.link("output", "consistency", edge_type="validation_branch", key=False)
    builder.link("output", "sensitivity", edge_type="validation_branch", key=False)


def _statistics(
    builder: _FrameworkBuilder,
    text: str,
    methods: dict[str, list[str]],
    compact: bool,
) -> None:
    builder.add("problem", "goal", "统计问题与研究假设", 0, "context", "context")
    builder.add("sample", "sample", "样本设计与变量定义", 1, "component", "data")
    builder.link("problem", "sample")
    quality_specs = [
        ("missing", "缺失与异常检查"),
        ("distribution", "分布与独立性检查"),
        ("descriptive", "描述统计与可视探索"),
    ]
    if compact:
        quality_specs = quality_specs[1:]
    for index, (key, label) in enumerate(quality_specs):
        semantic = "descriptive" if key == "descriptive" else "data_quality"
        builder.add(key, semantic, label, 2, "component", "data", branch=f"quality-{index}")
        builder.link("sample", key, edge_type="quality_branch", key=False)
    builder.add("inference", "statistic", "统计推断框架", 3, "main_method", "modeling")
    for key, _ in quality_specs:
        builder.link(key, "inference")
    method_names = methods.get("method") or ["参数检验", "非参数检验", "Bootstrap"]
    if compact:
        method_names = method_names[:2]
    method_keys = []
    for index, name in enumerate(method_names[:4]):
        key = f"method_{index}"
        semantic = "assumption_test" if "正态" in name else "statistic"
        builder.add(key, semantic, name, 4, "submethod", "inference", branch=f"test-{index}", parent="inference", inferred=not methods.get("method"))
        builder.link("inference", key, edge_type="test_branch")
        method_keys.append(key)
    builder.add("synthesis", "significance", "显著性与效应量综合", 5, "component", "inference")
    for key in method_keys:
        builder.link(key, "synthesis", edge_type="inference_merge")
    builder.add("interval", "interval", "置信区间与不确定性", 6, "validation", "validation")
    builder.add("diagnosis", "diagnosis", "稳健性与残差诊断", 6, "validation", "validation")
    builder.link("synthesis", "interval", edge_type="validation_branch")
    builder.link("synthesis", "diagnosis", edge_type="validation_branch", key=False)
    builder.add("output", "output", "统计结论与实际解释", 7, "output", "result")
    builder.link("interval", "output")
    builder.link("diagnosis", "output", key=False)


def _mechanism(
    builder: _FrameworkBuilder,
    text: str,
    methods: dict[str, list[str]],
    compact: bool,
) -> None:
    optical = bool(
        re.search(
            r"光谱|光束|干涉|反射|折射|Snell|光程差|膜厚|SiC|\bAiry\b|\bFFT\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    if optical:
        builder.add("boundary", "data", "多角度反射光谱", 0, "context", "data")
        builder.add("assumption", "assumption", "平行膜层与相干假设", 0, "context", "context")
        variable_specs = [
            ("state", "state_variable", "波长与入射角"),
            ("control", "parameter", "折射率与膜厚"),
            ("external", "parameter", "光程差与相位"),
        ]
    else:
        builder.add("boundary", "boundary", "系统边界与作用对象", 0, "context", "context")
        builder.add("assumption", "assumption", "机理假设与守恒前提", 0, "context", "context")
        variable_specs = [
            ("state", "state_variable", "状态变量"),
            ("control", "control_variable", "控制变量"),
            ("external", "exogenous_variable", "外生变量"),
            ("parameter", "parameter", "关键机理参数"),
        ]
        if compact:
            variable_specs = [variable_specs[0], variable_specs[-1]]
    for index, (key, semantic, label) in enumerate(variable_specs):
        builder.add(key, semantic, label, 1, "component", "variables", branch=f"variable-{index}")
        builder.link("boundary", key, edge_type="variable_branch")
        builder.link("assumption", key, edge_type="assumption_constraint", key=False)
    equation_names = methods.get("equation") or (
        ["光谱干涉厚度反演模型"] if optical else ["守恒与作用机制"]
    )
    if optical and re.search(r"\bAiry\b|多光束|判别", text, flags=re.IGNORECASE):
        mechanism_label = "Airy 多光束干涉模型"
    elif optical and re.search(r"反演|膜厚|SiC", text, flags=re.IGNORECASE):
        mechanism_label = "光谱干涉厚度反演模型"
    elif optical:
        mechanism_label = "双光束干涉物理模型"
    else:
        mechanism_label = " + ".join(equation_names[:2])
    builder.add("mechanism", "mechanism", mechanism_label, 2, "main_method", "modeling", inferred=not methods.get("equation"))
    for key, _, _ in variable_specs:
        builder.link(key, "mechanism")
    if optical and re.search(r"\bAiry\b|多光束|判别", text, flags=re.IGNORECASE):
        condition_specs = [
            ("initial", "initial_condition", "双光束基线模型"),
            ("boundary_condition", "boundary_condition", "多次反射相位累积"),
        ]
    elif optical and re.search(r"反演|膜厚|SiC", text, flags=re.IGNORECASE):
        condition_specs = [
            ("initial", "initial_condition", "频域周期初值"),
            ("boundary_condition", "boundary_condition", "膜厚物理边界"),
        ]
    elif optical:
        condition_specs = [
            ("initial", "initial_condition", "Snell 折射关系"),
            ("boundary_condition", "boundary_condition", "光程差—相位关系"),
        ]
    else:
        condition_specs = [("initial", "initial_condition", "初始条件"), ("boundary_condition", "boundary_condition", "边界条件")]
    for index, (key, semantic, label) in enumerate(condition_specs):
        builder.add(key, semantic, label, 3, "component", "equation", branch=f"condition-{index}")
        builder.link("mechanism", key, edge_type="condition_branch", key=False)
    if optical and re.search(r"\bAiry\b|多光束", text, flags=re.IGNORECASE):
        equation_label = "Airy 强度方程"
    elif optical and re.search(r"反演|膜厚|SiC", text, flags=re.IGNORECASE):
        equation_label = "光谱周期—膜厚方程"
    elif optical:
        equation_label = "双光束相位—厚度方程"
    else:
        equation_label = "控制方程组"
    builder.add("equation", "equation", equation_label, 3, "submethod", "equation", parent="mechanism")
    builder.link("mechanism", "equation")
    for key, _, _ in condition_specs:
        builder.link(key, "equation", edge_type="condition_input")
    solver_names = methods.get("solver") or (
        ["解析推导", "角度联合校准"] if optical else ["参数辨识", "数值离散求解"]
    )
    if compact and not optical:
        solver_names = solver_names[:2]
    solver_keys = []
    for index, name in enumerate(solver_names[:3]):
        key = f"solver_{index}"
        semantic = "identification" if "辨识" in name else "solver"
        builder.add(key, semantic, name, 4, "submethod", "solution", branch=f"solver-{index}", inferred=not methods.get("solver"))
        builder.link("equation", key, edge_type="solver_branch")
        solver_keys.append(key)
    simulation_label = "理论光谱重构与残差" if optical else "动态仿真与状态演化"
    builder.add("simulation", "solver", simulation_label, 5, "component", "solution")
    for key in solver_keys:
        builder.link(key, "simulation", edge_type="simulation_merge")
    validation_names = methods.get("validation") or ["实测数据与物理一致性"]
    validation_keys = []
    for index, name in enumerate(validation_names[:3]):
        key = f"validation_{index}"
        builder.add(
            key,
            "validation",
            name,
            6,
            "validation",
            "validation",
            branch=f"validation-{index}",
            parent="mechanism",
            inferred=not methods.get("validation"),
        )
        builder.link("simulation", key, edge_type="validation_branch", key=index == 0)
        validation_keys.append(key)
    if optical and re.search(r"\bAiry\b|多光束|判别", text, flags=re.IGNORECASE):
        output_label = "多光束效应判别结论"
    elif optical and re.search(r"反演|膜厚|SiC", text, flags=re.IGNORECASE):
        output_label = "膜厚估计与置信区间"
    elif optical:
        output_label = "双光束厚度关系"
    else:
        output_label = "机理解释与仿真结果"
    builder.add("output", "output", output_label, 7, "output", "result")
    for index, key in enumerate(validation_keys):
        builder.link(key, "output", edge_type="validation_merge", key=index == 0)


BUILDERS: dict[str, Callable[[_FrameworkBuilder, str, dict[str, list[str]], bool], None]] = {
    "优化类": _optimization,
    "预测类": _prediction,
    "评价类": _evaluation,
    "数理统计类": _statistics,
    "机理分析类": _mechanism,
}


def build_method_framework(
    question: dict[str, Any],
    text: str,
    source_reference: str,
    *,
    compact: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, list[str]]]:
    methods = detect_methods(text, question["primary_type"])
    builder = _FrameworkBuilder(question, source_reference)
    BUILDERS[question["primary_type"]](builder, text, methods, compact)
    nodes, edges = builder.finish()
    return nodes, edges, methods
