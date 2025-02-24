import matplotlib.pyplot as plt
import numpy as np
import time
import streamlit as st

def simulate_mechanism(mechanism, scale):
    placeholder = st.empty()  # Erstelle einen Platzhalter für die Aktualisierung des Plots

    fig, ax = plt.subplots()
    ax.set_xlim(-scale, scale)
    ax.set_ylim(-scale, scale)
    
    for _ in range(100):  # 100 Frames für die Animation
        mechanism.theta += mechanism.speed  # Drehwinkel von Gelenk 2 aktualisieren
        mechanism.joints[2] = mechanism.compute_gelenk_2()  # Neue Position für Gelenk 2
        optimized_joints = mechanism.optimize_joints()  # Gelenke optimieren
        
        if optimized_joints:
            ax.clear()
            ax.set_xlim(-scale, scale)
            ax.set_ylim(-scale, scale)
            ax.set_title("Viergelenk-Mechanismus Simulation")

            # Zeichne Stäbe
            for (j1, j2) in mechanism.rods:
                p1, p2 = mechanism.joints[j1], mechanism.joints[j2]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'bo-', markersize=5, linewidth=2)
            
            # Zeichne Gelenke
            for joint in mechanism.joints.values():
                ax.scatter(joint[0], joint[1], color='r', zorder=3, s=50)
            
            placeholder.pyplot(fig)  # Zeichne das aktualisierte Bild in den Platzhalter
            time.sleep(0.05)  # Kurze Pause für die Animation
