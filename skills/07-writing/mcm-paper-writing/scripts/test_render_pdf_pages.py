from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_pdf_pages import resolve_pdftoppm


class RenderPdfPagesTests(unittest.TestCase):
    def test_resolver_returns_existing_command(self) -> None:
        command = Path(resolve_pdftoppm())
        self.assertTrue(command.exists(), command)


if __name__ == "__main__":
    unittest.main()
