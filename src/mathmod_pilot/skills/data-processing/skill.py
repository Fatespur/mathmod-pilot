"""Skill entry point: data-processing.

Multi-format data loading, cleaning and physical-constraint validation.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class DataProcessingSkill(PromptSkill):
    """Entry point for the *data-processing* skill (S2, v4.0.0)."""

    skill_name = "data-processing"
    skill_stage = "S2"
    skill_version = "4.0.0"
    skill_tier = 1

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("DataProcessingSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
