"""MathMod-Pilot Agent -- skill discovery, loading and pipeline orchestration.

The agent follows a *plugin architecture*: it does not hard-code any skill.
Instead it relies on :func:`mathmod_pilot.skills.discover_skills` to scan the
``src/scipilot/skills/`` directory at run-time and build a registry of
:class:`~mathmod_pilot.skills.base.BaseSkill` instances.  This means adding a new
skill is as simple as dropping a folder that contains a ``SKILL.md`` and a
``skill.py`` -- no registration code needs to change.

.. warning::
    LEGACY_SYMBOL_SET / NOT_V3_PRODUCTION_ENTRY

    The S0–S7 pipeline symbol set in this module (PIPELINE list below) is a
    LEGACY nomenclature from the v1 orchestration architecture.

    As of Phase 4 Production Cutover (2026-09-06), the authoritative production
    runtime is ``orchestrator_v3.py`` (V3 HITL State Machine). This agent module
    is NOT the production entry point. It is retained for:
      - Internal skill discovery / loading infrastructure
      - Development and testing of individual Skills
      - Non-production research workflows

    Do NOT use this module to run production competition workflows.
    Use: CUMCM_skill_pipeline_prompt.md (V3) + orchestrator_v3.py CLI
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from mathmod_pilot.skills import discover_skills
from mathmod_pilot.skills.base import BaseSkill

logger = logging.getLogger(__name__)

# The canonical core pipeline: one skill per stage, S0 -> S7.
PIPELINE: list[str] = [
    "brainstorming",          # S0 -- requirement exploration & init
    "problem-analyzer",       # S1 -- problem decomposition & method routing
    "data-processing",        # S2 -- data loading & cleaning
    "mle-solver",             # S3 -- model code generation & execution
    "model-validation",       # S4 -- sensitivity & uncertainty analysis
    "scipilot-figure",        # S5 -- publication-grade visualisation
    "mcm-paper-writing",      # S6 -- contest paper drafting
    "paper-review",           # S7 -- nine-dimension final review
]


@dataclass
class MathModPilotAgent:
    """High-level orchestrator that manages the skill registry and pipeline.

    Examples
    --------
    >>> from mathmod_pilot.core import MathModPilotAgent
    >>> agent = MathModPilotAgent()
    >>> agent.list_skills()                     # doctest: +SKIP
    ['brainstorming', 'data-processing', ...]
    >>> result = agent.run_skill("problem-analyzer", {"problem_text": "..."})
    """

    skills: dict[str, BaseSkill] = field(default_factory=dict)
    _discovered: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        if not self.skills and not self._discovered:
            self.skills = discover_skills()
            self._discovered = True
            logger.info("MathModPilotAgent loaded %d skills", len(self.skills))

    # ------------------------------------------------------------------
    # skill access
    # ------------------------------------------------------------------
    def get_skill(self, name: str) -> BaseSkill | None:
        """Return the skill registered under *name*, or ``None``."""
        return self.skills.get(name)

    def list_skills(self) -> list[str]:
        """Return a sorted list of all registered skill names."""
        return sorted(self.skills.keys())

    def skill_info(self) -> list[dict[str, Any]]:
        """Return a list of metadata dicts for every registered skill."""
        info: list[dict[str, Any]] = []
        for skill in sorted(self.skills.values(), key=lambda s: (s.meta.stage, s.meta.name)):
            info.append(
                {
                    "name": skill.meta.name,
                    "stage": skill.meta.stage,
                    "version": skill.meta.version,
                    "tier": skill.meta.tier,
                    "dir": skill.skill_dir.name,
                }
            )
        return info

    # ------------------------------------------------------------------
    # execution
    # ------------------------------------------------------------------
    def run_skill(self, name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """Execute a single skill by name.

        Raises
        ------
        KeyError
            If *name* is not a registered skill.
        """
        skill = self.get_skill(name)
        if skill is None:
            available = ", ".join(self.list_skills())
            raise KeyError(f"Skill '{name}' not found. Available: {available}")
        logger.info(
            "Executing skill '%s' (stage=%s, v%s)", name, skill.meta.stage, skill.meta.version
        )
        return skill.execute(inputs)

    def run_pipeline(
        self,
        inputs: dict[str, Any],
        stages: list[str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Run a sequence of skills, threading the context dictionary forward.

        Parameters
        ----------
        inputs:
            Initial context passed to the first skill.
        stages:
            Optional list of skill names overriding :data:`PIPELINE`.
            Skills not present in the registry are silently skipped with a
            warning.
        """
        sequence = stages if stages is not None else PIPELINE
        context: dict[str, Any] = dict(inputs)
        results: dict[str, dict[str, Any]] = {}

        for name in sequence:
            skill = self.get_skill(name)
            if skill is None:
                logger.warning("Pipeline skill '%s' not registered -- skipping", name)
                continue
            logger.info("Pipeline step [%s]: %s", skill.meta.stage, name)
            try:
                result = skill.execute(context)
            except Exception as exc:  # pragma: no cover
                logger.exception("Skill '%s' failed: %s", name, exc)
                results[name] = {"status": "error", "error": str(exc)}
                continue
            results[name] = result
            # Thread the result back into the context for downstream skills.
            if isinstance(result, dict):
                context.update(result)

        return results

    def reload(self) -> None:
        """Force a fresh discovery pass (useful after adding skills at runtime)."""
        self.skills = discover_skills(force_reload=True)
        self._discovered = True
        logger.info("Reloaded %d skills", len(self.skills))
