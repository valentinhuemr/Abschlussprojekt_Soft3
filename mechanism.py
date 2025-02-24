import numpy as np
from scipy.optimize import minimize

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
                actual_length = np.linalg.norm(positions.get(j1, self.joints[j1]) - positions.get(j2, self.joints[j2]))
                error += (actual_length - expected_length) ** 2
            return error
    
        initial_guess = np.concatenate([self.joints[j] for j in moving_joints])
        result = minimize(error_function, initial_guess, method="BFGS")
        if result.success:
            optimized_positions = result.x.reshape(-1, 2)
            for i, j in enumerate(moving_joints):
                self.joints[j] = optimized_positions[i]
            return self.joints
        return None
