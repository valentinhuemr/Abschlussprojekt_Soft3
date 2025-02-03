import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def plot_mechanism_animation(mechanism, theta_values, simulation_data):
    fig, ax = plt.subplots()
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_aspect("equal")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Kreisbahn zeichnen
    theta_circle = np.linspace(0, 2*np.pi, 100)
    x_circle = mechanism.joints[0][0] + mechanism.radius * np.cos(theta_circle)
    y_circle = mechanism.joints[0][1] + mechanism.radius * np.sin(theta_circle)
    ax.plot(x_circle, y_circle, 'r--', lw=1.5, label="Kreisbahn")

    # Mechanismus zeichnen
    line, = ax.plot([], [], 'bo-', lw=2, label="Mechanismus")

    # Fixpunkte schwarz markieren
    for i, (x, y) in enumerate(mechanism.joints):
        if mechanism.fixed_joints[i]:
            ax.scatter(x, y, c='black', marker='o', label="Fixpunkt")

    ax.legend()

    def update(frame):
        positions = simulation_data[frame]
        x_vals, y_vals = zip(*positions)
        line.set_data(x_vals, y_vals)
        return line,

    ani = animation.FuncAnimation(fig, update, frames=len(simulation_data), interval=100, repeat=True)
    plt.show()
