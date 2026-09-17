import unittest

from _support import SCRIPTS
from classify_question import classify_document, classify_question


class QuestionClassificationTests(unittest.TestCase):
    def assert_type(self, text: str, expected: str) -> None:
        result = classify_question("Q1", text)
        self.assertIn(expected, result["primary_type"])
        self.assertGreaterEqual(result["confidence"], 0.65)

    def test_optimization(self):
        self.assert_type("以成本最小为目标，建立整数规划并优化路径调度", "优化")

    def test_prediction(self):
        self.assert_type("使用 LSTM 时间序列预测未来需求趋势", "预测")

    def test_evaluation(self):
        self.assert_type("建立指标体系，使用 AHP TOPSIS 评价并排序", "评价")

    def test_statistics(self):
        self.assert_type("执行假设检验并判断差异是否显著，给出置信区间", "统计")

    def test_mechanism(self):
        self.assert_type("根据质量守恒建立微分方程解释扩散机理", "机理")

    def test_multi_question_split(self):
        result = classify_document("# 问题一：预测\n预测未来趋势\n# 问题二：优化\n最小化成本并调度")
        self.assertEqual(len(result), 2)
        self.assertEqual([item["question_id"] for item in result], ["Q1", "Q2"])

    def test_low_confidence_is_recorded(self):
        result = classify_question("Q1", "描述现象")
        self.assertLess(result["confidence"], 0.65)
        self.assertTrue(result["uncertainties"])


if __name__ == "__main__":
    unittest.main()
