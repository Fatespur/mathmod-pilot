"""MathMod-Pilot -- an Agent-Native skill library for mathematical modelling.

MathMod-Pilot packages 15 specialised *skills* -- each a self-contained folder with
a native ``SKILL.md`` prompt and a Python entry point -- that together cover
the full CUMCM / MCM pipeline from problem analysis to paper review.

Quick start
-----------
    >>> from mathmod_pilot.core import MathModPilotAgent
    >>> agent = MathModPilotAgent()
    >>> agent.list_skills()          # doctest: +SKIP
    ['brainstorming', 'data-processing', ...]
"""
from __future__ import annotations

__version__ = "1.0.0"
__all__ = ["__version__"]

# Lazy imports to avoid heavy dependencies at import time.
def __getattr__(name: str):  # pragma: no cover
    if name == "MathModPilotAgent":
        from mathmod_pilot.core.agent import MathModPilotAgent

        return MathModPilotAgent
    if name == "BaseSkill":
        from mathmod_pilot.skills.base import BaseSkill

        return BaseSkill
    if name == "discover_skills":
        from mathmod_pilot.skills import discover_skills

        return discover_skills
    raise AttributeError(f"module 'scipilot' has no attribute {name!r}")
