# -*- coding: utf-8 -*-
import json
import os


def lade_highscores(datei="highscores.json"):
    """Lade Highscores aus einer Datei oder liefere eine leere Liste zurueck."""
    if not os.path.exists(datei) or os.path.getsize(datei) == 0:
        return []
    try:
        with open(datei, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Warnung: Ungueltiges JSON in {datei}. Datei wird zurueckgesetzt.")
        return []


def speichere_highscores(highscores, datei="highscores.json"):
    """Speichere die Highscores in einer JSON-Datei."""
    with open(datei, "w", encoding="utf-8") as file:
        json.dump(highscores, file, indent=4)


def aktualisiere_highscores(new_score, player_name, datei="highscores.json"):
    """Aktualisiere die Highscore-Liste mit einem neuen Eintrag."""
    if not player_name.strip() or not isinstance(new_score, (int, float)) or new_score <= 0:
        return

    highscores = lade_highscores(datei)
    highscores.append({"player": player_name.strip(), "score": new_score})
    highscores = sorted(highscores, key=lambda x: x["score"], reverse=True)[:10]
    speichere_highscores(highscores, datei)


