import matplotlib.pyplot as plt
import numpy as np
import time
import streamlit as st
import pandas as pd

def simulate_mechanism(mechanism, scale, return_trajectory=False):
    placeholder = st.empty()  # Platzhalter für Animation

    fig, ax = plt.subplots()
    ax.set_xlim(-scale, scale)
    ax.set_ylim(-scale, scale)
    ax.set_title("Viergelenk-Mechanismus Simulation")

    # Speicherung der Bahnkurven für Gelenke mit aktivierter Anzeige
    trajectory = {j: [] for j in mechanism.joints.keys() if mechanism.show_trajectory.get(j, False)}
    initial_theta = mechanism.theta  # Startwinkel speichern

    while mechanism.theta - initial_theta < 2 * np.pi:  # Solange bis eine volle Umdrehung erreicht ist
        mechanism.theta += mechanism.speed  # Winkel für Gelenk 2 aktualisieren
        mechanism.joints[2] = mechanism.compute_gelenk_2()  # Gelenk 2 Position berechnen
        optimized_joints = mechanism.optimize_joints()  # Optimierung der Gelenke

        if optimized_joints:
            ax.clear()
            ax.set_xlim(-scale, scale)
            ax.set_ylim(-scale, scale)
            ax.set_title("Viergelenk-Mechanismus Simulation")

            # Speichere Gelenkpositionen für aktivierte Bahnkurven
            for j, pos in mechanism.joints.items():
                if mechanism.show_trajectory.get(j, False):
                    trajectory[j].append(pos.copy())

            # Zeichne Stäbe
            for (j1, j2) in mechanism.rods:
                p1, p2 = mechanism.joints[j1], mechanism.joints[j2]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'bo-', markersize=5, linewidth=2)
            
            # Zeichne Gelenke
            for joint in mechanism.joints.values():
                ax.scatter(joint[0], joint[1], color='r', zorder=3, s=50)

            # Zeichne Bahnkurven
            for j, points in trajectory.items():
                if len(points) > 1:
                    points_np = np.array(points)
                    ax.plot(points_np[:, 0], points_np[:, 1], 'r-', alpha=0.8)  # Rote Linie für Trajektorie
            
            placeholder.pyplot(fig)  # Aktualisiere Streamlit-Grafik
            time.sleep(0.05)  # Simulationspause für Animation

    # Falls `return_trajectory` aktiviert ist, geben wir die Trajektorien-Daten zurück
    if return_trajectory:
        return trajectory