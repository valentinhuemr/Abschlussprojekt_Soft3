import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.optimize import minimize

# Streamlit UI
st.title("Physikalisch korrekte Simulation der Viergelenkkette")
st.sidebar.header("Parameter einstellen")

# Einstellbare Parameter für die Simulation
theta_start = np.radians(st.sidebar.slider("Startwinkel (°)", 0, 360, 0))
theta_speed = np.radians(st.sidebar.slider("Winkelgeschwindigkeit (°/Frame)", 1, 10, 2))
frames = st.sidebar.slider("Anzahl der Frames", 50, 300, 100)

# Definition der Fixpunkte (entspricht den Bildern)
p0 = np.array([0, 0])  # Fixpunkt
c = np.array([-30, 0])  # Mittelpunkt der Kreisbewegung

# Startkonfiguration der Punkte
p1 = np.array([10, 35])
p2 = np.array([-25, 10])

# Berechnung der initialen Längen (wie in den Bildern)
def calculate_lengths(p0, p1, p2, c):
    L1 = np.linalg.norm(p2 - c)  # Länge der Kurbel
    L2 = np.linalg.norm(p1 - p0)  # Länge von p0 zu p1
    L3 = np.linalg.norm(p1 - p2)  # Länge von p1 zu p2
    return L1, L2, L3

L1, L2, L3 = calculate_lengths(p0, p1, p2, c)

# Berechnet die neue Position von p2 basierend auf der Drehung um c
def compute_p2(theta):
    x = c[0] + L1 * np.cos(theta)
    y = c[1] + L1 * np.sin(theta)
    return np.array([x, y])

# Optimierungsfunktion für die Berechnung von p1
def optimize_p1(p2_new):
    def error_function(p1_guess):
        err1 = np.linalg.norm(p1_guess - p0) - L2
        err2 = np.linalg.norm(p1_guess - p2_new) - L3
        return err1**2 + err2**2  # Fehler minimieren

    p1_init = p1  # Startwert für Optimierung
    result = minimize(error_function, p1_init, method="BFGS")

    if result.success:
        return result.x
    else:
        st.error("Keine gültige Gelenkkonfiguration gefunden!")
        return None

# Streamlit Platzhalter für Animation
plot_container = st.empty()

# Simulation durchlaufen
theta_vals = np.linspace(theta_start, theta_start + frames * theta_speed, frames)

for theta in theta_vals:
    p2_new = compute_p2(theta)
    p1_new = optimize_p1(p2_new)

    if p1_new is None:
        break  # Falls keine Lösung gefunden wird, stoppe die Simulation

    # Zeichnen der Mechanismus-Bewegung
    fig, ax = plt.subplots()
    ax.set_xlim(-40, 40)
    ax.set_ylim(-40, 40)
    
    x_vals = [p0[0], p1_new[0], p2_new[0], c[0]]
    y_vals = [p0[1], p1_new[1], p2_new[1], c[1]]
    
    ax.plot(x_vals[:3], y_vals[:3], 'o-', lw=3, markersize=8)  # Gelenke p0 → p1 → p2
    ax.plot([p2_new[0], c[0]], [p2_new[1], c[1]], 'o-', lw=3, markersize=8, color="red")  # Verbindung p2 → c

    # Anzeige aktualisieren
    plot_container.pyplot(fig)
    plt.close(fig)
    time.sleep(0.05)  # Geschwindigkeitssteuerung
