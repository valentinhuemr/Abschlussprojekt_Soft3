import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Mechanismus-Parameter (angepasst für Stabilität)
L1, L2, L3, L4 = 4, 3, 3, 4  # Längen der Glieder
theta1_vals = np.linspace(0, 2*np.pi, 100)  # Bewegung der Antriebsstange

# Funktion zur Positionsberechnung des Mechanismus
def compute_positions(theta1):
    x1, y1 = 0, 0  # Fixpunkt
    x2, y2 = L1 * np.cos(theta1), L1 * np.sin(theta1)
    x3, y3 = x2 + L2, y2  # Vereinfachung für eine stabile Simulation
    x4, y4 = L4, 0  # Zweiter Fixpunkt
    return (x1, y1), (x2, y2), (x3, y3), (x4, y4)

# Streamlit App Header
st.title("Simulation des 4-Gelenk-Mechanismus")

# Matplotlib Animation
fig, ax = plt.subplots()
ax.set_xlim(-L1 - L2 - 1, L1 + L2 + 1)
ax.set_ylim(-L1 - L2 - 1, L1 + L2 + 1)
line, = ax.plot([], [], 'o-', lw=2)

def init():
    line.set_data([], [])
    return line,

def update(frame):
    joints = compute_positions(theta1_vals[frame])
    x_vals, y_vals = zip(*joints)
    line.set_data(x_vals, y_vals)
    return line,

ani = animation.FuncAnimation(fig, update, frames=len(theta1_vals), init_func=init, blit=True)

# Anzeige in Streamlit
st.pyplot(fig)
