# Stellar Siege

**Stellar Siege** ist ein in Python (mit Pygame) entwickeltes Arcade-Spiel im Stil von *Space Invaders*, erweitert um Bosskaempfe, Soundeffekte, Musik, Highscores und mehrere Level-Welten.

## Features
 - Drei Welten mit je drei Stages, inklusive Bosskaempfen mit mehreren Phasen.
- Fluessige Spielerbewegung und FPS-unabhaengiges Gameplay.
- Animierte Neon-Buttons und optisch ansprechende Menues.
- Soundeffekte, Hintergrundmusik und einstellbare Lautstaerken.
- Highscore-System mit Speicherung in JSON.
- Mini-Bosse und unterschiedliche Alien-Verhalten je Welt.
- Upgrade-Shop zum Kauf von Power-Ups zwischen den Stages.

## Voraussetzungen
- Python ≥ 3.8
- [Pygame](https://www.pygame.org/) ≥ 2.1

Installiere Pygame mit:
```bash
pip install pygame
```

## Dateien
- `stellar_siege.py`: Haupteinstiegspunkt des Spiels mit Spielschleife und Level-Management.
- `display.py`: Darstellung der Screens (Hauptmenue, Optionen, Highscore, Win/Lose).
- `player.py`: Spielerlogik, Bewegung, Schuesse und Hitbox.
- `world1.py` & `world2.py`: Alien-Logik und Bossmechaniken fuer Welt 1 und 2.
- `world3.py`: Alien-Logik und Bossmechaniken fuer Welt 3.
- `sounds.py`: Laden und Anpassen von Soundeffekten und Musik.
- `settings.py`: Laden und Speichern der Lautstaerkeeinstellungen.
- `highscore.py`: Laden, Speichern und Aktualisieren der Highscores.
- `shop.py`: Upgrade-Shop zum Kauf von Power-Ups zwischen den Stages.

Zusaetzlich benoetigte Ressourcen (im selben Verzeichnis ablegen):
- Bilder: `raumschiff.png`, `alien1.png`, `alien2.png`, `alien3.png`, `world1.jpg`, `world2.jpg`, `world3.jpg`, `main_screen.png`, `highscore_screen.png`, `win_screen.png`, `lose_screen.png`
- Sounds: `shoot.wav`, `hit.wav`, `game_over.wav`, `win_sound.wav`, `alien_shoot.wav`, `alien_shoot_klein.wav`, `mouse_over.wav`, `mouse_click.wav`
- Musik: `main.wav`, `world1.wav`, `world2.wav`, `world3.wav`, `world1-boss.wav`, `world2-boss.wav`, `world3-boss.wav`, `shop.wav`

## Start
Starte das Spiel mit:
```bash
python stellar_siege.py
```

## Steuerung
- **Links/Rechts**: Bewegung
- **Leertaste**: Schiessen
- **Maus**: Navigation in den Menues
- **S**: Testmodus - ueberspringt die aktuelle Stage
 - **G**: Testmodus - toggelt Godmode (Unbesiegbarkeit). Der Modus bleibt nach
   Aktivierung auch ueber Stages hinweg erhalten und endet erst nach erneutem
   Druecken von **G** oder einem Neustart des Spiels.
 - **P**: Testmodus - gibt 1000 Punkte fuer Shop-Tests.

## Highscore
Nach einem Game Over kann der Spieler seinen Namen eingeben. Die besten 10 Scores werden in `highscores.json` gespeichert.

## Optionen
Im Optionsmenue koennen Musik- und Effektlautstaerke angepasst und gespeichert werden. Zudem gibt es eine Schaltflaeche, um zwischen Fenster- und Vollbildmodus zu wechseln. Die Einstellung wird in `settings.json` gesichert.
