"""MathMod-Pilot Quickstart — load skills, inspect metadata, and run the pipeline.

Run:
    python examples/quickstart.py
"""
from __future__ import annotations

from mathmod_pilot.core import MathModPilotAgent, PIPELINE


def main() -> None:
    agent = MathModPilotAgent()

    # --- list all skills ---
    print("=" * 60)
    print(f"Discovered {len(agent.list_skills())} skills:")
    print("=" * 60)
    for info in agent.skill_info():
        print(
            f"  [{info['stage']:>3s}]  Tier {info['tier']}  "
            f"{info['name']:25s}  v{info['version']}"
        )

    # --- load a single skill's prompt ---
    print("\n" + "=" * 60)
    print("Loading problem-analyzer prompt (first 300 chars):")
    print("=" * 60)
    result = agent.run_skill("problem-analyzer", {"problem_text": "demo"})
    print(result["prompt"][:300])

    # --- run the core pipeline (prompt-only mode) ---
    print("\n" + "=" * 60)
    print("Running pipeline S0 -> S7 (prompt dispatch):")
    print("=" * 60)
    results = agent.run_pipeline({"problem_text": "demo problem"})
    for name, output in results.items():
        print(f"  {name:25s} -> {output.get('status', 'n/a')}")


if __name__ == "__main__":
    main()
