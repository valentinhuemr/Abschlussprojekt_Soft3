import numpy as np

def calculate_positions(joints, rotating_joint, radius, theta):
    """Berechnet die Positionen aller Gelenke bei einem bestimmten Winkel θ."""
    new_positions = joints.copy()
    if rotating_joint is not None and radius is not None:
        cx, cy = joints[rotating_joint]
        new_x = cx + radius * np.cos(np.radians(theta))
        new_y = cy + radius * np.sin(np.radians(theta))
        new_positions[rotating_joint] = (new_x, new_y)
    return new_positions

def simulate_mechanism(mechanism, theta_start, theta_end, step_size):
    """Simuliert den Mechanismus für verschiedene Winkelpositionen."""
    theta_values = np.arange(theta_start, theta_end + step_size, step_size)
    simulation_data = [
        calculate_positions(mechanism.joints, mechanism.rotating_joint, mechanism.radius, theta)
        for theta in theta_values
    ]
    return theta_values, simulation_data
