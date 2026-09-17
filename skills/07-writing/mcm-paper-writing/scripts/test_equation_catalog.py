from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from equation_catalog import extract_equations, write_tex


class EquationCatalogTests(unittest.TestCase):
    def test_extract_numbered_display_and_inline(self) -> None:
        paper = r"""# 论文标题

## 摘要
误差记为 \(e_i\)。

## 一、模型建立
\begin{equation}
\label{eq:objective}
\min_x f(x)
\end{equation}

由式\eqref{eq:objective}可得结论。

\[
y=x^2
\]
"""
        records, issues = extract_equations(paper)
        self.assertEqual(len(records), 3)
        numbered = [item for item in records if item.equation_number]
        self.assertEqual(numbered[0].equation_number, 1)
        self.assertEqual(numbered[0].label, "eq:objective")
        self.assertTrue(numbered[0].referenced_at)
        self.assertFalse(any(item["severity"] == "FAIL" for item in issues), issues)

    def test_generated_label_warns(self) -> None:
        records, issues = extract_equations("\\begin{equation}\nx=1\n\\end{equation}")
        self.assertEqual(records[0].label, "eq:auto_001")
        self.assertTrue(any(item["severity"] == "WARNING" for item in issues))

    def test_duplicate_and_unresolved_labels_fail(self) -> None:
        paper = r"""\begin{equation}
\label{eq:a}a=1
\end{equation}
\begin{equation}
\label{eq:a}a=2
\end{equation}
See \eqref{eq:missing}.
"""
        _, issues = extract_equations(paper)
        messages = [item["message"] for item in issues if item["severity"] == "FAIL"]
        self.assertTrue(any("duplicate label" in message for message in messages))
        self.assertTrue(any("unresolved" in message for message in messages))

    def test_write_tex_preserves_source(self) -> None:
        records, _ = extract_equations(r"\[x=1\]")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "equations.tex"
            write_tex(records, path)
            self.assertIn(r"\[x=1\]", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
