"""Abstract base class and utilities for all MathMod-Pilot skills.

Every skill lives in its own directory under ``src/scipilot/skills/`` and is
expected to contain:

* ``SKILL.md``  -- the native Trae skill definition / prompt (preserved as-is)
* ``skill.py``  -- the Python execution entry point subclassing ``BaseSkill``

The dynamic registry in ``mathmod_pilot.skills.__init__`` scans every sub-directory,
imports ``skill.py`` and instantiates the first ``BaseSkill`` subclass it finds.
"""
from __future__ import annotations

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]

    _HAS_YAML = True
except ImportError:  # pragma: no cover
    _HAS_YAML = False

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Metadata container
# ---------------------------------------------------------------------------
@dataclass
class SkillMeta:
    """Structured metadata parsed from a skill's ``SKILL.md`` front-matter."""

    name: str = ""
    description: str = ""
    version: str = "0.1.0"
    stage: str = ""
    tier: int = 3


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------
class BaseSkill(ABC):
    """Abstract base for every MathMod-Pilot agent skill.

    Subclasses **must** implement :meth:`execute`.  They may also override the
    class-level attributes ``skill_name``, ``skill_stage``, ``skill_version``
    and ``skill_tier`` to provide static metadata that is merged with whatever
    is declared in the ``SKILL.md`` YAML front-matter.
    """

    # --- static metadata (can be overridden by subclasses) ---
    skill_name: str = ""
    skill_stage: str = ""
    skill_version: str = "0.1.0"
    skill_tier: int = 3

    # ------------------------------------------------------------------
    # construction
    # ------------------------------------------------------------------
    def __init__(self, skill_dir: Path | str | None = None) -> None:
        if skill_dir is None:
            skill_dir = self._infer_skill_dir()
        self.skill_dir: Path = Path(skill_dir)
        self._skill_md_path: Path = self.skill_dir / "SKILL.md"
        self.logger: logging.Logger = logging.getLogger(
            f"mathmod_pilot.skills.{self.skill_name or self.__class__.__name__.lower()}"
        )
        self.meta: SkillMeta = self._load_meta()

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _infer_skill_dir(self) -> Path:
        """Derive the skill directory from the subclass's module file."""
        module = sys.modules.get(self.__class__.__module__)
        if module is not None and getattr(module, "__file__", None):
            return Path(module.__file__).resolve().parent  # type: ignore[arg-type]
        return Path.cwd()

    def _load_meta(self) -> SkillMeta:
        """Parse ``SKILL.md`` YAML front-matter and merge with class attributes."""
        name = self.skill_name or self.skill_dir.name
        description = ""
        version = self.skill_version
        if self._skill_md_path.exists():
            text = self._skill_md_path.read_text(encoding="utf-8-sig")
            fm, _ = _split_frontmatter(text)
            if fm:
                data: dict[str, Any] = {}
                if _HAS_YAML:
                    try:
                        loaded = yaml.safe_load(fm)
                        if isinstance(loaded, dict):
                            data = loaded
                    except yaml.YAMLError:
                        logger.debug("YAML parse error in %s", self._skill_md_path)
                else:  # pragma: no cover
                    logger.debug("PyYAML not installed; front-matter parsing limited")
                name = str(data.get("name", name))
                description = str(data.get("description", ""))
                version = str(data.get("version", version))
        return SkillMeta(
            name=name,
            description=description,
            version=version,
            stage=self.skill_stage,
            tier=self.skill_tier,
        )

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    @property
    def prompt(self) -> str:
        """Return the full ``SKILL.md`` content (the skill's prompt)."""
        if self._skill_md_path.exists():
            return self._skill_md_path.read_text(encoding="utf-8-sig")
        return ""

    def get_prompt(self) -> str:
        """Public accessor for :attr:`prompt`."""
        return self.prompt

    @abstractmethod
    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Run the skill.

        Parameters
        ----------
        inputs:
            A dictionary of contextual data handed in by the caller or the
            previous pipeline stage.

        Returns
        -------
        dict
            A structured result dictionary.  At minimum it should contain a
            ``"status"`` key.
        """
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<{self.__class__.__name__} name={self.meta.name!r} "
            f"stage={self.meta.stage!r} v{self.meta.version}>"
        )


# ---------------------------------------------------------------------------
# PromptSkill -- convenience base for prompt-only skills
# ---------------------------------------------------------------------------
class PromptSkill(BaseSkill):
    """Base class for skills whose primary asset is the ``SKILL.md`` prompt.

    Skills that do not ship executable Python logic (the majority of the
    MathMod-Pilot suite) inherit from :class:`PromptSkill` and only need to set the
    class-level metadata attributes.  :meth:`execute` returns the prompt text
    together with a readiness signal so the agent can forward it to an LLM.
    """

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return {
            "skill": self.meta.name,
            "stage": self.meta.stage,
            "version": self.meta.version,
            "tier": self.meta.tier,
            "prompt": self.get_prompt(),
            "inputs": inputs,
            "status": "ready",
        }


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------
def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split a Markdown file into ``(frontmatter, body)`` if present."""
    if text.startswith("---"):
        # find the closing delimiter
        end = text.find("\n---", 3)
        if end != -1:
            frontmatter = text[3:end].lstrip("\n")
            body = text[end + 4 :].lstrip("\n")
            return frontmatter, body
    return "", text
