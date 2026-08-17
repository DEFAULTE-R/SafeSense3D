"""
SafeSense 3D safety decision engine.

Core model:
    d_stop = v^2 / (2a)
    d_reaction = v * t_delay
    d_uncertainty = k * (1 - confidence)
    d_safe = d_stop + d_reaction + d_uncertainty

The engine is a supervisory simulation component.
It is NOT a certified industrial safety controller.
"""

from dataclasses import dataclass
from math import inf


@dataclass
class SafetyResult:
    distance: float
    relative_speed: float
    confidence: float
    stopping_distance: float
    reaction_distance: float
    uncertainty_margin: float
    safe_distance: float
    ttc: float
    state: str


class SafetyEngine:
    def __init__(
        self,
        machine_speed: float = 1.5,
        deceleration: float = 1.4,
        reaction_delay: float = 0.20,
        uncertainty_gain: float = 0.80,
    ):
        self.machine_speed = machine_speed
        self.deceleration = deceleration
        self.reaction_delay = reaction_delay
        self.uncertainty_gain = uncertainty_gain

    def stopping_distance(self, speed: float | None = None) -> float:
        v = self.machine_speed if speed is None else speed

        if v <= 0:
            return 0.0

        return (v ** 2) / (2 * self.deceleration)

    def reaction_distance(self, speed: float | None = None) -> float:
        v = self.machine_speed if speed is None else speed
        return v * self.reaction_delay

    def uncertainty_margin(self, confidence: float) -> float:
        confidence = max(0.0, min(1.0, confidence))
        return self.uncertainty_gain * (1.0 - confidence)

    def time_to_collision(
        self,
        distance: float,
        relative_speed: float,
    ) -> float:
        if relative_speed <= 0:
            return inf

        return distance / relative_speed

    def classify(
        self,
        distance: float,
        ttc: float,
        safe_distance: float,
    ) -> str:

        stopping_floor = self.stopping_distance()

        if distance <= stopping_floor + 0.05 or ttc <= 0.60:
            return "E-STOP"

        if distance <= safe_distance or ttc <= 1.20:
            return "BRAKE"

        if distance <= safe_distance + 0.80 or ttc <= 2.20:
            return "WARNING"

        return "NORMAL"

    def evaluate(
        self,
        distance: float,
        relative_speed: float,
        confidence: float,
    ) -> SafetyResult:

        d_stop = self.stopping_distance()
        d_reaction = self.reaction_distance()
        d_uncertainty = self.uncertainty_margin(confidence)

        d_safe = d_stop + d_reaction + d_uncertainty

        ttc = self.time_to_collision(
            distance,
            relative_speed,
        )

        state = self.classify(
            distance,
            ttc,
            d_safe,
        )

        return SafetyResult(
            distance=distance,
            relative_speed=relative_speed,
            confidence=confidence,
            stopping_distance=d_stop,
            reaction_distance=d_reaction,
            uncertainty_margin=d_uncertainty,
            safe_distance=d_safe,
            ttc=ttc,
            state=state,
        )
