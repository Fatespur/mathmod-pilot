"""Submission Governance Skill."""
from mathmod_pilot.skills.base import PromptSkill

class SubmissionGovernanceSkill(PromptSkill):
    skill_name = "submission-governance"
    skill_stage = "S7"
    skill_version = "1.0.0"
    skill_tier = 1
