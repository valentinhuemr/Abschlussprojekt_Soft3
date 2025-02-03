import numpy as np
from scipy.optimize import least_squares

class Solver:
    def __init__(self, mechanism):
        self.mechanism = mechanism
        self.fixed_positions = {
            i: tuple(pos) for i, pos in enumerate(mechanism.joints) if i in mechanism.fixed_joints
        }
        self.stab_definitions = mechanism.stab_definitions  # Stäbe aus Mechanismus übernehmen
        self.initial_lengths = self.compute_initial_lengths()

    def compute_initial_lengths(self):
        """ Berechnet die initialen Längen der vom Nutzer definierten Stäbe """
        lengths = {}
        for (i, j) in self.stab_definitions:
            lengths[(i, j)] = np.linalg.norm(np.array(self.mechanism.joints[i]) - np.array(self.mechanism.joints[j]))
        return lengths

    def constraint_equations(self, vars, theta):
        """ Stellt sicher, dass alle Stäbe konstant bleiben """
        joints = vars.reshape(-1, 2)  # Umformen in (N, 2) für N Gelenkpunkte
        constraints = []

        # **Fixierte Gelenke dürfen sich NICHT bewegen**
        for index, pos in self.fixed_positions.items():
            constraints.append(joints[index][0] - pos[0])  # X-Koordinate bleibt gleich
            constraints.append(joints[index][1] - pos[1])  # Y-Koordinate bleibt gleich

        # **Rotierendes Gelenk bewegt sich auf der Kreisbahn**
        rotating_joint_index = self.mechanism.rotating_joint
        x_c, y_c = self.fixed_positions[rotating_joint_index]  # Mittelpunkt der Rotation
        x_r, y_r = joints[rotating_joint_index]  # Aktuelle Position
        constraints.append(np.hypot(x_r - x_c, y_r - y_c) - self.mechanism.radius)  # Muss auf Kreisbahn liegen

        # **Alle definierten Stäbe müssen konstante Länge haben**
        for (i, j), original_length in self.initial_lengths.items():
            x_i, y_i = joints[i]
            x_j, y_j = joints[j]
            constraints.append(np.hypot(x_i - x_j, y_i - y_j) - original_length)  # Abstand bleibt konstant

        return constraints

    def run_simulation(self, theta_start=0, theta_end=360, step_size=1):
        """ Führt die Simulation aus, indem die Nebenbedingungen für konstante Stablängen eingehalten werden """
        theta_values = np.arange(theta_start, theta_end + step_size, step_size)
        simulation_results = []

        for theta in theta_values:
            initial_guess = np.array(self.mechanism.joints).flatten()  # Startwerte als 1D-Array

            # Nicht-lineare Optimierung zur Anpassung der Gelenkpositionen
            result = least_squares(
                self.constraint_equations, initial_guess, args=(theta,), method='lm'  # Levenberg-Marquardt für Stabilität
            )

            if result.success:
                joints_reshaped = result.x.reshape(-1, 2)  # Zurück in (N,2)-Form
                simulation_results.append(joints_reshaped.tolist())
            else:
                print(f"⚠️ Warnung: Keine Lösung für θ={theta} gefunden!")

        return theta_values, np.array(simulation_results)
