import numpy as np
import time
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image


def simulate_mechanism(mechanism, plot_size_x=100, plot_size_y=100, return_trajectory=False, save_gif=False):
    # **Dynamische Plot-Größe basierend auf Benutzereingaben**
    placeholder = st.empty()  
    fig, ax = plt.subplots(figsize=(plot_size_x / 50, plot_size_y / 50))  # Dynamische Plot-Größe
    canvas = FigureCanvas(fig)  

    # **Achsen skalieren basierend auf Benutzerwerten**
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim([-plot_size_x / 2, plot_size_x / 2])
    ax.set_ylim([-plot_size_y / 2, plot_size_y / 2])

    # **Achsen-Ticks automatisch setzen für bessere Lesbarkeit**
    ax.set_xticks(np.linspace(-plot_size_x / 2, plot_size_x / 2, num=5))
    ax.set_yticks(np.linspace(-plot_size_y / 2, plot_size_y / 2, num=5))

    # **Plot-Beschriftungen und Gitternetz**
    ax.set_title(f"Simulation des Viergelenk-Mechanismus\nPlotgröße: X={plot_size_x}, Y={plot_size_y}", fontsize=12, fontweight="bold")
    ax.set_xlabel("X-Achse (mm)", fontsize=10)
    ax.set_ylabel("Y-Achse (mm)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.7)  

    # Speicher für Bahnkurven
    trajectory = {j: [] for j in mechanism.joints.keys() if mechanism.show_trajectory.get(j, False)}
    initial_theta = mechanism.theta  

    # GIF-Setup
    gif_filename = "mechanism_simulation.gif"
    frames = []  
    

    while mechanism.theta - initial_theta < 2 * np.pi:  
        mechanism.theta += mechanism.speed  
        mechanism.joints[2] = mechanism.compute_gelenk_2()  
        optimized_joints = mechanism.optimize_joints()  

        if optimized_joints:
            ax.clear()
            ax.set_xlim(-plot_size_x / 2, plot_size_x / 2)  
            ax.set_ylim(-plot_size_y / 2, plot_size_y / 2)  
            ax.set_xticks(np.linspace(-plot_size_x / 2, plot_size_x / 2, num=5))
            ax.set_yticks(np.linspace(-plot_size_y / 2, plot_size_y / 2, num=5))

            

            # **Achsenbeschriftung aktualisieren**
            ax.set_title(f"Simulation des Viergelenk-Mechanismus\nPlotgröße: X={plot_size_x}, Y={plot_size_y}", fontsize=12, fontweight="bold")
            ax.set_xlabel("X-Achse (mm)", fontsize=10)
            ax.set_ylabel("Y-Achse (mm)", fontsize=10)
            ax.grid(True, linestyle="--", alpha=0.7)

            # Gelenkpositionen speichern
            for j, pos in mechanism.joints.items():
                if mechanism.show_trajectory.get(j, False):
                    trajectory[j].append(pos.copy())

            # Zeichne Mechanismus
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
                    ax.plot(points_np[:, 0], points_np[:, 1], 'r-', alpha=0.8)  
            
            # Aktualisiere Streamlit-Grafik
            placeholder.pyplot(fig)

            # Speichere Frame für das GIF
            if save_gif:
                fig.canvas.draw()
                buf = np.array(fig.canvas.renderer.buffer_rgba())
                image = Image.fromarray(buf)
                frames.append(image)

    # Speichere GIF
    if save_gif and frames:
        frames[0].save(
            gif_filename,
            save_all=True,
            append_images=frames[1:], 
            duration=50,  
            loop=0  
        )

    if return_trajectory:
        return trajectory, gif_filename
    return None, None
