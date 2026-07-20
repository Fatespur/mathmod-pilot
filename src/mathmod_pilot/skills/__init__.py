"""Dynamic skill discovery and registration.

At import time this module scans every sub-directory of ``src/scipilot/skills/``
that contains a ``SKILL.md`` file.  If a ``skill.py`` is present it is imported
and the first :class:`~mathmod_pilot.skills.base.BaseSkill` subclass found is
instantiated and registered.  Directories without ``skill.py`` fall back to a
prompt-only wrapper so that even pure-markdown skills remain callable.
"""
from __future__ import annotations

import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Any

from .base import BaseSkill, PromptSkill, SkillMeta

logger = logging.getLogger(__name__)

_SKILLS_DIR: Path = Path(__file__).resolve().parent


class _FallbackSkill(PromptSkill):
    """Auto-generated wrapper for directories that lack a ``skill.py``."""

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        result = super().execute(inputs)
        result["status"] = "prompt_only_fallback"
        return result


def _instantiate(cls: type[BaseSkill], skill_dir: Path) -> BaseSkill | None:
    """Safely instantiate a skill class, returning ``None`` on failure."""
    try:
        return cls(skill_dir=skill_dir)
    except Exception:  # pragma: no cover
        logger.exception("Failed to instantiate skill in %s", skill_dir)
        return None


def discover_skills(force_reload: bool = False) -> dict[str, BaseSkill]:
    """Scan the skills directory and build a ``{name: instance}`` registry.

    Parameters
    ----------
    force_reload:
        When *True*, previously imported ``skill.py`` modules are removed from
        :data:`sys.modules` so that changes are picked up on re-discovery.

    Returns
    -------
    dict[str, BaseSkill]
        Mapping keyed by the skill's declared name (falling back to the
        directory name when the front-matter does not specify one).
    """
    registry: dict[str, BaseSkill] = {}

    for entry in sorted(_SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(("_", ".")):
            continue

        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue

        skill_py = entry / "skill.py"
        if not skill_py.exists():
            # Prompt-only skill without an explicit wrapper.
            instance = _FallbackSkill(skill_dir=entry)
            instance.skill_name = entry.name
            instance.meta = SkillMeta(
                name=entry.name,
                stage="",
                tier=3,
            )
            registry[entry.name] = instance
            logger.debug("Registered prompt-only skill: %s", entry.name)
            continue

        mod_name = f"mathmod_pilot.skills.{entry.name}.skill"
        if force_reload and mod_name in sys.modules:
            del sys.modules[mod_name]

        try:
            mod = importlib.import_module(mod_name)
        except Exception:  # pragma: no cover
            logger.exception("Failed to import %s", mod_name)
            continue

        # Find the first BaseSkill subclass defined in this module.
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if (
                issubclass(cls, BaseSkill)
                and cls is not BaseSkill
                and cls is not PromptSkill
                and cls is not _FallbackSkill
                and cls.__module__ == mod_name
            ):
                instance = _instantiate(cls, entry)
                if instance is not None:
                    # Always key by the directory name for stable pipeline
                    # references, even when the SKILL.md front-matter declares
                    # a different display name.
                    key = entry.name
                    registry[key] = instance
                    logger.debug(
                        "Registered skill: %s (display=%s, v%s)",
                        key, instance.meta.name, instance.meta.version,
                    )
                break
        else:
            logger.warning("No BaseSkill subclass found in %s", mod_name)

    return registry


# Eagerly populate a module-level registry so that ``from mathmod_pilot.skills
# import SKILLS`` works out of the box.
SKILLS: dict[str, BaseSkill] = discover_skills()


def get_skill(name: str) -> BaseSkill | None:
    """Convenience accessor for the module-level registry."""
    return SKILLS.get(name)


def list_skills() -> list[str]:
    """Return a sorted list of registered skill names."""
    return sorted(SKILLS.keys())


__all__ = [
    "BaseSkill",
    "PromptSkill",
    "SkillMeta",
    "SKILLS",
    "discover_skills",
    "get_skill",
    "list_skills",
]
