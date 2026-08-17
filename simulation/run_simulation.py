"""
Run SafeSense 3D deterministic validation scenarios.
"""

import csv
from pathlib import Path

from safety_engine import SafetyEngine


OUTPUT = Path("results/validation/safesense_validation.csv")


SCENARIOS = [
    {
        "name": "Clear / high confidence",
        "confidence": 0.95,
        "distance": 2.75,
        "relative_speed": 1.00,
    },
    {
        "name": "Approach / high confidence",
        "confidence": 0.92,
        "distance": 2.00,
        "relative_speed": 1.00,
    },
    {
        "name": "Critical approach",
        "confidence": 0.90,
        "distance": 1.30,
        "relative_speed": 1.00,
    },
    {
        "name": "Occlusion / low confidence",
        "confidence": 0.55,
        "distance": 1.65,
        "relative_speed": 1.30,
    },
    {
        "name": "Conflicting sensors",
        "confidence": 0.35,
        "distance": 1.25,
        "relative_speed": 1.40,
    },
    {
        "name": "Imminent hazard",
        "confidence": 0.85,
        "distance": 0.82,
        "relative_speed": 1.40,
    },
]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    engine = SafetyEngine()

    fields = [
        "scenario",
        "confidence",
        "distance_m",
        "relative_speed_mps",
        "stopping_distance_m",
        "reaction_distance_m",
        "uncertainty_margin_m",
        "safe_distance_m",
        "ttc_s",
        "state",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for scenario in SCENARIOS:
            result = engine.evaluate(
                distance=scenario["distance"],
                relative_speed=scenario["relative_speed"],
                confidence=scenario["confidence"],
            )

            writer.writerow({
                "scenario": scenario["name"],
                "confidence": f"{result.confidence:.2f}",
                "distance_m": f"{result.distance:.2f}",
                "relative_speed_mps": f"{result.relative_speed:.2f}",
                "stopping_distance_m": f"{result.stopping_distance:.2f}",
                "reaction_distance_m": f"{result.reaction_distance:.2f}",
                "uncertainty_margin_m": f"{result.uncertainty_margin:.2f}",
                "safe_distance_m": f"{result.safe_distance:.2f}",
                "ttc_s": (
                    "inf"
                    if result.ttc == float("inf")
                    else f"{result.ttc:.2f}"
                ),
                "state": result.state,
            })

            print(
                f"{scenario['name']:28} "
                f"confidence={result.confidence:.2f}  "
                f"d={result.distance:.2f} m  "
                f"TTC={result.ttc:.2f} s  "
                f"d_safe={result.safe_distance:.2f} m  "
                f"STATE={result.state}"
            )

    print(f"\nSaved validation results to: {OUTPUT}")


if __name__ == "__main__":
    main()
