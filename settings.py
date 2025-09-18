# -*- coding: utf-8 -*-
import json
import os

SETTINGS_FILE = "settings.json"  # Pfad zur Einstellungsdatei

def lade_einstellungen():
    """
    Lese die Einstellungen aus der Datei oder liefere Standardwerte zurueck.
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if "fullscreen" not in data:
                    data["fullscreen"] = False
                return data
        except (json.JSONDecodeError, IOError):
            print("Fehler beim Lesen der Einstellungen. Verwende Standardwerte.")
    return {
        "music_volume": 0.5,
        "effects_volume": 0.5,
        "fullscreen": False
    }

def speichere_einstellungen(einstellungen):
    """
    Speichere die Einstellungen in die Datei.
    """
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(einstellungen, file, indent=4)
        print("Einstellungen erfolgreich gespeichert.")
    except IOError as e:
        print(f"Fehler beim Speichern der Einstellungen: {e}")
