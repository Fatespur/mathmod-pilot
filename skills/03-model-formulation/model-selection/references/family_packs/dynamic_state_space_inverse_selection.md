# DYNAMIC_STATE_SPACE_INVERSE selection contract v2

Eligible structure: evolving latent state, defensible transition/observation equations, mechanism parameters inferred from indirect/noisy observations, or state reconstruction/control. Separate forward dynamics, state estimation and inverse parameter inference. An ordinary univariate trend without latent-state or mechanism basis is not enough for Kalman/state-space routing.

- Preconditions: time scale, state/observation distinction, inputs, initial/boundary conditions, measurement model, purpose (`PREDICTION_ONLY`, `STATE_RECONSTRUCTION`, `PARAMETER_INFERENCE`, `MECHANISM_INTERPRETATION`), and preliminary structural identifiability/observability screen.
- Baselines: persistence/simple trend for prediction; reduced mechanism/constant-rate; direct observation or simple smoother for state estimation.
- Candidates: ODE/PDE forward model, linear/nonlinear state-space/filter/smoother, constrained inverse estimation, Bayesian/data-assimilation route.
- Alternatives: time series, statistical regression, simulation.
- Failure modes: non-identifiability, non-observability, parameter compensation, discretization error, wrong measurement model, initial-condition sensitivity.
- Replacement triggers: latent state unnecessary; required claims non-identifiable; stable prediction but unstable parameters forces claim restriction; residual dynamics contradict mechanism.

