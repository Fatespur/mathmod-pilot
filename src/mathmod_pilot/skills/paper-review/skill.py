"""Skill entry point: paper-review.

Nine-dimension final review benchmarked against award-winning papers.

This module is a thin Python wrapper that exposes the native ``SKILL.md``
prompt through the :class:`~mathmod_pilot.skills.base.PromptSkill` interface.  The
full prompt text is preserved verbatim in ``SKILL.md`` and can be retrieved
via :meth:`get_prompt`.
"""
from __future__ import annotations

from typing import Any

from mathmod_pilot.skills.base import PromptSkill


class PaperReviewSkill(PromptSkill):
    """Entry point for the *paper-review* skill (S7, v4.0.0)."""

    skill_name = "paper-review"
    skill_stage = "S7"
    skill_version = "4.0.0"
    skill_tier = 1

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return the skill prompt packaged with contextual inputs."""
        result = super().execute(inputs)
        self.logger.debug("PaperReviewSkill dispatched, inputs keys=%s", list(inputs.keys()))
        return result
