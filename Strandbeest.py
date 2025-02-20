import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.optimize import minimize
import json
import os
if "reload" in st.session_state and st.session_state.reload:
    st.session_state.reload = False
    st.rerun()
st.title("Simulation eines Viergelenk-Mechanismus")
st.sidebar.header("Mechanismus Konfiguration")
CONFIG_FILE = "configurations.json"  # Datei, in der die Konfigurationen gespeichert werden

def save_to_database(config_name, config):
    """Speichert die aktuelle Konfiguration als JSON-Datei."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            all_configs = json.load(file)
    else:
        all_configs = {}

    all_configs[config_name] = config  # Speichern unter dem angegebenen Namen

    with open(CONFIG_FILE, "w") as file:
        json.dump(all_configs, file, indent=4)

def load_from_database(config_name):
    """Lädt eine gespeicherte Konfiguration aus der JSON-Datei."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            all_configs = json.load(file)
        return all_configs.get(config_name, None)  # Falls nicht vorhanden, None zurückgeben
    return None  # Falls die Datei nicht existiert
def load_database():
    """Lädt die gespeicherten Konfigurationen aus der JSON-Datei."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}  # Falls die Datei nicht existiert, leere Datenbank zurückgeben

# Simulation starten
start_simulation = st.sidebar.button("▶ Simulation starten", key="start_button")

if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "scale" not in st.session_state:
    st.session_state.scale = 100  # Standardwert für Skalierung

if start_simulation:
    st.session_state.simulation_running = not st.session_state.simulation_running

# Skalierung
scale = st.sidebar.slider("Skalierung anpassen", 40, 500, st.session_state.scale, step=10)
st.session_state.scale = scale

mid_x = st.sidebar.number_input("Mittelpunkt X", value=0.0, step=1.0)
mid_y = st.sidebar.number_input("Mittelpunkt Y", value=0.0, step=1.0)
fixed_point = np.array([mid_x, mid_y])

radius = st.sidebar.number_input("Rotationsradius für Gelenk 2", value=15.0, min_value=1.0, max_value=100.0, step=0.5)
start_angle = np.radians(st.sidebar.slider("Startwinkel von Gelenk 2 (Grad)", 0, 360, 0))
speed = np.radians(st.sidebar.slider("Geschwindigkeit (°/Frame)", 1, 10, 2))

def compute_gelenk_2(theta):
    return fixed_point + radius * np.array([np.cos(theta), np.sin(theta)])

default_joints = {
    1: fixed_point,
    2: compute_gelenk_2(start_angle),
    3: np.array([10, 35]),
    4: np.array([-25, 10])
}

num_joints = st.sidebar.number_input("Anzahl der Gelenke", min_value=4, max_value=15, value=len(default_joints), step=1)
num_rods = st.sidebar.number_input("Anzahl der Stäbe", min_value=3, max_value=num_joints*(num_joints-1)//2, value=4, step=1)

joints = default_joints.copy()
fixed_joints = {1}

st.sidebar.subheader("Gelenke Konfiguration")
for j in range(3, num_joints + 1):
    with st.sidebar.expander(f"Gelenk {j} bearbeiten"):
        x = st.number_input(f"Gelenk {j} - X", value=float(joints.get(j, np.array([0, 0]))[0]))
        y = st.number_input(f"Gelenk {j} - Y", value=float(joints.get(j, np.array([0, 0]))[1]))
        fixed = st.checkbox(f"Gelenk {j} fixiert?", value=(j in fixed_joints))
        joints[j] = np.array([x, y])
        if fixed:
            fixed_joints.add(j)
        elif j in fixed_joints:
            fixed_joints.remove(j)

st.sidebar.subheader("Stäbe Konfiguration")
rods = []
for i in range(1, num_rods + 1):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        joint1 = st.selectbox(f"Stab {i} - Gelenk 1", list(joints.keys()), key=f"rod_{i}_j1")
    with col2:
        joint2 = st.selectbox(f"Stab {i} - Gelenk 2", list(joints.keys()), key=f"rod_{i}_j2")
    rods.append((joint1, joint2))

def calculate_lengths(joints, rods):
    return {pair: np.linalg.norm(joints[pair[0]] - joints[pair[1]]) for pair in rods}

initial_lengths = calculate_lengths(joints, rods)

def optimize_joints():
    moving_joints = [j for j in joints if j not in fixed_joints and j != 2]
    if not moving_joints:
        return None

    def error_function(p_guess):
        error = 0
        positions = {j: p_guess[i*2:i*2+2] for i, j in enumerate(moving_joints)}
        for (j1, j2) in rods:
            expected_length = initial_lengths[(j1, j2)]
            if j1 in positions and j2 in positions:
                actual_length = np.linalg.norm(positions[j1] - positions[j2])
            elif j1 in positions:
                actual_length = np.linalg.norm(positions[j1] - joints[j2])
            elif j2 in positions:
                actual_length = np.linalg.norm(joints[j1] - positions[j2])
            else:
                actual_length = expected_length
            error += (actual_length - expected_length) ** 2
        return error

    initial_guess = np.concatenate([joints[j] for j in moving_joints])
    result = minimize(error_function, initial_guess, method="BFGS")
    if result.success:
        optimized_positions = result.x.reshape(-1, 2)
        for i, j in enumerate(moving_joints):
            joints[j] = optimized_positions[i]
        return joints
    else:
        return None

# JSON: Speichern & Laden
st.sidebar.subheader("🔹 Konfiguration speichern/laden")
db = load_database()
config_names = list(db.keys())
selected_config = st.sidebar.selectbox("Gespeicherte Konfigurationen", ["-- Wählen --"] + config_names)

config_name = st.sidebar.text_input("Name der Konfiguration")
if st.sidebar.button("💾 Speichern"):
    if config_name:
        config = {
            "scale": st.session_state.scale,
            "fixed_point": fixed_point.tolist(),
            "radius": radius,
            "start_angle": np.degrees(start_angle),
            "speed": np.degrees(speed),
            "joints": {k: v.tolist() for k, v in joints.items()},  # Speichert alle Gelenkkoordinaten
            "fixed_joints": list(fixed_joints),  # Fixierte Gelenke
            "num_joints": num_joints,  # Anzahl der Gelenke
            "num_rods": num_rods,  # Anzahl der Stäbe
            "rods": rods  # Liste der Stäbe (Verbindungen)
        }
        save_to_database(config_name, config)
        st.success(f"Konfiguration '{config_name}' gespeichert!")
    else:
        st.warning("Bitte einen Namen eingeben.")


# Konfiguration laden
#config_options = get_saved_configs()  # Diese Funktion gibt eine Liste gespeicherter Konfigurationen zurück

if st.sidebar.button("⬇ Laden"):
    if selected_config:
        config = load_from_database(selected_config)  # Lädt die Konfiguration als Dictionary

        if config:
            # Geladene Werte in den Session-State schreiben
            st.session_state.scale = config["scale"]
            fixed_point = np.array(config["fixed_point"])
            radius = config["radius"]
            start_angle = np.radians(config["start_angle"])
            speed = np.radians(config["speed"])
            joints = {int(k): np.array(v) for k, v in config["joints"].items()}  # Gelenk-Koordinaten wiederherstellen
            fixed_joints = set(config["fixed_joints"])
            num_joints = config["num_joints"]
            num_rods = config["num_rods"]
            rods = config["rods"]

            st.success(f"Konfiguration '{selected_config}' erfolgreich geladen!")
        else:
            st.error("Fehler beim Laden der Konfiguration.")
    else:
        st.warning("Bitte eine Konfiguration auswählen.")



# Simulation
plot_container = st.empty()
theta = start_angle

while True:
    if st.session_state.simulation_running:
        theta += speed
        joints[1] = np.array([mid_x, mid_y])
        joints[2] = compute_gelenk_2(theta)
        updated_joints = optimize_joints()
        if updated_joints is None:
            continue

    fig, ax = plt.subplots()
    ax.set_xlim([-scale / 2, scale / 2])
    ax.set_ylim([-scale / 2, scale / 2])
    ax.set_aspect('equal')

    for joint1, joint2 in rods:
        ax.plot(*zip(joints[joint1], joints[joint2]), 'o-', lw=3, markersize=8)

    plot_container.pyplot(fig)
    plt.close(fig)
    time.sleep(0.05)
