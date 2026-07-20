"""Skill entry point: model-validation.

Sensitivity analysis, Monte-Carlo uncertainty and residual diagnostics.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class ModelValidationSkill(PromptSkill):
    """Entry point for the *model-validation* skill (S4, v8.0.0)."""

    skill_name = "model-validation"
    skill_stage = "S4"
    skill_version = "8.0.0"
    skill_tier = 1

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("ModelValidationSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
