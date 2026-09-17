# SIMULATION_QUEUE_DES_ABM selection contract v2

Eligible structure: stochastic event/resource interactions, queues, non-closed-form dynamics, or agent rules whose emergent system outcome is the target. Separate analytical queue, DES, Monte Carlo and ABM.

- M/M/c requires supported Poisson arrivals, exponential service, independence, stationarity, identical parallel servers and declared capacity/discipline. Heavy tails or time-varying arrivals reject or downgrade it toward G/G/c approximation, empirical replay or DES.
- DES requires event logic, resources, clocks, warm-up/termination and replication budget. ABM additionally requires behavior rules and calibration evidence; uncalibrated rules cannot support strong claims.
- Baselines: analytical approximation where defensible; empirical replay; deterministic mean-input scenario; simpler queue.
- Alternatives: direct statistical model, dynamic/state-space, optimization.
- Failure modes: no warm-up, too few replications, hidden seed, unstable mean/tails, invalid event ordering, uncalibrated agent rules, horizon truncation.
- Replacement triggers: closed form adequate; distributional tests invalidate queue assumptions; calibration fails; conclusions reverse across seeds/horizons.

