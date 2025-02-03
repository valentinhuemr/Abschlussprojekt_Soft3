from tinydb import TinyDB
from mechanisms.mechanism_model import Mechanism

db = TinyDB("data/mechanisms.json")

def save_mechanism(mechanism):
    """Speichert einen Mechanismus in TinyDB"""
    mechanism_data = mechanism.to_dict()
    if not isinstance(mechanism_data, dict):
        raise TypeError("Mechanismus-Daten sind kein Dictionary!")
    db.insert(mechanism_data)

def load_mechanisms():
    """Lädt alle gespeicherten Mechanismen"""
    mechanisms = []
    
    data_list = db.all()
    
    if not isinstance(data_list, list):
        raise TypeError("Fehler: db.all() gibt keine Liste zurück!")
    
    for entry in data_list:
        if isinstance(entry, dict):  
            mechanisms.append(Mechanism.from_dict(entry))
        else:
            print("⚠️ Fehler: Eintrag in der Datenbank ist kein Dictionary:", entry)

    return mechanisms
