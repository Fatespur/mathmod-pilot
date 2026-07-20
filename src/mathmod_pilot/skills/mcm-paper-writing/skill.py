"""Skill entry point: mcm-paper-writing.

Contest paper drafting with CUMCM/MCM dual-mode and macro-variable drive.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class McmPaperWritingSkill(PromptSkill):
    """Entry point for the *mcm-paper-writing* skill (S6, v5.0.0)."""

    skill_name = "mcm-paper-writing"
    skill_stage = "S6"
    skill_version = "5.0.0"
    skill_tier = 1

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("McmPaperWritingSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
