import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.optimize import minimize
from tinydb import TinyDB, Query

# Datenbank initialisieren
db = TinyDB("mechanism_configurations.json")

st.title("Simulation eines Viergelenk-Mechanismus")
st.sidebar.header("Mechanismus Konfiguration")

class Mechanism:
    def __init__(self, fixed_point, radius, start_angle, speed, joints, fixed_joints, rods):
        self.fixed_point = np.array(fixed_point)
        self.radius = radius
        self.theta = np.radians(start_angle)
        self.speed = np.radians(speed)
        self.joints = {int(k): np.array(v) for k, v in joints.items()}
        self.fixed_joints = set(fixed_joints)
        self.rods = rods
        self.initial_lengths = self.calculate_lengths()
    
    def compute_gelenk_2(self):
        return self.fixed_point + self.radius * np.array([np.cos(self.theta), np.sin(self.theta)])
    
    def calculate_lengths(self):
        return {pair: np.linalg.norm(self.joints[pair[0]] - self.joints[pair[1]]) for pair in self.rods}
    
    def optimize_joints(self):
        moving_joints = [j for j in self.joints if j not in self.fixed_joints and j != 2]
        if not moving_joints:
            return None
    
        def error_function(p_guess):
            error = 0
            positions = {j: p_guess[i*2:i*2+2] for i, j in enumerate(moving_joints)}
            for (j1, j2) in self.rods:
                expected_length = self.initial_lengths[(j1, j2)]
                if j1 in positions and j2 in positions:
                    actual_length = np.linalg.norm(positions[j1] - positions[j2])
                elif j1 in positions:
                    actual_length = np.linalg.norm(positions[j1] - self.joints[j2])
                elif j2 in positions:
                    actual_length = np.linalg.norm(self.joints[j1] - positions[j2])
                else:
                    actual_length = expected_length
                error += (actual_length - expected_length) ** 2
            return error
    
        initial_guess = np.concatenate([self.joints[j] for j in moving_joints])
        result = minimize(error_function, initial_guess, method="BFGS")
        if result.success:
            optimized_positions = result.x.reshape(-1, 2)
            for i, j in enumerate(moving_joints):
                self.joints[j] = optimized_positions[i]
            return self.joints
        else:
            return None
    
    def save(self, name):
        if name:
            db.upsert({"name": name, "fixed_point": self.fixed_point.tolist(), "radius": self.radius,
                       "theta": np.degrees(self.theta), "speed": np.degrees(self.speed),
                       "joints": {k: v.tolist() for k, v in self.joints.items()},
                       "fixed_joints": list(self.fixed_joints), "rods": self.rods}, Query().name == name)
            st.sidebar.success(f"Mechanismus '{name}' gespeichert!")
        else:
            st.sidebar.error("Bitte einen gültigen Namen eingeben.")
    
    @staticmethod
    def load(name):
        config = Query()
        result = db.get(config.name == name)
        if result:
            try:
                return Mechanism(
                    result["fixed_point"],
                    result["radius"],
                    result["theta"],
                    result["speed"],
                    {int(k): np.array(v) for k, v in result["joints"].items()},
                    set(result["fixed_joints"]),
                    result["rods"]
                )
            except (KeyError, TypeError, ValueError) as e:
                st.sidebar.error("Fehler beim Laden der Mechanismus-Daten. Bitte überprüfe die gespeicherten Werte.")
                return None
        else:
            st.sidebar.error("Mechanismus nicht gefunden.")
            return None

# UI Einstellungen
scale = st.sidebar.slider("Skalierung", 40, 500, 100, step=10)
mid_x = st.sidebar.number_input("Mittelpunkt X", value=0.0, step=1.0)
mid_y = st.sidebar.number_input("Mittelpunkt Y", value=0.0, step=1.0)
radius = st.sidebar.number_input("Rotationsradius für Gelenk 2", value=15.0, min_value=1.0, max_value=100.0, step=0.5)
start_angle = st.sidebar.slider("Startwinkel von Gelenk 2 (Grad)", 0, 360, 0)
speed = st.sidebar.slider("Geschwindigkeit (°/Frame)", 1, 10, 2)

num_joints = st.sidebar.number_input("Anzahl der Gelenke", min_value=4, max_value=15, value=4, step=1)
num_rods = st.sidebar.number_input("Anzahl der Stäbe", min_value=3, max_value=num_joints*(num_joints-1)//2, value=4, step=1)

joints = {1: np.array([mid_x, mid_y]), 2: np.array([mid_x + radius, mid_y])}
fixed_joints = {1}

st.sidebar.subheader("Gelenke Konfiguration")
for j in range(3, num_joints + 1):
    with st.sidebar.expander(f"Gelenk {j} bearbeiten"):
        x = st.number_input(f"Gelenk {j} - X", value=0.0, step=1.0)
        y = st.number_input(f"Gelenk {j} - Y", value=0.0, step=1.0)
        fixed = st.checkbox(f"Gelenk {j} fixiert?", value=False)
        joints[j] = np.array([x, y])
        if fixed:
            fixed_joints.add(j)

st.sidebar.subheader("Stäbe Konfiguration")
rods = []
for i in range(1, num_rods + 1):
    joint1 = st.sidebar.selectbox(f"Stab {i} - Gelenk 1", list(joints.keys()), key=f"rod_{i}_j1")
    joint2 = st.sidebar.selectbox(f"Stab {i} - Gelenk 2", list(joints.keys()), key=f"rod_{i}_j2")
    rods.append((joint1, joint2))

mech = Mechanism([mid_x, mid_y], radius, start_angle, speed, joints, fixed_joints, rods)

name = st.sidebar.text_input("Mechanismus Name")
if st.sidebar.button("💾 Speichern"):
    mech.save(name)

if st.sidebar.button("📂 Laden"):
    loaded_mech = Mechanism.load(name)
    if loaded_mech:
        mech = loaded_mech
