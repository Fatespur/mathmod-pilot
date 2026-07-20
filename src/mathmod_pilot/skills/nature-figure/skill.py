"""
MathMod-Pilot Skill: nature-figure
--------------------------------------------------
Original Source / Inspiration: figures4papers (Chen Liu, Yale University)
Repository: https://github.com/ChenLiu-1996/figures4papers
License: No explicit license declared (academic use; author permits use under
         academic norms)

Modified & Adapted by: Ye Jiahui (William) for MathMod-Pilot Framework
Description: The nature-figure SKILL.md references figures4papers as a pattern
             source for publication-grade matplotlib plots from Nature Machine
             Intelligence and top ML/bioinformatics venues. The assets/figures4papers/
             directory contains original demo scripts from the upstream repo for
             pattern-level reference. The skill.py wrapper, nature_figure_backend.py
             and generate_openrouter_schematic.py are original MathMod-Pilot implementations.
             WARNING: The upstream repo carries no explicit open-source license;
             redistribute assets/figures4papers/ scripts at your own risk or seek
             written permission from the original author.
--------------------------------------------------
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

from mathmod_pilot.skills.base import BaseSkill

logger = logging.getLogger(__name__)


class NatureFigureSkill(BaseSkill):
    """Entry point for the *nature-figure* skill (S5, v1.0.0).

    Wraps two helper scripts:

    * ``nature_figure_backend.py``       -- persistent Python/R backend
      selection (stores user preference on disk).
    * ``generate_openrouter_schematic.py`` -- AI schematic generation via the
      OpenRouter image API (requires ``OPENROUTER_API_KEY``).
    """

    skill_name = "nature-figure"
    skill_stage = "S5"
    skill_version = "1.0.0"
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
        """Dispatch the nature-figure skill.

        Returns the ``SKILL.md`` prompt and the parsed ``manifest.yaml``.
        When ``inputs`` contains ``"action"``:

        * ``"get_backend"``  -- reads the stored backend preference.
        * ``"set_backend"``  -- persists a new backend (``"python"``/``"r"``).
        * ``"generate_schematic"`` -- calls the OpenRouter image API using
          ``OPENROUTER_API_KEY`` from the environment.
        """
        result: dict[str, Any] = {
            "skill": self.meta.name,
            "stage": self.meta.stage,
            "version": self.meta.version,
            "tier": self.meta.tier,
            "prompt": self.get_prompt(),
            "inputs": inputs,
            "status": "ready",
        }

        action = inputs.get("action", "")

        if action in ("get_backend", "set_backend", "clear_backend"):
            backend_mod = self._try_import("nature_figure_backend")
            if backend_mod is not None:
                cfg = backend_mod.config_path()
                if action == "get_backend":
                    result["backend"] = backend_mod.get_backend(cfg)
                elif action == "set_backend":
                    result["backend"] = backend_mod.set_backend(cfg, inputs.get("backend", "python"))
                elif action == "clear_backend":
                    result["backend"] = backend_mod.clear_backend(cfg)
                result["status"] = "backend_ok"

        elif action == "generate_schematic":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                result["status"] = "missing_key"
                result["error"] = "OPENROUTER_API_KEY environment variable is not set."
            else:
                schematic_mod = self._try_import("generate_openrouter_schematic")
                if schematic_mod is not None:
                    result["status"] = "schematic_ready"
                    result["note"] = "Call generate_openrouter_schematic.main() with a configured argparse Namespace."
                else:
                    result["status"] = "module_unavailable"

        return result
