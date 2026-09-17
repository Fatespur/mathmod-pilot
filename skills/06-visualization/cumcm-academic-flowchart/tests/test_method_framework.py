import tempfile
import unittest
from pathlib import Path

from _support import SCRIPTS
from extract_modeling_ir import extract_modeling_ir
from layout_candidates import build_layout, candidate_layout_names
from quality_review import _semantic_review
from validate_layout import validate_layout


class MethodFrameworkTests(unittest.TestCase):
    def extract(self, text: str):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "方案.md"
            source.write_text(text, encoding="utf-8")
            ir, _ = extract_modeling_ir([source], contest_mode=True)
            return ir

    def test_optimization_is_a_hierarchical_method_framework(self):
        ir = self.extract(
            "# 问题一：车辆路径优化\n"
            "定义路径决策变量、成本目标和容量约束，建立混合整数规划模型，"
            "结合遗传算法求解，最后进行可行性检验和敏感性分析。"
        )
        roles = [node.get("framework_role") for node in ir["nodes"]]
        self.assertIn("main_method", roles)
        self.assertGreaterEqual(roles.count("submethod") + roles.count("component"), 4)
        out_degree = {
            node["id"]: sum(edge["source"] == node["id"] for edge in ir["edges"])
            for node in ir["nodes"]
        }
        in_degree = {
            node["id"]: sum(edge["target"] == node["id"] for edge in ir["edges"])
            for node in ir["nodes"]
        }
        self.assertTrue(any(value >= 2 for value in out_degree.values()))
        self.assertTrue(any(value >= 2 for value in in_degree.values()))

    def test_named_prediction_methods_become_parallel_submethods(self):
        ir = self.extract(
            "# 问题一：负荷预测\n"
            "历史负荷与气象数据经过清洗和特征构造，分别训练 LSTM 与 ARIMA，"
            "通过 MAE、RMSE、残差诊断和滚动验证评价预测结果。"
        )
        labels = {node["label"] for node in ir["nodes"]}
        self.assertTrue(any("LSTM" in label for label in labels))
        self.assertTrue(any("ARIMA" in label for label in labels))
        model_nodes = [
            node for node in ir["nodes"]
            if node.get("framework_role") == "submethod" and node.get("module") == "modeling"
        ]
        self.assertGreaterEqual(len(model_nodes), 2)

    def test_evaluation_retains_weight_and_ranking_methods(self):
        ir = self.extract(
            "# 问题一：城市韧性评价\n"
            "构建经济、生态、基础设施和治理指标，结合熵权与 AHP 组合赋权，"
            "采用 TOPSIS 计算综合得分并开展敏感性分析。"
        )
        labels = " ".join(node["label"] for node in ir["nodes"])
        for method in ("熵权", "AHP", "TOPSIS"):
            self.assertIn(method, labels)

    def test_framework_layouts_are_default_and_geometrically_valid(self):
        ir = self.extract(
            "# 问题一：预测\n"
            "清洗历史数据并提取时序与外生特征，训练 LSTM 和 ARIMA，"
            "融合预测结果后进行误差、残差和滚动验证。"
        )
        candidates = candidate_layout_names(ir)
        self.assertIn("method_framework", candidates[:4])
        self.assertIn("hierarchical_tree", candidates[:6])
        for name in ("method_framework", "hierarchical_tree", "layered_architecture"):
            with self.subTest(name=name):
                self.assertTrue(validate_layout(build_layout(ir, name))["passed"])

    def test_optical_inverse_problem_retains_named_methods_and_real_architecture(self):
        ir = self.extract(
            "# 问题一：双光束干涉机理\n"
            "利用双角度反射光谱，依据 Snell 定律、光程差与相位关系建立双光束干涉模型，"
            "推导膜层厚度关系，并进行角度一致性和物理边界检验。\n"
            "# 问题二：SiC 薄膜厚度反演\n"
            "对光谱去趋势和加窗，采用 FFT 获得周期初值，再以峰谷检测和非线性最小二乘"
            "联合反演厚度；使用 Bootstrap 重抽样、窗口敏感性和残差诊断给出置信区间。\n"
            "# 问题三：多光束干涉判别\n"
            "建立 Airy 多光束干涉模型，与双光束基线进行嵌套模型比较，"
            "结合信息准则、Si 对照实验和留块验证判断多次反射影响。"
        )
        self.assertEqual([question["primary_type"] for question in ir["questions"]], ["机理分析类"] * 3)
        labels = " ".join(node["label"] for node in ir["nodes"])
        for method in ("Snell", "光程差", "FFT", "非线性最小二乘", "Airy", "留块验证"):
            self.assertIn(method, labels)
        for question in ir["questions"]:
            question_id = question["question_id"]
            nodes = [node for node in ir["nodes"] if node["question_id"] == question_id]
            node_ids = {node["id"] for node in nodes}
            edges = [
                edge for edge in ir["edges"]
                if edge["source"] in node_ids and edge["target"] in node_ids and not edge.get("feedback")
            ]
            out_degree = {node_id: sum(edge["source"] == node_id for edge in edges) for node_id in node_ids}
            in_degree = {node_id: sum(edge["target"] == node_id for edge in edges) for node_id in node_ids}
            self.assertGreaterEqual(len(nodes), 9)
            self.assertTrue(any(value >= 2 for value in out_degree.values()))
            self.assertTrue(any(value >= 2 for value in in_degree.values()))
        self.assertEqual(candidate_layout_names(ir)[0], "question_architecture")
        layout = build_layout(ir, "question_architecture")
        centers = {
            node["id"]: (node["x"] + node["width"] / 2, node["y"] + node["height"] / 2)
            for node in layout["nodes"]
        }
        dependencies = [edge for edge in ir["edges"] if edge["edge_type"] == "question_dependency"]
        self.assertTrue(dependencies)
        for edge in dependencies:
            self.assertLess(abs(centers[edge["source"]][0] - centers[edge["target"]][0]), 20)

    def test_short_linear_chain_is_blocked_even_below_six_nodes(self):
        ir = self.extract(
            "# 问题一：机理分析\n"
            "基于物理规律建立微分方程，数值求解后进行验证并输出结果。"
        )
        nodes = ir["nodes"][:5]
        for index, node in enumerate(nodes):
            node["framework_role"] = (
                "main_method" if index == 1 else "output" if index == 4 else "component"
            )
            node["semantic_type"] = (
                "mechanism" if index == 1 else "output" if index == 4 else "validation"
            )
        ir["nodes"] = nodes
        ir["edges"] = [
            {
                "id": f"linear_{index}",
                "source": nodes[index]["id"],
                "target": nodes[index + 1]["id"],
                "edge_type": "method_dependency",
                "feedback": False,
                "key": True,
            }
            for index in range(len(nodes) - 1)
        ]
        result = _semantic_review(ir)
        self.assertFalse(result["passed"])
        self.assertTrue(any("linear step chain" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
