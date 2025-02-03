import numpy as np

class Mechanism:
    def __init__(self, name, joints, links, joint_types, rotating_joint=None, radius=None):
        self.name = name
        self.joints = np.array(joints)  
        self.links = links  
        self.joint_types = joint_types  
        self.rotating_joint = rotating_joint  
        self.radius = radius  

    def to_dict(self):
        return {
            "name": self.name,
            "joints": self.joints.tolist(),
            "links": self.links,
            "joint_types": self.joint_types,
            "rotating_joint": self.rotating_joint,
            "radius": self.radius
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            joints=np.array(data["joints"]),
            links=data["links"],
            joint_types=data["joint_types"],
            rotating_joint=data.get("rotating_joint"),
            radius=data.get("radius")
        )
