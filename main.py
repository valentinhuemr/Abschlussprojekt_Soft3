import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tinydb import TinyDB, Query
from mechanisms.mechanism_model import Mechanism
from mechanisms.solver import Solver
import tempfile
import os

# Datenbankpfad
DB_PATH = "data/mechanisms.json"
db = TinyDB(DB_PATH)
MechanismQuery = Query()

# 🟢 Funktion zum Speichern
def save_mechanism(name, joints, fixed_joints, radius, start_angle):
    mechanism_data = {
        "name": name,
        "joints": joints,
        "fixed_joints": fixed_joints,
        "radius": radius,
        "start_angle": start_angle
    }
    db.insert(mechanism_data)

# 🟢 Funktion zum Laden
def load_mechanisms():
    return db.all()

# 🟢 Funktion zur Berechnung der neuen Gelenkpositionen (Kinematische Simulation)
def compute_mechanism_motion(joints, fixed_joints, radius, start_angle, steps=36):
    simulation_data = []
    x_c, y_c = joints[0]  # Mittelpunkt des rotierenden Arms
    l1 = np.linalg.norm(np.array(joints[1]) - np.array(joints[0]))  # Länge der ersten Stange

    for step in range(steps):
        theta = np.radians(start_angle + step * (360 / steps))  # Drehwinkel
        x_new = x_c + radius * np.cos(theta)
        y_new = y_c + radius * np.sin(theta)

        new_positions = [(x_c, y_c), (x_new, y_new)]

        # Berechnung der restlichen Gelenke unter Berücksichtigung fixer Punkte
        for i in range(2, len(joints)):
            if fixed_joints[i-2]:  # Fixierte Gelenke bleiben unverändert
                new_positions.append(joints[i])
            else:
                # Bewege das Gelenk so, dass die Stangenlänge erhalten bleibt
                prev_x, prev_y = new_positions[i - 1]
                l_i = np.linalg.norm(np.array(joints[i]) - np.array(joints[i - 1]))  # Länge der Stange
                angle_i = np.arctan2(joints[i][1] - joints[i-1][1], joints[i][0] - joints[i-1][0])

                new_x = prev_x + l_i * np.cos(angle_i)
                new_y = prev_y + l_i * np.sin(angle_i)
                new_positions.append((new_x, new_y))

        simulation_data.append(new_positions)

    return simulation_data

# 🟢 Funktion zur Animation
def plot_mechanism_animation(joints, simulation_data):
    fig, ax = plt.subplots()
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Kreisbahn berechnen
    x_c, y_c = joints[0]  # Mittelpunkt
    radius = np.linalg.norm(np.array(joints[1]) - np.array(joints[0]))
    theta_circle = np.linspace(0, 2 * np.pi, 100)
    x_circle = x_c + radius * np.cos(theta_circle)
    y_circle = y_c + radius * np.sin(theta_circle)
    ax.plot(x_circle, y_circle, 'r--', lw=1.5, label="Kreisbahn")

    # Gelenke und Stäbe zeichnen
    line, = ax.plot([], [], 'bo-', lw=2, label="Mechanismus")
    ax.scatter(x_c, y_c, c='black', marker='o', label="Mittelpunkt")

    # **Update-Funktion für die Animation**
    def update(frame):
        positions = simulation_data[frame]
        x_vals, y_vals = zip(*positions)
        line.set_data(x_vals, y_vals)
        return line,

    ani = animation.FuncAnimation(fig, update, frames=len(simulation_data), interval=100, repeat=True)

    # **GIF als temporäre Datei speichern**
    temp_gif = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
    ani.save(temp_gif.name, writer="pillow", fps=10)

    return temp_gif.name

# Streamlit UI
st.title("🔧 Mechanism Simulator")

mode = st.radio("Modus wählen:", ["Neuer Mechanismus", "Gespeicherten Mechanismus laden"])

if mode == "Neuer Mechanismus":
    # Eingabe für den Mechanismus
    name = st.text_input("Mechanismus Name", value="Viergelenkgetriebe")
    num_joints = st.number_input("Anzahl der Gelenke (ohne Mittelpunkt)", min_value=2, step=1, value=3)

    # Mittelpunkt-Eingabe
    st.write("### Mittelpunkt auswählen:")
    col1, col2 = st.columns(2)
    with col1:
        x_c = st.number_input("Mittelpunkt X", value=0)
    with col2:
        y_c = st.number_input("Mittelpunkt Y", value=0)

    radius = st.number_input("Radius der Rotation", min_value=1.0, value=10.0)
    start_angle = st.slider("Startwinkel (°)", 0, 360, 0)

    # Gelenk 1 auf der Kreisbahn
    x_start = x_c + radius * np.cos(np.radians(start_angle))
    y_start = y_c + radius * np.sin(np.radians(start_angle))

    joints = [(x_c, y_c), (x_start, y_start)]
    joint_positions = []
    fixed_joints = []

    # Restliche Gelenke
    st.write("### Gelenkpunkte auswählen:")
    for i in range(2, num_joints + 1):
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            x = st.number_input(f"Gelenk {i} X", value=i * 10, key=f"x{i}")
        with col2:
            y = st.number_input(f"Gelenk {i} Y", value=i * 5, key=f"y{i}")
        with col3:
            is_fixed = st.checkbox(f"Fix", key=f"fix{i}")

        joint_positions.append((x, y))
        fixed_joints.append(is_fixed)

    joints.extend(joint_positions)

    # **Speicher-Button**
    if st.button("💾 Mechanismus speichern"):
        save_mechanism(name, joints, fixed_joints, radius, start_angle)
        st.success("Mechanismus erfolgreich gespeichert!")

else:
    # 🟢 **Gespeicherten Mechanismus laden**
    saved_mechanisms = load_mechanisms()
    valid_mechanisms = [m for m in saved_mechanisms if "name" in m]

    if valid_mechanisms:
        selected_mechanism = st.selectbox("Gespeicherte Mechanismen:", [m["name"] for m in valid_mechanisms])
        mechanism_data = next(m for m in valid_mechanisms if m["name"] == selected_mechanism)

        name = mechanism_data["name"]
        joints = mechanism_data["joints"]
        fixed_joints = mechanism_data["fixed_joints"]
        radius = mechanism_data["radius"]
        start_angle = mechanism_data["start_angle"]

        st.write(f"🔄 **Mechanismus {name} geladen!**")

    else:
        st.warning("⚠️ Keine gespeicherten Mechanismen gefunden.")
        st.stop()

# **Simulation starten**
if st.button("▶️ Simulation starten"):
    try:
        simulation_data = compute_mechanism_motion(joints, fixed_joints, radius, start_angle)
        gif_path = plot_mechanism_animation(joints, simulation_data)
        st.image(gif_path, caption="Mechanism Animation")
        os.remove(gif_path)
    except Exception as e:
        st.error(f"Fehler bei der Simulation: {e}")
