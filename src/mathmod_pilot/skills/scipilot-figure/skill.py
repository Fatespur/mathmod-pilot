"""Skill entry point: scipilot-figure.

CUMCM/MCM contest-specific visualisation dispatcher (S5 entry).

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class ScipilotFigureSkill(PromptSkill):
    """Entry point for the *scipilot-figure* skill (S5, v2.0.0)."""

    skill_name = "scipilot-figure"
    skill_stage = "S5"
    skill_version = "2.0.0"
    skill_tier = 1

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("ScipilotFigureSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
