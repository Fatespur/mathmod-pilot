"""Basic unit tests for the MathMod-Pilot skill registry and agent."""
from __future__ import annotations

import pytest

from mathmod_pilot.core import MathModPilotAgent, PIPELINE
from mathmod_pilot.skills import SKILLS, discover_skills, get_skill, list_skills
from mathmod_pilot.skills.base import BaseSkill, PromptSkill, SkillMeta


# ---------------------------------------------------------------------------
# expected skill set
# ---------------------------------------------------------------------------
EXPECTED_SKILLS = {
    "brainstorming",
    "problem-analyzer",
    "data-processing",
    "mle-solver",
    "model-validation",
    "scipilot-figure",
    "scipilot-figure-skill",
    "mcm-paper-writing",
    "paper-review",
    "diagram-generator",
    "matlab-figure",
    "nature-figure",
    "winning-paper-analysis",
    "reference-manager",
    "systematic-debugging",
}


# ---------------------------------------------------------------------------
# registry tests
# ---------------------------------------------------------------------------
class TestSkillRegistry:
    def test_all_15_skills_discovered(self) -> None:
        discovered = set(list_skills())
        missing = EXPECTED_SKILLS - discovered
        assert not missing, f"Missing skills: {missing}"

    def test_registry_count(self) -> None:
        assert len(SKILLS) >= 15

    def test_get_skill_returns_instance(self) -> None:
        skill = get_skill("brainstorming")
        assert skill is not None
        assert isinstance(skill, BaseSkill)

    def test_get_skill_unknown_returns_none(self) -> None:
        assert get_skill("nonexistent-skill") is None

    def test_rediscover_returns_same_keys(self) -> None:
        fresh = discover_skills()
        assert set(fresh.keys()) == set(SKILLS.keys())


# ---------------------------------------------------------------------------
# BaseSkill contract tests
# ---------------------------------------------------------------------------
class TestBaseSkillContract:
    def test_every_skill_has_prompt(self) -> None:
        for name, skill in SKILLS.items():
            assert skill.get_prompt(), f"Skill '{name}' has empty prompt"

    def test_every_skill_has_meta(self) -> None:
        for name, skill in SKILLS.items():
            assert isinstance(skill.meta, SkillMeta)
            assert skill.meta.name, f"Skill '{name}' has empty meta.name"

    def test_every_skill_execute_returns_dict(self) -> None:
        for name, skill in SKILLS.items():
            result = skill.execute({"test": True})
            assert isinstance(result, dict), f"Skill '{name}' execute() did not return dict"
            assert "status" in result, f"Skill '{name}' result missing 'status'"

    def test_cannot_instantiate_abstract_base(self) -> None:
        with pytest.raises(TypeError):
            BaseSkill()  # type: ignore[abstract]

    def test_promptskill_is_concrete(self) -> None:
        # PromptSkill provides execute(), so it should be instantiable
        # (though it needs a skill_dir)
        assert issubclass(PromptSkill, BaseSkill)


# ---------------------------------------------------------------------------
# agent tests
# ---------------------------------------------------------------------------
class TestMathModPilotAgent:
    def test_agent_loads_skills(self) -> None:
        agent = MathModPilotAgent()
        assert len(agent.list_skills()) >= 15

    def test_agent_get_skill(self) -> None:
        agent = MathModPilotAgent()
        skill = agent.get_skill("mle-solver")
        assert skill is not None
        assert skill.meta.stage == "S3"

    def test_agent_run_skill(self) -> None:
        agent = MathModPilotAgent()
        result = agent.run_skill("brainstorming", {"topic": "test"})
        assert result["status"] == "ready"
        assert "prompt" in result

    def test_agent_run_skill_unknown_raises(self) -> None:
        agent = MathModPilotAgent()
        with pytest.raises(KeyError):
            agent.run_skill("does-not-exist", {})

    def test_pipeline_runs_all_stages(self) -> None:
        agent = MathModPilotAgent()
        results = agent.run_pipeline({"problem_text": "demo"})
        for name in PIPELINE:
            assert name in results, f"Pipeline skill '{name}' not in results"

    def test_skill_info_returns_list(self) -> None:
        agent = MathModPilotAgent()
        info = agent.skill_info()
        assert isinstance(info, list)
        assert len(info) >= 15
        for entry in info:
            assert "name" in entry
            assert "stage" in entry
            assert "version" in entry
            assert "tier" in entry


# ---------------------------------------------------------------------------
# mle-solver heuristic extension test
# ---------------------------------------------------------------------------
class TestMleSolverExtension:
    def test_heuristic_available(self) -> None:
        skill = get_skill("mle-solver")
        assert skill is not None
        ext = skill._get_heuristic()  # type: ignore[attr-defined]
        # The extension requires numpy; skip if not installed
        if ext is None:
            pytest.skip("numpy not installed")
        assert hasattr(ext, "solve_optimization")
        assert hasattr(ext, "genetic_algorithm")
