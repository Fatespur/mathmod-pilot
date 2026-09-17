from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from markdown_paper_validator import audit_markdown_paper


class MarkdownPaperValidatorTests(unittest.TestCase):
    def test_valid_markdown_paper_passes_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.md"
            paper.write_text(
                "# 题目\n\n"
                "## 摘要\n\n针对复杂系统建立了微分方程与动力学模型，精度达到98%。\n\n"
                "## 一、问题重述\n\n深入分析问题背景与核心需求，分解为五个子任务。\n\n"
                "## 二、模型的建立与求解\n\n"
                "根据经典力学机理 [1]，建立动力学方程：\n\n"
                "$$\\frac{dx}{dt} = -kx$$\n\n"
                "根据方程求解得到连续解曲线。\n\n"
                "## 三、参考文献\n\n"
                "[1] 姜启源. 数学模型[M]. 北京: 高等教育出版社, 2011.\n",
                encoding="utf-8"
            )
            checks, evidence = audit_markdown_paper(paper, min_body_chars=50)
            failed = [c for c in checks if c.status == "FAIL"]
            self.assertEqual(failed, [], [c.message_zh for c in failed])

    def test_illegal_toc_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.md"
            paper.write_text("# 标题\n\n# 目录\n\n- 摘要\n- 一、问题重述\n\n## 一、问题重述\n\n正文", encoding="utf-8")
            checks, _ = audit_markdown_paper(paper, min_body_chars=10)
            toc_check = next(c for c in checks if c.id == "STRUCT-NO-TOC")
            self.assertEqual(toc_check.status, "FAIL")

    def test_unbalanced_math_blocks_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.md"
            paper.write_text("# 标题\n\n## 一、模型\n\n公式损坏: $$x = 1\n\n没有闭合", encoding="utf-8")
            checks, _ = audit_markdown_paper(paper, min_body_chars=10)
            math_check = next(c for c in checks if c.id == "MATH-INTEGRITY")
            self.assertEqual(math_check.status, "FAIL")

    def test_anonymity_violation_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.md"
            paper.write_text("# 标题\n\n作者联系邮箱: contestant@example.edu\n\n## 一、问题重述\n\n正文", encoding="utf-8")
            checks, _ = audit_markdown_paper(paper, min_body_chars=10)
            anon_check = next(c for c in checks if c.id == "ANON-TEXT")
            self.assertEqual(anon_check.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
