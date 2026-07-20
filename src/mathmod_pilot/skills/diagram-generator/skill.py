"""Skill entry point: diagram-generator.

Algorithm flowcharts, framework and architecture diagrams via matplotlib.patches.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class DiagramGeneratorSkill(PromptSkill):
    """Entry point for the *diagram-generator* skill (S5, v1.0.0)."""

    skill_name = "diagram-generator"
    skill_stage = "S5"
    skill_version = "1.0.0"
    skill_tier = 2

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("DiagramGeneratorSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
