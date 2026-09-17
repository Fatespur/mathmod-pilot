# HYBRID_MODELING selection contract v2

Eligible only when distinct components address distinct, evidenced structures and their interfaces are defined. “Advanced”, ensemble popularity, or stacking models for its own sake is not eligibility. Specify component roles, input/output contracts, timing, train/deployment availability, uncertainty propagation and an ablation plan before selection.

- Baselines: best single component; simpler serial pipeline; point-estimate pipeline when testing uncertainty propagation.
- Candidates: prediction→optimization, mechanism+data residual, simulation→surrogate/optimization, ensemble only when diversity is measured.
- Reject: redundant components, leakage through interfaces, no test-set material gain, no ablation feasibility, uncertainty discarded before a decision.
- Alternatives: the strongest single component or simpler family.
- Failure modes: error amplification, interface mismatch, uncertainty collapse, unstable policy, redundant component, joint overfit.
- Replacement triggers: any component has no material ablation contribution; simpler model matches decision loss; interface distribution shifts; uncertainty changes policy.

