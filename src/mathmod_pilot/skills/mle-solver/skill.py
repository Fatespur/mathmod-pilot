"""
MathMod-Pilot Skill: mle-solver
--------------------------------------------------
Original Source / Inspiration: MathMod-Pilot Project (original work)
Repository: https://github.com/Fatespur/mathmod-pilot
License: MIT License

Author: Ye Jiahui (William)
Description: Original Python implementation. The Generate-Verify-Revise iterative
             architecture, the extensions/heuristic_algorithms.py module (GA/PSO/SA/DE
             optimisers), and the three-layer assertion-checking mechanism are all
             independent original developments based on national-level mathematical
             modelling competition experience.
--------------------------------------------------
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from mathmod_pilot.skills.base import BaseSkill

logger = logging.getLogger(__name__)


class MleSolverSkill(BaseSkill):
    """Entry point for the *mle-solver* skill (S3, v9.0.0).

    The solver follows a **Generate-Verify-Revise** iterative architecture:
    code is generated, executed, errors are captured, and the code is revised
    until all hard assertions (physical consistency, cross-validation,
    model-reality checks) pass.
    """

    skill_name = "mle-solver"
    skill_stage = "S3"
    skill_version = "9.0.0"
    skill_tier = 1

    def __init__(self, skill_dir: Path | str | None = None) -> None:
        super().__init__(skill_dir)
        # Make ``extensions/`` importable so heuristic algorithms can be
        # loaded on demand without polluting the top-level package namespace.
        ext_dir = self.skill_dir / "extensions"
        if ext_dir.is_dir() and str(ext_dir) not in sys.path:
            sys.path.insert(0, str(ext_dir))

    # ------------------------------------------------------------------
    # lazy access to heuristic optimisers
    # ------------------------------------------------------------------
    def _get_heuristic(self) -> Any:
        """Lazily import the heuristic-algorithms extension."""
        try:
            import heuristic_algorithms  # type: ignore[import-not-found]
            return heuristic_algorithms
        except ImportError:
            self.logger.warning("heuristic_algorithms extension not available")
            return None

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Dispatch the solver.

        The primary output is the ``SKILL.md`` prompt that an LLM agent uses
        to drive the Generate-Verify-Revise loop.  When ``inputs`` contains an
        ``"optimization"`` key the heuristic-algorithms extension is invoked
        directly to solve a numerical optimisation problem.
        """
        result: dict[str, Any] = {
            "skill": self.meta.name,
            "stage": self.meta.stage,
            "version": self.meta.version,
            "tier": self.meta.tier,
            "prompt": self.get_prompt(),
            "inputs": inputs,
            "status": "ready",
        }

        opt_request = inputs.get("optimization")
        if opt_request and isinstance(opt_request, dict):
            ext = self._get_heuristic()
            if ext is not None:
                try:
                    sol, val, history = ext.solve_optimization(
                        objective_func=opt_request["objective_func"],
                        bounds=opt_request["bounds"],
                        method=opt_request.get("method", "GA"),
                    )
                    result["optimization_result"] = {
                        "solution": list(sol),
                        "optimal_value": float(val),
                        "convergence_history": [float(v) for v in history],
                    }
                    result["status"] = "solved"
                except Exception as exc:  # pragma: no cover
                    self.logger.exception("Heuristic optimisation failed: %s", exc)
                    result["status"] = "optimization_error"
                    result["error"] = str(exc)

        return result
