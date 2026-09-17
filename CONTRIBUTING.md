# Contributing to CUMCM Modeling Skills Toolkit

Thank you for your interest in contributing to the **CUMCM Modeling Skills Toolkit**! This project provides an agent-native, standardized toolkit for mathematical modeling competitions (CUMCM, MCM/ICM).

## Code of Conduct

We are committed to providing a friendly, rigorous, and respectful environment for all participants.

## Workflow Principles

All skills in this repository follow strict architectural principles:
1. **Mathematical Rigor**: Every model must have clear mathematical assumptions, explicit variables/units, and objective equations. Keyword-based template matching without physical grounding is prohibited.
2. **Deterministic Artifact Contracts**: Each skill declares structured inputs and outputs (`inputs` and `outputs` in YAML frontmatter and `registry/skills.json`).
3. **Decoupled Execution**: All scripts must support CLI invocation without hardcoded machine paths.
4. **Anonymity & Privacy**: Never commit private contest submission IDs, sensitive author names, real student IDs, or competition unreleased datasets.

## How to Add or Improve a Skill

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/new-skill-name
   ```
2. Follow the standardized directory structure:
   ```text
   skills/<category>/<skill-name>/
   ├── SKILL.md         # Agent-executable instructions, decision rules & methods
   ├── README.md        # Human-readable guide and explanations
   ├── scripts/         # Local CLI tools and algorithms (if applicable)
   └── references/      # Schemas, formula derivations, cheat sheets
   ```
3. Update `registry/skills.json` and `registry/workflow.json` to register the new skill.
4. Test all CLI scripts and verify that `npm run build` passes for the website.
5. Submit a Pull Request with clear documentation and tests.
