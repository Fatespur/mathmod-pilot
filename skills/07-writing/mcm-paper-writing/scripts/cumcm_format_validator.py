#!/usr/bin/env python3
"""Backward compatibility adapter for cumcm_format_validator.py.

DEPRECATED: MathPilot has migrated to Markdown-Only writing (Phase 3E-D).
LaTeX and DOCX format validation are deprecated and replaced by
markdown_paper_validator.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

from markdown_paper_validator import (
    Check,
    audit_markdown_paper,
    format_validation_markdown,
    main as md_validator_main,
)

audit_docx = None
audit_pdf = None

if __name__ == "__main__":
    sys.exit(md_validator_main())
