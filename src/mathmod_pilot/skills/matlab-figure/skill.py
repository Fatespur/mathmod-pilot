"""Skill entry point: matlab-figure.

MATLAB-native plotting: 3-D surfaces, vector fields and Simulink dynamics.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class MatlabFigureSkill(PromptSkill):
    """Entry point for the *matlab-figure* skill (S5, v1.0.0)."""

    skill_name = "matlab-figure"
    skill_stage = "S5"
    skill_version = "1.0.0"
    skill_tier = 2

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("MatlabFigureSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
