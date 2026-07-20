"""Skill entry point: systematic-debugging.

Anti-pattern library and automatic error-repair routing for modelling code.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class SystematicDebuggingSkill(PromptSkill):
    """Entry point for the *systematic-debugging* skill (aux, v3.0.0)."""

    skill_name = "systematic-debugging"
    skill_stage = "aux"
    skill_version = "3.0.0"
    skill_tier = 3

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("SystematicDebuggingSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
