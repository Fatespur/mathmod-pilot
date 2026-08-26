"""CUMCM S0-S7 Pipeline Skill."""
from mathmod_pilot.skills.base import PromptSkill

class CUMCMPipelineSkill(PromptSkill):
    skill_name = "cumcm-pipeline"
    skill_stage = "S0-S7"
    skill_version = "3.1.0"
    skill_tier = 1
