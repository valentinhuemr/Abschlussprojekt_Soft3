from tinydb import TinyDB, Query

class MechanismDB:
    def __init__(self):
        self.db = TinyDB("mechanisms.json")

    def save_mechanism(self, name, joints, rods, radius):
        self.db.insert({"name": name, "joints": joints, "rods": rods, "radius": radius})

    def load_mechanism(self, name):
        Mechanism = Query()
        result = self.db.search(Mechanism.name == name)
        return result[0] if result else None
