import cv2
import streamlit as st
import numpy as np
from mechanism import Mechanism
from storage import save_mechanism, load_mechanism, get_all_mechanism_names, delete_mechanism
from simulation import simulate_mechanism
import matplotlib.pyplot as plt
import time
import pandas as pd


st.title("Simulation eines 2D Mechanismus")
st.sidebar.header("Mechanismus Konfiguration")

st.sidebar.header("⚙ Mechanismus-Verwaltung")

# Gespeicherte Mechanismen abrufen & Dropdown-Menü anzeigen
saved_mechanisms = get_all_mechanism_names()
selected_mechanism = st.sidebar.selectbox("📂 Gespeicherte Mechanismen:", ["-"] + saved_mechanisms)

# **Platzhalter für UI-Felder (Standardwerte)**
if "loaded_data" not in st.session_state:
    st.session_state.loaded_data = None

# **Laden-Button**
if st.sidebar.button("📂 Laden"):
    if selected_mechanism != "-":
        loaded_mech = load_mechanism(selected_mechanism)
        if loaded_mech:
            st.session_state.loaded_data = {
                "mid_x": loaded_mech.fixed_point[0],
                "mid_y": loaded_mech.fixed_point[1],
                "radius": loaded_mech.radius,
                "start_angle": np.degrees(loaded_mech.theta),
                "speed": np.degrees(loaded_mech.speed),
                "num_joints": len(loaded_mech.joints),
                "num_rods": len(loaded_mech.rods),
                "joints": loaded_mech.joints,
                "fixed_joints": loaded_mech.fixed_joints,
                "rods": loaded_mech.rods
            }
            st.sidebar.success(f"✅ Mechanismus '{selected_mechanism}' geladen!")
    else:
        st.sidebar.error("⚠ Bitte einen Mechanismus auswählen.")

# **Löschen-Button**
if st.sidebar.button("🗑 Löschen"):
    if selected_mechanism != "-":
        delete_mechanism(selected_mechanism)
    else:
        st.sidebar.error("⚠ Bitte einen Mechanismus zum Löschen auswählen.")


# 📏 Manuelle Eingabe für die Plotgröße in X- und Y-Richtung
plot_size_x = st.sidebar.number_input("📐 Plot-Breite (X)", min_value=40, max_value=500, value=100, step=10)
plot_size_y = st.sidebar.number_input("📏 Plot-Höhe (Y)", min_value=40, max_value=500, value=100, step=10)



# **UI-Werte setzen**
mid_x = st.sidebar.number_input("Mittelpunkt X", value=st.session_state.loaded_data["mid_x"] if st.session_state.loaded_data else 0.0, step=1.0)
mid_y = st.sidebar.number_input("Mittelpunkt Y", value=st.session_state.loaded_data["mid_y"] if st.session_state.loaded_data else 0.0, step=1.0)
radius = st.sidebar.number_input("Rotationsradius für Gelenk 2", value=st.session_state.loaded_data["radius"] if st.session_state.loaded_data else 15.0, min_value=1.0, max_value=100.0, step=0.5)
start_angle = st.sidebar.slider("Startwinkel von Gelenk 2 (Grad)", 0, 360, int(st.session_state.loaded_data["start_angle"]) if st.session_state.loaded_data else 0)
speed = st.sidebar.slider("Geschwindigkeit (°/Frame)", 1, 10, int(st.session_state.loaded_data["speed"]) if st.session_state.loaded_data else 2)

num_joints = st.sidebar.number_input("Anzahl der Gelenke", min_value=4, max_value=15, value=st.session_state.loaded_data["num_joints"] if st.session_state.loaded_data else 4, step=1)
num_rods = st.sidebar.number_input("Anzahl der Stäbe", min_value=3, max_value=num_joints*(num_joints-1)//2, value=st.session_state.loaded_data["num_rods"] if st.session_state.loaded_data else 4, step=1)

joints = {1: np.array([mid_x, mid_y])}  # Gelenk 1 existiert, wird aber nicht angezeigt
fixed_joints = {1}
show_trajectory = {2: True}  # Gelenk 2 wird immer angezeigt

st.sidebar.subheader("Gelenke Konfiguration")

st.sidebar.subheader("Gelenk 2 (Berechnet)")
gelenk_2_x = mid_x + radius * np.cos(np.radians(start_angle))
gelenk_2_y = mid_y + radius * np.sin(np.radians(start_angle))
st.sidebar.text(f"X: {gelenk_2_x:.2f}, Y: {gelenk_2_y:.2f}")
joints[2] = np.array([gelenk_2_x, gelenk_2_y])


for j in range(3, num_joints + 1):
    with st.sidebar.expander(f"Gelenk {j} bearbeiten"):
        x = st.number_input(f"Gelenk {j} - X", value=st.session_state.loaded_data["joints"][j][0] if st.session_state.loaded_data and j in st.session_state.loaded_data["joints"] else 0.0, step=1.0, key=f"j_{j}_x")
        y = st.number_input(f"Gelenk {j} - Y", value=st.session_state.loaded_data["joints"][j][1] if st.session_state.loaded_data and j in st.session_state.loaded_data["joints"] else 0.0, step=1.0, key=f"j_{j}_y")
        fixed = st.checkbox(f"Gelenk {j} fixiert?", value=j in st.session_state.loaded_data["fixed_joints"] if st.session_state.loaded_data else False, key=f"j_{j}_fixed")
        show_traj = st.checkbox(f"Bahnkurve anzeigen?", value=False, key=f"j_{j}_traj")
        joints[j] = np.array([x, y])
        if fixed:
            fixed_joints.add(j)
        show_trajectory[j] = show_traj


st.sidebar.subheader("Stäbe Konfiguration")
rods = []

all_joint_keys = list(joints.keys())
if 1 not in all_joint_keys:
    all_joint_keys.insert(0, 1)
if 2 not in all_joint_keys:
    all_joint_keys.insert(1, 2)

for i in range(1, num_rods + 1):
    default_rod = (
        st.session_state.loaded_data["rods"][i-1]
        if st.session_state.loaded_data and i-1 < len(st.session_state.loaded_data["rods"])
        else (1, 2)
    )

    # Zwei Spalten für die Dropdowns (nebeneinander)
    col1, col2 = st.sidebar.columns(2)

    with col1:
        joint1 = st.selectbox(
            f"Stab {i} - Gelenk 1",
            all_joint_keys,
            index=all_joint_keys.index(default_rod[0]),
            key=f"rod_{i}_j1"
        )

    with col2:
        joint2 = st.selectbox(
            f"Stab {i} - Gelenk 2",
            all_joint_keys,
            index=all_joint_keys.index(default_rod[1]),
            key=f"rod_{i}_j2"
        )

    rods.append((joint1, joint2))

mech = Mechanism([mid_x, mid_y], radius, start_angle, speed, joints, fixed_joints, rods)
mech.show_trajectory = show_trajectory

# Statische Darstellung des Mechanismus in der Ausgangsstellung
fig, ax = plt.subplots(figsize=(5, 5))
ax.set_xlim([-plot_size_x / 2, plot_size_x / 2])
ax.set_ylim([-plot_size_y / 2, plot_size_y / 2])
ax.set_title("Ausgangsstellung des Mechanismus")

# Gelenke zeichnen
for j, coord in joints.items():
    ax.plot(coord[0], coord[1], 'ro' if j in fixed_joints else 'bo', markersize=8)
    ax.text(coord[0] + 2, coord[1] + 2, f"J{j}", fontsize=9, color='black')

# Stäbe zeichnen
for rod in rods:
    j1, j2 = rod
    p1, p2 = joints[j1], joints[j2]
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', lw=2)

# Anzeige im Streamlit
st.pyplot(fig)

name = st.sidebar.text_input("Mechanismus Name")
if st.sidebar.button("💾 Speichern"):
    save_mechanism(mech, name)




# **Simulation starten, wenn der Button gedrückt wird**
if st.button("🔄 Simulation durchführen & GIF speichern"):
    
    # **Gelenkpositionen optimieren und Längenfehler überprüfen**
    optimized_joints = mech.optimize_joints()
    
    if optimized_joints is None:
        st.error("❌ Mechanismus ist kinematisch nicht lösbar oder Längenfehler erkannt!")
    else:
        # **Falls die Optimierung erfolgreich war, Simulation durchführen**
        trajectory_data, gif_filename = simulate_mechanism(
            mech, 
            plot_size_x=plot_size_x,  
            plot_size_y=plot_size_y,  
            return_trajectory=True, 
            save_gif=True
        )

        if trajectory_data:
            # CSV-Daten vorbereiten
            csv_data = {"Frame": []}
            active_joints = [j for j in trajectory_data.keys() if mech.show_trajectory.get(j, False)]

            for j in active_joints:
                csv_data[f"Joint {j} X"] = []
                csv_data[f"Joint {j} Y"] = []

            num_frames = len(next(iter(trajectory_data.values())))

            for frame in range(num_frames):
                csv_data["Frame"].append(frame)
                for j in active_joints:
                    csv_data[f"Joint {j} X"].append(trajectory_data[j][frame][0])
                    csv_data[f"Joint {j} Y"].append(trajectory_data[j][frame][1])

            # CSV-Datei speichern und Download-Link anzeigen
            csv_filename = "mechanism_trajectory.csv"
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_filename, index=False)

            with open(csv_filename, "rb") as f:
                st.download_button("📥 Bahnkurven als CSV herunterladen", f, file_name=csv_filename, mime="text/csv")

        if gif_filename:
            # **GIF anzeigen**
            st.image(gif_filename)

            # **GIF-Download-Button anzeigen**
            with open(gif_filename, "rb") as f:
                st.download_button("🎥 Simulation als GIF herunterladen", f, file_name=gif_filename, mime="image/gif")