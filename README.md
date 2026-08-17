# SafeSense 3D

### Adaptive, Uncertainty-Aware Digital Safety Twin for Automated Machinery

> **Sense → Estimate → Adapt → Decide → Act**

SafeSense 3D is a simulation-first safety architecture for automated machinery that dynamically determines the required protective envelope based on machine motion, hazard proximity, and sensor confidence.

Developed for **National Student Hack-A-Stage 2026** — Track 01: Algorithmic Safety & Hazard Mitigation in Automated Systems.
Team: Robo Rebels

---

## Problem

Automated machinery commonly relies on predefined safety zones and threshold-based responses. A fixed safety zone does not account for:

- Machine velocity
- Stopping distance
- Reaction delay
- Sensor uncertainty
- Occlusion
- Conflicting sensor observations

The core question: **how much safety space does the machine need right now?**

---

## Approach

SafeSense answers this continuously by combining machine dynamics with sensor confidence, following a five-stage pipeline:

1. **Sense** — virtual LiDAR + thermal observation
2. **Estimate** — distance, velocity, and confidence
3. **Adapt** — stopping distance + uncertainty margin
4. **Decide** — risk classification via TTC
5. **Act** — slow / brake / E-stop

**Safety principle:** uncertainty can expand the protective envelope, but it can never reduce the deterministic safety floor.

---

## Core Model

d_safe = d_stop + d_reaction + d_uncertainty

- `d_stop = v² / (2a)` — required stopping distance
- `d_reaction = v × t_delay` — sensing, computation, and actuation delay
- `d_uncertainty = f(confidence)` — lower confidence increases the protective margin

Risk states are classified using distance, time-to-collision (TTC), and the adaptive safety envelope: **NORMAL → WARNING → BRAKE → E-STOP**.

---



## Running the Simulation

```bash
pip install -r requirements.txt
python3 simulation/run_simulation.py
```

This runs six deterministic validation scenarios and writes results to `results/validation/safesense_validation.csv`.

---

## Validation Results

| Scenario | Confidence | Distance (m) | TTC (s) | d_safe (m) | State |
|---|---|---|---|---|---|
| Clear / high confidence | 0.95 | 2.75 | 2.75 | 1.14 | NORMAL |
| Approach / high confidence | 0.92 | 2.00 | 2.00 | 1.17 | WARNING |
| Critical approach | 0.90 | 1.30 | 1.30 | 1.18 | WARNING |
| Occlusion / low confidence | 0.55 | 1.65 | 1.27 | 1.46 | WARNING |
| Conflicting sensors | 0.35 | 1.25 | 0.89 | 1.62 | BRAKE |
| Imminent hazard | 0.85 | 0.82 | 0.59 | 1.22 | E-STOP |

Lower confidence increases the uncertainty margin and therefore expands `d_safe`. All values above are outputs of the deterministic simulation model, not measurements from physical sensors.

---

## Safety Positioning

SafeSense 3D is a **supervisory decision-support layer**. It is not a certified industrial safety controller — certified hardwired / safety-PLC functions remain the final safety authority in any real deployment.

---

## Roadmap

- Calibrate uncertainty models using real sensor data
- Validate against representative industrial robot/AGV scenarios
- Integrate with certified safety controllers under appropriate industrial standards
- Develop automated sensor-placement optimization for complex workspaces

---

## License

See the `LICENSE` file for licensing information.
