# -*- coding: utf-8 -*-
import pygame
import math
from sounds import (
    lade_musik
)

def world1_lade_hintergrundbild():
    """Lade das Hintergrundbild fuer Welt 1."""
    return pygame.image.load("world1.jpg")

def world1_lade_alien_img(current_stage):
    """Lade das passende Alien-Bild fuer die angegebene Stage."""
    alien_img = pygame.image.load("alien1.png")
    if current_stage == 3:
        alien_img = pygame.transform.scale(alien_img, (240, 180))  # Boss-Alien
    return alien_img

def world1_erstelle_stage_1_1_aliens():
    """Erstelle die Alienformation fuer Stage 1-1."""
    return world1_erstelle_aliens(5, 6, 100, 50, 30, 30)  # Abstand reduziert

def world1_erstelle_stage_1_2_aliens():
    """Erstelle die Alienformation fuer Stage 1-2."""
    return world1_erstelle_aliens(5, 7, 90, 50, 40, 40)   # Noch enger

def world1_erstelle_stage_1_3_aliens():
    """Erstelle den Boss fuer Stage 1-3."""
    screen_width = pygame.display.get_surface().get_width()
    boss_width = 240

    return [{
        "pos": [(screen_width // 2) - (boss_width // 2), -200],
        "hitpoints": 20,
        "max_hitpoints": 20,        # NEU: Maximal-Lebenspunkte
        "speed_multiplier": 1.0,
        "shoot_interval": 2000,     # Basis-Schussintervall (wird angepasst)
        "bullet_speed": 5,          # Geschwindigkeit der Boss-Schuesse
        "last_shot_time": 0,
        "is_boss": True,
        "is_invulnerable": True,
        "is_entering": True,
        "entry_speed": 1,
        "target_y": 100
    }]

def world1_erstelle_aliens(rows, cols, start_x, start_y, spacing_x, spacing_y):
    """Generiere ein Raster von Aliens."""
    aliens = []
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (spacing_x + 40)  # Breite = 40
            y = start_y + row * (spacing_y + 36)  # Hoehe = 36

            # Alien als Dictionary
            alien = {
                "pos": [x, y],
                "hitpoints": 1,
                "is_boss": False
            }

            aliens.append(alien)
    return aliens

def world1_bewege_aliens(aliens, alien_speed_x, alien_speed_y, screen_width, delta_time):
    """Bewege alle Aliens zeilenweise ueber den Bildschirm."""
    move_down = False
    speed_multiplier = 100  # Kontrolle der Geschwindigkeit
    alien_height = 36       # Hoehe des Alien-Bildes

    for alien in aliens:
        # Bewegung der X-Position
        alien["pos"][0] += alien_speed_x * delta_time * speed_multiplier

        # Randpruefung mit Positionskorrektur
        if alien["pos"][0] < 0:
            alien["pos"][0] = 0
            move_down = True
        elif alien["pos"][0] > screen_width - 40:  # 40 = Breite des Aliens
            alien["pos"][0] = screen_width - 40
            move_down = True

    # Wenn Aliens den Rand erreicht haben, nach unten bewegen
    if move_down:
        for alien in aliens:
            alien["pos"][1] += alien_height  # Um die Hoehe des Aliens nach unten rutschen
        alien_speed_x *= -1  # Richtung umkehren

    # Entferne Aliens, die den Bildschirm nach unten verlassen haben
    screen_height = pygame.display.get_surface().get_height()
    aliens = [alien for alien in aliens if alien["pos"][1] <= screen_height]

    return aliens, alien_speed_x, move_down
    
def world1_handle_boss(aliens, alien_bullets, current_time, bullet_img, sounds, player_pos, alien_speed_x, delta_time):
    """Steuere Verhalten und Angriffe des Stage-1 Bosses."""
    screen_width = pygame.display.get_surface().get_width()
    boss_width = 240
    speed_multiplier = 100

    for alien in aliens:
        if alien.get("is_boss", False):
            # Setze max_hitpoints, falls nicht vorhanden
            if "max_hitpoints" not in alien:
                alien["max_hitpoints"] = alien["hitpoints"]

            # Initialisiere die Aggressionsstufen-Flags, falls nicht gesetzt
            if "aggression_flags" not in alien:
                alien["aggression_flags"] = {"66": False, "33": False}

            # Berechne den prozentualen HP-Wert
            hp_ratio = alien["hitpoints"] / alien["max_hitpoints"]

            # Aggressionslevel bei 66% und 33% Lebenspunkten
            if hp_ratio <= 0.66 and not alien["aggression_flags"]["66"]:
                alien["shoot_interval"] = max(300, alien["shoot_interval"] // 2)
                alien["aggression_flags"]["66"] = True
                print("Boss wird aggressiver! Schiesst jetzt SCHNELLER!")

            if hp_ratio <= 0.33 and not alien["aggression_flags"]["33"]:
                alien["shoot_interval"] = max(300, alien["shoot_interval"] // 2)
                alien["aggression_flags"]["33"] = True
                print("Boss ist WUETEND! Schiesst jetzt SEHR SCHNELL!")

            # Einflug-Phase
            if alien.get("is_entering", True):
                alien["pos"][0] = (screen_width // 2) - (boss_width // 2)
                alien["pos"][1] += alien.get("entry_speed", 2) * delta_time * speed_multiplier
                alien["is_invulnerable"] = True

                if alien["pos"][1] >= alien.get("target_y", 100):
                    alien["pos"][1] = alien.get("target_y", 100)
                    alien["is_invulnerable"] = False
                    alien["is_entering"] = False
                    alien["last_shot_time"] = current_time

            # Normale Bewegung nach dem Einflug
            if not alien.get("is_entering", False):
                aliens, alien_speed_x = world1_bewege_einzelnes_alien(aliens, alien_speed_x, screen_width, delta_time)

                if not alien.get("is_invulnerable", False):
                    if current_time - alien.get("last_shot_time", 0) >= alien.get("shoot_interval", 2000):
                        alien_bullets = world1_boss_shooting(
                            aliens, alien_bullets, current_time, bullet_img, sounds,
                            alien.get("last_shot_time", 0), 300, player_pos, delta_time
                        )
                        alien["last_shot_time"] = current_time

    # Bewegung der Boss-Schuesse
    screen_height = pygame.display.get_surface().get_height()

    for bullet in alien_bullets[:]:
        bullet["pos"][0] += bullet.get("dx", 0) * delta_time * speed_multiplier
        bullet["pos"][1] += bullet.get("dy", 5) * delta_time * speed_multiplier

        if (
            bullet["pos"][1] >= screen_height or bullet["pos"][1] <= 0 or
            bullet["pos"][0] <= 0 or bullet["pos"][0] >= screen_width
        ):
            alien_bullets.remove(bullet)

    # Entferne besiegte Bosse sicherheitshalber
    aliens = [a for a in aliens if a.get("hitpoints", 1) > 0]

    return aliens, alien_bullets, alien_speed_x

def world1_bewege_einzelnes_alien(aliens, speed_x, screen_width, delta_time):
    """Bewege einen Boss oder ein normales Alien einzeln."""
    boss_width = 240
    alien_width = 40
    speed_multiplier = 100

    for alien in aliens:
        if alien.get("is_boss", False):
            # Initialisiere die Bewegungsrichtung, falls nicht vorhanden
            if "direction" not in alien:
                alien["direction"] = 1  # 1 = nach rechts, -1 = nach links

            adjusted_speed_x = speed_x * alien.get("speed_multiplier", 1.0)
            alien["pos"][0] += alien["direction"] * adjusted_speed_x * delta_time * speed_multiplier

            # Randpruefung mit Positionskorrektur
            if alien["pos"][0] <= 0:
                alien["pos"][0] = 0  # Position korrigieren
                alien["direction"] = 1  # Nach rechts bewegen

            elif alien["pos"][0] >= screen_width - boss_width:
                alien["pos"][0] = screen_width - boss_width  # Position korrigieren
                alien["direction"] = -1  # Nach links bewegen

            # Geschwindigkeitserhoehung basierend auf verlorenen Hitpoints
            lost_hitpoints = max(0, 20 - alien.get("hitpoints", 20))
            if lost_hitpoints > 0 and lost_hitpoints % 5 == 0:
                alien["speed_multiplier"] = 1.0 + 0.6 * (lost_hitpoints // 5)

        else:
            # Bewegung fuer normale Aliens
            alien["pos"][0] += speed_x * delta_time * speed_multiplier
            if alien["pos"][0] <= 0 or alien["pos"][0] >= screen_width - alien_width:
                speed_x *= -1

    return aliens, speed_x

def world1_zeichne_aliens(screen, aliens, alien_img):
    """Zeichne alle Aliens auf den Bildschirm."""
    for alien in aliens:
        screen.blit(alien_img, (alien["pos"][0], alien["pos"][1]))

def world1_zeichne_boss_lebensbalken(screen, boss_hitpoints, max_hitpoints):
    """Zeichne den Lebensbalken des Bosses."""
    # Position und Groesse des Lebensbalkens
    bar_x = 300
    bar_y = 10
    bar_width = 200
    bar_height = 20

    # Roter Hintergrund (fuer verlorene Lebenspunkte)
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

    # Berechnung des gruenen Balkens basierend auf den verbleibenden Lebenspunkten
    health_ratio = max(0, boss_hitpoints / max_hitpoints)
    green_bar_width = int(health_ratio * bar_width)

    # Gruener Balken (fuer verbleibende Lebenspunkte)
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, green_bar_width, bar_height))

    # Optional: Schwarzer Rahmen um den Lebensbalken
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)

def world1_lade_hintergrundmusik(current_stage, sounds):
    """Spiele die passende Hintergrundmusik fuer Welt 1 ab."""
    musik_key = "world1_boss_music" if current_stage == 3 else "world1_music"
    if musik_key in sounds["music"]:
        musik_datei = sounds["music"][musik_key]
        lade_musik(musik_datei)
        print(f"Hintergrundmusik fuer Stage {current_stage} geladen: {musik_datei}")
    else:
        print(f"Musikschluessel {musik_key} nicht in sounds['music'] gefunden.")

def world1_boss_shooting(aliens, bullets, current_time, bullet_img, sounds, last_shot_time, cooldown, player_pos, delta_time):
    """Lasse den Boss Schuesse auf den Spieler feuern."""
    screen_width = pygame.display.get_surface().get_width()
    screen_height = pygame.display.get_surface().get_height()
    speed_multiplier = 100  # Fuer FPS-unabhaengige Bewegung

    for alien in aliens:
        if alien.get("is_boss", False):  # Nur der Boss kann schiessen
            alien_width = 240
            alien_height = 180

            # Lebenspunkte & Anpassung des Schussintervalls
            max_hitpoints = alien.get("max_hitpoints", 20)  # Maximalwert definieren
            current_hitpoints = alien.get("hitpoints", 20)

            # Berechne den Lebensverlust in Prozent
            health_percentage = (current_hitpoints / max_hitpoints) * 100

            # Basis-Schussintervall
            base_shoot_interval = alien.get("shoot_interval", 3000)

            # Anpassung des Intervalls basierend auf dem Gesundheitsstatus
            if health_percentage <= 33:
                shoot_interval = base_shoot_interval // 3  # Sehr schnell
            elif health_percentage <= 66:
                shoot_interval = base_shoot_interval // 2  # Mittel-schnell
            else:
                shoot_interval = base_shoot_interval       # Standard

            # Boss schiesst, wenn genug Zeit vergangen ist
            if current_time - alien.get("last_shot_time", 0) >= shoot_interval:
                alien["last_shot_time"] = current_time

                # Startposition des Schusses (Mitte des Bosses)
                bullet_x = alien["pos"][0] + (alien_width // 2) - (bullet_img.get_width() // 2)
                bullet_y = alien["pos"][1] + (alien_height // 2)

                # Zielposition: Exakte Mitte der Spieler-Hitbox
                player_x, player_y = player_pos
                player_center_x = player_x + (70 // 2)   # Spielerbreite = 70
                player_center_y = player_y + (46 // 2)   # Spielerhoehe = 46

                # Berechne den Richtungsvektor zur Mitte des Spielers
                dx = player_center_x - bullet_x
                dy = player_center_y - bullet_y

                # Berechne die euklidische Distanz
                distance = math.hypot(dx, dy)
                if distance == 0:
                    distance = 0.001  # Vermeidung von Division durch 0

                # Normalisierung des Vektors
                dx /= distance
                dy /= distance

                # Verstaerkung des horizontalen Anteils
                angle_correction_factor = 1.3
                dx *= angle_correction_factor

                # Erneut normalisieren
                corrected_distance = math.hypot(dx, dy)
                dx /= corrected_distance
                dy /= corrected_distance

                # Geschwindigkeit des Schusses
                speed = alien.get("bullet_speed", 3)  # Standard: 3
                bullet_dx = dx * speed
                bullet_dy = dy * speed

                # Fuege den Schuss hinzu
                bullets.append({"pos": [bullet_x, bullet_y], "img": bullet_img, "dx": bullet_dx, "dy": bullet_dy})

                # Schuss-Sound
                if current_time - last_shot_time >= cooldown:
                    sounds["effects"]["alien_shoot"].set_volume(sounds["volumes"]["effects_volume"])
                    sounds["effects"]["alien_shoot"].play()

    # Bewege bestehende Schuesse (FPS-unabhaengig)
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet.get("dx", 0) * delta_time * speed_multiplier
        bullet["pos"][1] += bullet.get("dy", 5) * delta_time * speed_multiplier

        # Entfernen von Schuessen, die den Bildschirm verlassen
        if (
            bullet["pos"][1] >= screen_height or bullet["pos"][1] <= 0 or
            bullet["pos"][0] <= 0 or bullet["pos"][0] >= screen_width
        ):
            bullets.remove(bullet)

    return bullets

def world1_handle_erste_welle(aliens, speed_x, screen_width, delta_time):
    """Bewege die erste Alienwelle in Welt 1."""
    speed_multiplier = 100  # Kontrolle der Bewegungsgeschwindigkeit

    for alien in aliens:
        # FPS-unabhaengige horizontale Bewegung
        alien["pos"][0] += speed_x * delta_time * speed_multiplier

        # Bildschirmbegrenzung pruefen und vertikale Bewegung einfuegen
        if alien["pos"][0] > screen_width:
            alien["pos"][0] = -40  # Setzt das Alien links ausserhalb des Bildschirms neu
            alien["pos"][1] += 60  # Alien "rutscht" eine Zeile nach unten
        elif alien["pos"][0] < -40:
            alien["pos"][0] = screen_width  # Setzt das Alien rechts ausserhalb des Bildschirms neu
            alien["pos"][1] += 60  # Alien "rutscht" eine Zeile nach unten

    return aliens, speed_x

def world1_handle_zweite_welle(aliens, zweite_welle, speed_x, screen_width, max_depth=50, delta_time=0.016):
    """Steuere die zweite Alienwelle inklusive Kollisionspruefung."""
    alien_width = 40
    alien_height = 36
    spacing = 80
    speed_multiplier = 100  # Kontrolle der Bewegungsgeschwindigkeit

    # Initialisierung der zweiten Welle, wenn die erste abgeschlossen ist
    if not aliens and not zweite_welle.get("started", False):
        links = []
        rechts = []

        for row in range(2):
            for col in range(8):
                x_offset = col * spacing
                y_offset = row * (alien_height + 20)

                # Aliens von links und rechts erstellen
                if (row + col) % 2 == 0:
                    links.append({
                        "pos": [0 + x_offset, 0 + y_offset],
                        "dx": speed_x * 0.5,
                        "dy": 0.5
                    })
                else:
                    rechts.append({
                        "pos": [screen_width - alien_width - x_offset, 0 + y_offset],
                        "dx": -speed_x * 0.5,
                        "dy": 0.5
                    })

        zweite_welle = {
            "links": links,
            "rechts": rechts,
            "completed": False,
            "started": True
        }

    # Bewegung der zweiten Welle
    if zweite_welle.get("started", False):
        # Bei delta_time == 0 nur Status pruefen, keine Bewegung
        if delta_time == 0:
            if not zweite_welle["links"] and not zweite_welle["rechts"]:
                zweite_welle["completed"] = True
            return zweite_welle, speed_x, False

        alien_reached_player = False

        def bewege_aliens(alien_list):
            nonlocal alien_reached_player
            for alien in alien_list:
                # FPS-unabhaengige Bewegung
                alien["pos"][0] += alien["dx"] * delta_time * speed_multiplier
                alien["pos"][1] += alien["dy"] * delta_time * (speed_multiplier / 2)

                # Richtungswechsel am Rand
                if alien["pos"][0] <= 0:
                    alien["pos"][0] = 0
                    alien["dx"] *= -1
                elif alien["pos"][0] >= screen_width - alien_width:
                    alien["pos"][0] = screen_width - alien_width
                    alien["dx"] *= -1

                # Lose-Bedingung pruefen
                if alien["pos"][1] + alien_height >= max_depth:
                    alien_reached_player = True

        # Bewegung fuer beide Seiten (links und rechts)
        bewege_aliens(zweite_welle["links"])
        bewege_aliens(zweite_welle["rechts"])

        # Ueberpruefen, ob die zweite Welle abgeschlossen ist
        if not zweite_welle["links"] and not zweite_welle["rechts"]:
            zweite_welle["completed"] = True

        return zweite_welle, speed_x, alien_reached_player

    return zweite_welle, speed_x, False
