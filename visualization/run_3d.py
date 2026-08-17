"""
SafeSense 3D — 3D Digital Safety Twin Prototype

Visualizes:
- Automated machine
- Human/obstacle
- Virtual LiDAR rays
- Adaptive safety envelope
- Planned trajectory
- Risk state
- Stopping-distance floor
- Uncertainty-aware safety margin

This is a visualization prototype, not a certified industrial safety controller.
"""

from pathlib import Path
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Import the safety engine
from simulation.safety_engine import SafetyEngine, SafetyResult


def evaluate_scenario(distance, relative_speed, confidence):
    """Evaluate a safety scenario using the SafetyEngine."""
    # Create engine with default parameters
    engine = SafetyEngine()
    
    # Evaluate the scenario - adjust method call based on your actual implementation
    return engine.evaluate(
        distance=distance,
        relative_speed=relative_speed,
        confidence=confidence
    )


def create_box(center, size):
    """Create box vertices for 3D visualization."""
    x, y, z = center
    dx, dy, dz = size
    
    vertices = [
        [x - dx/2, y - dy/2, z - dz/2],
        [x + dx/2, y - dy/2, z - dz/2],
        [x + dx/2, y + dy/2, z - dz/2],
        [x - dx/2, y + dy/2, z - dz/2],
        [x - dx/2, y - dy/2, z + dz/2],
        [x + dx/2, y - dy/2, z + dz/2],
        [x + dx/2, y + dy/2, z + dz/2],
        [x - dx/2, y + dy/2, z + dz/2]
    ]
    
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # Top
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # Front
        [vertices[3], vertices[2], vertices[6], vertices[7]],  # Back
        [vertices[0], vertices[3], vertices[7], vertices[4]],  # Left
        [vertices[1], vertices[2], vertices[6], vertices[5]]   # Right
    ]
    
    return faces


def visualize_scenario(scenario_name, scenario_data):
    """Create 3D visualization for a single scenario."""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Evaluate safety
    result = evaluate_scenario(
        scenario_data['distance'],
        scenario_data['relative_speed'],
        scenario_data['confidence']
    )
    
    # Set axis limits
    max_dist = max(3.0, result.safe_distance * 1.5)
    ax.set_xlim([-0.5, max_dist])
    ax.set_ylim([-2, 2])
    ax.set_zlim([0, 3])
    
    # Draw machine (box)
    machine_faces = create_box(center=(0, 0, 0.6), size=(0.8, 0.6, 1.2))
    machine = Poly3DCollection(machine_faces, alpha=0.7, facecolor='blue', edgecolor='darkblue')
    ax.add_collection3d(machine)
    
    # Draw person/obstacle (simplified as cylinder)
    person_x, person_y, person_z = scenario_data['distance'], 0, 0
    theta = np.linspace(0, 2*np.pi, 20)
    radius = 0.2
    height = 1.7
    
    x_circle = person_x + radius * np.cos(theta)
    y_circle = person_y + radius * np.sin(theta)
    
    for i in range(len(theta)):
        ax.plot(
            [x_circle[i], x_circle[i]],
            [y_circle[i], y_circle[i]],
            [0, height],
            color='red', linewidth=2, alpha=0.8
        )
    
    # Draw LiDAR rays
    n_rays = 15
    ray_angles = np.linspace(-0.5, 0.5, n_rays)
    for angle in ray_angles:
        end_x = scenario_data['distance'] * 1.2 * np.cos(angle)
        end_y = scenario_data['distance'] * 1.2 * np.sin(angle)
        ax.plot([0, end_x], [0, end_y], [0.6, 0.6], 
                color='green', alpha=0.3, linewidth=0.5)
    
    # Draw safety envelope (semi-transparent sphere)
    r = result.safe_distance
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 30)
    x_sphere = r * np.outer(np.cos(u), np.sin(v))
    y_sphere = r * np.outer(np.sin(u), np.sin(v))
    z_sphere = r * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x_sphere, y_sphere, z_sphere + 0.6, 
                    alpha=0.1, color='yellow')
    
    # Draw distance indicators
    ax.plot([0, result.stopping_distance], [0, 0], [0.3, 0.3], 
            color='orange', linewidth=3, label=f'Stopping: {result.stopping_distance:.2f}m')
    ax.plot([0, result.reaction_distance], [0, 0.3], [0.3, 0.3], 
            color='purple', linewidth=3, label=f'Reaction: {result.reaction_distance:.2f}m')
    ax.plot([0, result.uncertainty_margin], [0, -0.3], [0.3, 0.3], 
            color='red', linewidth=3, label=f'Uncertainty: {result.uncertainty_margin:.2f}m')
    
    # Set labels
    ax.set_xlabel('X (m) - Direction of Motion')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    
    # Color code the state
    state_colors = {
        "NORMAL": "green",
        "WARNING": "yellow",
        "BRAKE": "orange",
        "E-STOP": "red"
    }
    state_color = state_colors.get(result.state, "gray")
    
    # Add title
    ax.set_title(
        f'SafeSense 3D Digital Twin\n'
        f'{scenario_name} - State: {result.state}',
        color=state_color, fontweight='bold', fontsize=14
    )
    
    # Add info box
    info_text = (
        f'Distance: {scenario_data["distance"]:.2f}m\n'
        f'Confidence: {scenario_data["confidence"]:.2%}\n'
        f'Safe Distance: {result.safe_distance:.2f}m\n'
        f'TTC: {result.ttc:.2f}s'
    )
    ax.text2D(0.02, 0.95, info_text, transform=ax.transAxes, 
              fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.legend(loc='upper right')
    
    # Add safety disclaimer
    fig.text(0.02, 0.02, 
             "Safety Notice: This is a simulation/visualization prototype.\n"
             "It is NOT a certified industrial safety controller.",
             fontsize=8, style='italic', color='gray')
    
    # Set view angle
    ax.view_init(elev=25, azim=45)
    
    return fig


def main():
    """Main visualization function."""
    print("SafeSense 3D Visualization")
    print("-" * 40)
    
    # Define scenarios
    scenarios = {
        "Clear / high confidence": {
            "distance": 2.75, "confidence": 0.95, "relative_speed": 1.0
        },
        "Approach / high confidence": {
            "distance": 2.0, "confidence": 0.92, "relative_speed": 1.0
        },
        "Critical approach": {
            "distance": 1.3, "confidence": 0.90, "relative_speed": 1.0
        },
        "Occlusion / low confidence": {
            "distance": 1.65, "confidence": 0.55, "relative_speed": 1.3
        },
        "Conflicting sensors": {
            "distance": 1.25, "confidence": 0.35, "relative_speed": 1.4
        },
        "Imminent hazard": {
            "distance": 0.82, "confidence": 0.85, "relative_speed": 1.4
        }
    }
    
    # Create figures directory
    figures_dir = ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    # Visualize each scenario
    for i, (name, data) in enumerate(scenarios.items(), 1):
        print(f"\n[{i}/{len(scenarios)}] Visualizing: {name}")
        fig = visualize_scenario(name, data)
        
        # Save figure
        output_file = figures_dir / f"safesense_3d_{i:02d}.png"
        fig.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"  Saved: {output_file}")
        
        # Show interactive plot
        plt.show()
        plt.close(fig)
    
    print("\n✅ All visualizations complete!")
    print(f"📁 Figures saved to: {figures_dir}")


if __name__ == "__main__":
    main()
