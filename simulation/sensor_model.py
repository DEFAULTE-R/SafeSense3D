"""
Simplified virtual sensor model for SafeSense 3D.

This is a simulation abstraction, not a physical LiDAR or thermal-camera driver.
"""

from dataclasses import dataclass


@dataclass
class SensorObservation:
    distance: float
    confidence: float
    occluded: bool
    thermal_confirmation: bool


class VirtualSensor:
    def observe(
        self,
        distance: float,
        confidence: float = 0.95,
        occluded: bool = False,
        thermal_confirmation: bool = True,
    ) -> SensorObservation:

        confidence = max(0.0, min(1.0, confidence))

        if occluded:
            confidence *= 0.60

        if thermal_confirmation:
            confidence = min(1.0, confidence + 0.05)

        return SensorObservation(
            distance=distance,
            confidence=confidence,
            occluded=occluded,
            thermal_confirmation=thermal_confirmation,
        )
