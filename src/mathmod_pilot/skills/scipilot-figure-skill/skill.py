"""
MathMod-Pilot Skill: scipilot-figure-skill
--------------------------------------------------
Original Source / Inspiration: scipilot-figure-skill (Haojae)
Repository: https://github.com/Haojae/scipilot-figure-skill
License: MIT License (Copyright (c) 2026 Haojae)

Modified & Adapted by: Ye Jiahui (William) for MathMod-Pilot Framework
Description: Integrated the original skill as a MathMod-Pilot BaseSkill subclass.
             The scripts/ directory ships the original unmodified Python modules
             (setup_style, profile_data, export_figure, layout_tools, check_figure,
             visual_qa). A skill.py wrapper was added to expose the SKILL.md prompt
             through the BaseSkill interface, and scripts/ was added to sys.path so
             the modules remain importable as top-level scripts.
--------------------------------------------------
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from mathmod_pilot.skills.base import BaseSkill

logger = logging.getLogger(__name__)


class ScipilotFigureSkillWrapper(BaseSkill):
    """Entry point for the *scipilot-figure-skill* skill (S5, v2.1.0).

    Provides a programmatic interface to the visualisation-advisor tool-chain:

    * ``setup_style``      -- publication-grade matplotlib/seaborn presets
    * ``profile_data``     -- data profiling and chart-type recommendation
    * ``export_figure``    -- multi-format export with grayscale preview
    * ``layout_tools``     -- panel labels and constrained-layout finalisation
    * ``check_figure``     -- DPI / font / SVG quality auditor
    * ``visual_qa``        -- glyph-missing detection and layout-overlap audit
    """

    skill_name = "scipilot-figure-skill"
    skill_stage = "S5"
    skill_version = "2.1.0"
    skill_tier = 2

    def __init__(self, skill_dir: Path | str | None = None) -> None:
        super().__init__(skill_dir)
        scripts_dir = self.skill_dir / "scripts"
        if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

    # ------------------------------------------------------------------
    # lazy module accessors
    # ------------------------------------------------------------------
    def _try_import(self, module_name: str) -> Any:
        try:
            return __import__(module_name)
        except ImportError:
            self.logger.debug("Optional module '%s' not available", module_name)
            return None

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Dispatch the visualisation advisor.

        Returns the ``SKILL.md`` prompt together with a capability manifest.
        When ``inputs`` contains a ``"data"`` key, :func:`profile_data` is
        invoked to produce a data-profiling report and chart suggestions.
        """
        result: dict[str, Any] = {
            "skill": self.meta.name,
            "stage": self.meta.stage,
            "version": self.meta.version,
            "tier": self.meta.tier,
            "prompt": self.get_prompt(),
            "inputs": inputs,
            "status": "ready",
            "capabilities": [
                "setup_style",
                "profile_data",
                "export_figure",
                "layout_tools",
                "check_figure",
                "visual_qa",
            ],
        }

        data = inputs.get("data")
        if data is not None:
            profile_mod = self._try_import("profile_data")
            if profile_mod is not None:
                try:
                    group_cols = inputs.get("group_cols")
                    info = profile_mod.profile_data(data, group_cols=group_cols)
                    result["data_profile"] = info
                    result["chart_suggestions"] = info.get("suggested_charts", [])
                    result["status"] = "profiled"
                except Exception as exc:  # pragma: no cover
                    self.logger.exception("Data profiling failed: %s", exc)
                    result["status"] = "profile_error"
                    result["error"] = str(exc)

        return result
