"""Skill entry point: reference-manager.

GB/T 7714 and APA reference formatting with DOI completeness checks.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class ReferenceManagerSkill(PromptSkill):
    """Entry point for the *reference-manager* skill (S6, v1.0.0)."""

    skill_name = "reference-manager"
    skill_stage = "S6"
    skill_version = "1.0.0"
    skill_tier = 3

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("ReferenceManagerSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
