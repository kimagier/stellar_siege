# -*- coding: utf-8 -*-
import pygame
import random
import math
from sounds import (
    lade_musik
)

def world2_lade_hintergrundbild():
    """Lade das Hintergrundbild fuer Welt 2."""
    return pygame.image.load("world2.jpg")
    
def apply_color_filter(image, color=None):
    """Return a colorized version of ``image``.

    If ``color`` is ``None`` both orange and red filtered surfaces are
    returned in a dictionary. Otherwise the image is tinted with the given
    color and the tinted ``pygame.Surface`` is returned.
    """

    if color is None:
        # Provide default orange and red versions for bosses
        orange_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        orange_image.fill((255, 165, 0))
        orange_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        red_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        red_image.fill((255, 0, 0))
        red_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return {"orange": orange_image, "red": red_image}

    tinted_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tinted_image.fill(color)
    tinted_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image

def world2_lade_alien_img(current_stage, is_mini_boss=False):
    """Lade das passende Alien-Bild fuer Welt 2."""
    alien_img = pygame.image.load("alien2.png")
    
    if current_stage == 6:
        if is_mini_boss:
            alien_img = pygame.transform.scale(alien_img, (120, 90))  # **Mini-Boss**
            alien_img = apply_color_filter(alien_img, (255, 140, 0))  # **Orangerot**
        else:
            alien_img = pygame.transform.scale(alien_img, (240, 180))  # **Phase-1-Boss**
    
    else:
        alien_img = pygame.transform.scale(alien_img, (40, 36))  # **Normale Aliens**

    return alien_img

def world2_erstelle_stage_2_1_aliens():
    """Erstelle die Alienformation fuer Stage 2-1."""
    return world2_erstelle_aliens(5, 6, 100, 50, 30, 30)  # Abstand reduziert

def world2_erstelle_stage_2_2_aliens():
    """Erstelle die Alienformation fuer Stage 2-2."""
    return world2_erstelle_aliens(5, 7, 90, 50, 40, 40)   # Noch enger

def world2_erstelle_stage_2_3_aliens():
    """Erstelle den Boss fuer Stage 2-3."""
    screen_width = pygame.display.get_surface().get_width()
    boss_width = 240

    return [{
        "pos": [(screen_width // 2) - (boss_width // 2), -200],  # Startposition in der Mitte
        "hitpoints": 40,
        "max_hitpoints": 40,        # Maximale Lebenspunkte des Bosses
        "speed_multiplier": 1.0,
        "shoot_interval": 2000,     # Schussintervall in Millisekunden
        "bullet_speed": 5,          # Geschwindigkeit der Boss-Schuesse
        "last_shot_time": 0,
        "is_boss": True,
        "is_invulnerable": True,
        "is_entering": True,
        "entry_speed": 1,
        "target_y": 100,
        "phase": 1,
        "has_split": False
    }]

def world2_erstelle_aliens(rows, cols, start_x, start_y, spacing_x, spacing_y):
    """Generiere ein Raster von Aliens fuer Welt 2."""
    aliens = []
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (spacing_x + 40)  # 40 = Breite des Aliens
            y = start_y + row * (spacing_y + 36)  # 36 = Hoehe des Aliens

            # Aliens der oberen 2 Reihen bewegen sich nach LINKS (-1)
            # Aliens der unteren 3 Reihen bewegen sich nach RECHTS (1)
            direction = -1 if row < 2 else 1

            # Alien als Dictionary mit Bewegungsrichtung
            alien = {
                "pos": [x, y],
                "hitpoints": 1,
                "is_boss": False,
                "can_shoot": True,                        # Aliens koennen schiessen
                "shoot_interval": random.randint(3000, 5000),
                "last_shot_time": 0,
                "direction": direction                   # NEU: Bewegungsrichtung
            }

            aliens.append(alien)
    return aliens

def world2_bewege_aliens(aliens, alien_speed_x, alien_speed_y, screen_width, delta_time):
    """Bewege die Aliens in Wellenform ueber den Bildschirm."""
    speed_multiplier = 100

    wave_amplitude = 50       # Hoehe der Wellenbewegung
    wave_speed = 2000         # Langsame Wellenbewegung

    for alien in aliens:
        # Initiale Y-Position speichern (nur einmal)
        if "initial_y" not in alien:
            alien["initial_y"] = alien["pos"][1]

        # Horizontale Bewegung
        alien["pos"][0] += alien_speed_x * delta_time * speed_multiplier

        # Wellenbewegung (relativ zur urspruenglichen Position)
        alien["pos"][1] = alien["initial_y"] + wave_amplitude * math.sin(pygame.time.get_ticks() / wave_speed)

        # Randpruefung (links/rechts) mit Richtungswechsel
        if alien["pos"][0] < 0:
            alien["pos"][0] = 0
            alien_speed_x *= -1  # Richtung umkehren
        elif alien["pos"][0] > screen_width - 40:  # 40 = Alien-Breite
            alien["pos"][0] = screen_width - 40
            alien_speed_x *= -1  # Richtung umkehren

    return aliens, alien_speed_x, False
    
def world2_handle_alien_shooting(aliens, alien_bullets, current_time, bullet_img, delta_time, sounds, global_last_shot_time):
    """Steuere Schuesse normaler Aliens inklusive Cooldowns."""
    screen_height = pygame.display.get_surface().get_height()
    shooting_chance = 0.01     # Wahrscheinlichkeit fuer einen Schuss
    bullet_speed = 5
    speed_multiplier = 100
    alien_cooldown = 3000      # Individueller Cooldown fuer jedes Alien (3 Sekunden)
    global_cooldown = 1000     # Globaler Cooldown nach jedem Schuss (1 Sekunde)

    # Erlaube nur einen aktiven Alien-Schuss und pruefe den globalen Cooldown
    if len(alien_bullets) == 0 and (current_time - global_last_shot_time >= global_cooldown):
        random.shuffle(aliens)  # Zufaellige Reihenfolge fuer Abwechslung

        for alien in aliens:
            if not alien.get("is_boss", False):
                if "last_shot_time" not in alien:
                    alien["last_shot_time"] = 0

                # Ueberpruefen, ob das Alien bereit ist zu schiessen
                if current_time - alien["last_shot_time"] >= alien_cooldown:
                    if random.random() < shooting_chance:
                        bullet_x = alien["pos"][0] + 20  # Mitte des Aliens
                        bullet_y = alien["pos"][1] + 36  # Unterhalb des Aliens

                        # Schuss erstellen
                        alien_bullets.append({
                            "start_x": bullet_x,
                            "pos": [bullet_x, bullet_y],
                            "img": bullet_img,
                            "dy": bullet_speed
                        })

                        # Cooldowns aktualisieren
                        alien["last_shot_time"] = current_time
                        global_last_shot_time = current_time  # Globaler Cooldown startet jetzt

                        # Sound abspielen
                        sounds["effects"]["alien_shoot_klein"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["alien_shoot_klein"].play()

                        break  # Nur ein Schuss pro Frame zulassen

    # Bewege den aktiven Schuss
    for bullet in alien_bullets[:]:
        bullet["pos"][1] += bullet["dy"] * delta_time * speed_multiplier

        # Fixiere die horizontale Position
        bullet["pos"][0] = bullet["start_x"]

        # Entferne Schuesse, die den Bildschirm verlassen
        if bullet["pos"][1] > screen_height:
            alien_bullets.remove(bullet)

    return alien_bullets, global_last_shot_time
    
def world2_handle_boss(aliens, alien_bullets, current_time, bullet_img, sounds, player_pos, alien_speed_x, delta_time, alien_img):
    """Steuere Bossverhalten und spalte ihn bei Niederlage."""
    screen_width = pygame.display.get_surface().get_width()
    speed_multiplier = 100
    new_aliens = []  # Speichert Mini-Bosse fuer Phase 2
    phase2_spawned = False

    for alien in aliens[:]:  # Kopie der Liste, um Probleme zu vermeiden
        if alien.get("is_boss", False):
            if "max_hitpoints" not in alien:
                alien["max_hitpoints"] = alien["hitpoints"]

            if "aggression_flag" not in alien:
                alien["aggression_flag"] = False

            if "has_split" not in alien:
                alien["has_split"] = False  # Sicherstellen, dass der Boss nur einmal gesplittet wird

            if "phase" not in alien:
                alien["phase"] = 1  # Standard: Phase 1

            hp_ratio = alien["hitpoints"] / alien["max_hitpoints"]

            # Wenn der Phase-1-Boss besiegt wurde, sofort teilen
            if (
                alien.get("phase", 1) == 1
                and alien.get("hitpoints", 0) <= 0
                and not alien.get("has_split", False)
            ):
                filtered_images = apply_color_filter(alien_img)
                mini_boss_template = {
                    "hitpoints": 20,
                    "max_hitpoints": 20,
                    "is_boss": True,
                    "phase": 2,
                    "speed_multiplier": alien_speed_x,
                    "shoot_interval": 2000,
                    "bullet_speed": 5,
                    "last_shot_time": 0,
                    "is_invulnerable": False,
                    "direction": 1,
                    "size": (120, 90),
                }

                mini_boss_1 = mini_boss_template.copy()
                mini_boss_1["pos"] = [screen_width // 2 - 60, 100]
                mini_boss_1["direction"] = -1
                mini_boss_1["base_y"] = 100
                mini_boss_1["bar_position"] = 250  # Linker Lebensbalken
                mini_boss_1["image"] = pygame.transform.scale(
                    filtered_images["orange"], (120, 90)
                )

                mini_boss_2 = mini_boss_template.copy()
                mini_boss_2["pos"] = [screen_width // 2 - 60, 190]
                mini_boss_2["direction"] = 1
                mini_boss_2["base_y"] = 190
                mini_boss_2["bar_position"] = 430  # Rechter Lebensbalken
                mini_boss_2["image"] = pygame.transform.scale(
                    filtered_images["orange"], (120, 90)
                )

                new_aliens.extend([mini_boss_1, mini_boss_2])
                aliens.remove(alien)
                phase2_spawned = True
                continue

            # **Phase 1: Boss wird aggressiver bei 50 % HP**
            if alien["phase"] == 1 and hp_ratio <= 0.5 and not alien["aggression_flag"]:
                alien["shoot_interval"] = max(300, alien.get("shoot_interval", 2000) // 2)
                alien["aggression_flag"] = True
                print("Boss wird aggressiver!")

            # **Boss Bewegung**
            if alien.get("is_entering", True):
                alien["pos"][1] += alien.get("entry_speed", 2) * delta_time * speed_multiplier
                alien["is_invulnerable"] = True

                if alien["pos"][1] >= alien.get("target_y", 100):
                    alien["pos"][1] = alien.get("target_y", 100)
                    alien["is_invulnerable"] = False
                    alien["is_entering"] = False
                    alien["last_shot_time"] = current_time

            if not alien.get("is_invulnerable", False):
                if current_time - alien.get("last_shot_time", 0) >= alien.get("shoot_interval", 2000):
                    alien_bullets = world2_boss_shooting(
                        [alien],
                        alien_bullets,
                        current_time,
                        bullet_img,
                        sounds,
                        alien.get("last_shot_time", 0),
                        300,
                        player_pos,
                        delta_time,
                    )
                    alien["last_shot_time"] = current_time

    # **Phase 2: Boss wurde besiegt, jetzt Mini-Bosse erzeugen!**
    if (
        not phase2_spawned
        and not [alien for alien in aliens if alien.get("is_boss", False) and not alien["has_split"]]
    ):
        print("Phase 1 beendet! Boss ist wirklich tot! Phase 2 startet jetzt.")

        # **Mini-Bosse erstellen**
        filtered_images = apply_color_filter(alien_img)  # Einmalig filtern
        mini_boss_template = {
            "hitpoints": 20,
            "max_hitpoints": 20,
            "is_boss": True,
            "phase": 2,
            "speed_multiplier": alien_speed_x,  
            "shoot_interval": 2000,
            "bullet_speed": 5,
            "last_shot_time": 0,
            "is_invulnerable": False,
            "direction": 1,
            "size": (120, 90),  # **Halbe Groesse**
            "color_filter": (255, 140, 0)  # **Orangerot**
        }

        # Mini-Boss 1 (oben)
        mini_boss_1 = mini_boss_template.copy()
        mini_boss_1["pos"] = [screen_width // 2 - 60, 100]  # Exakte Y-Position setzen
        mini_boss_1["direction"] = -1
        mini_boss_1["base_y"] = 100  # NEU: Basis-Y zurueckbringen!
        mini_boss_1["bar_position"] = 250  # Linker Lebensbalken
        mini_boss_1["image"] = pygame.transform.scale(filtered_images["orange"], (120, 90))

        # Mini-Boss 2 (unten)
        mini_boss_2 = mini_boss_template.copy()
        mini_boss_2["pos"] = [screen_width // 2 - 60, 190]  # Exakte Y-Position setzen
        mini_boss_2["direction"] = 1
        mini_boss_2["base_y"] = 190  # NEU: Basis-Y zurueckbringen!
        mini_boss_2["bar_position"] = 430  # Rechter Lebensbalken
        mini_boss_2["image"] = pygame.transform.scale(filtered_images["orange"], (120, 90))

        # Mini-Bosse zur Liste hinzufuegen
        new_aliens.append(mini_boss_1)
        new_aliens.append(mini_boss_2)
        phase2_spawned = True

    # **Mini-Bosse erst hinzufuegen, wenn Phase 2 beginnt**
    if new_aliens:
        print(f"{len(new_aliens)} Mini-Bosse werden zur Alien-Liste hinzugefuegt!")
        aliens.extend(new_aliens)

    # Alle aktiven Bosse einmalig bewegen
    aliens, alien_speed_x = world2_bewege_einzelnes_alien(
        aliens, alien_speed_x, screen_width, delta_time
    )

    # **Bewege Boss-Schuesse**
    screen_height = pygame.display.get_surface().get_height()

    for bullet in alien_bullets[:]:
        bullet["pos"][0] += bullet.get("dx", 0) * delta_time * speed_multiplier
        bullet["pos"][1] += bullet.get("dy", 5) * delta_time * speed_multiplier

        if bullet["pos"][1] >= screen_height or bullet["pos"][1] <= 0:
            alien_bullets.remove(bullet)

    return aliens, alien_bullets, alien_speed_x

def world2_bewege_einzelnes_alien(aliens, speed_x, screen_width, delta_time):
    """Bewege einen Boss oder ein Alien unter Beruecksichtigung der Phase."""
    boss_width = 240  # Phase-1-Boss Breite
    mini_boss_width = 120  # Phase-2-Boss Breite
    alien_width = 40  # Normale Aliens
    speed_multiplier = 100

    for alien in aliens:
        if alien.get("is_invulnerable", False):
            continue

        if alien.get("is_boss", False):
            if "direction" not in alien:
                alien["direction"] = 1  # Standard-Richtung setzen

            if "max_hitpoints" not in alien:
                alien["max_hitpoints"] = 40  # Max HP sicherstellen

            adjusted_speed_x = speed_x * alien.get("speed_multiplier", 1.0)
            alien["pos"][0] += alien["direction"] * adjusted_speed_x * delta_time * speed_multiplier

            # **Phase 1 Boss Bewegung**
            if alien.get("phase", 1) == 1:
                right_boundary = screen_width - boss_width  # Richtige Begrenzung fuer Phase-1-Boss

            # **Phase 2 Mini-Bosse Bewegung**
            elif alien.get("phase") == 2:
                right_boundary = screen_width - mini_boss_width  # Begrenzung fuer Phase-2-Mini-Bosse

                # **Mini-Bosse auf der richtigen Hoehe halten**
                if "base_y" in alien:
                    alien["pos"][1] = alien["base_y"]  # Erzwinge die korrekte Y-Position!

            # Randpruefung mit Richtungswechsel
            if alien["pos"][0] <= 0:
                alien["pos"][0] = 0
                alien["direction"] = 1
            elif alien["pos"][0] >= right_boundary:
                alien["pos"][0] = right_boundary
                alien["direction"] = -1

            # Geschwindigkeitserhoehung bei verlorenem HP
            lost_hitpoints = max(0, alien["max_hitpoints"] - alien.get("hitpoints", 40))
            if lost_hitpoints > 0 and lost_hitpoints % 8 == 0:
                new_multiplier = 1.0 + 0.4 * (lost_hitpoints // 8)
                # Increase speed only, never reset it when another boss dies
                if new_multiplier > alien.get("speed_multiplier", 1.0):
                    alien["speed_multiplier"] = new_multiplier

        else:
            # Bewegung fuer normale Aliens
            alien["pos"][0] += speed_x * delta_time * speed_multiplier

            # Randpruefung fuer normale Aliens
            if alien["pos"][0] <= 0 or alien["pos"][0] >= screen_width - alien_width:
                speed_x *= -1

    return aliens, speed_x

def world2_zeichne_aliens(screen, aliens, alien_img):
    """Zeichne Aliens und Mini-Bosse fuer Welt 2."""
    for alien in aliens:
        if alien.get("phase", 1) == 2:  # **Mini-Boss**
            screen.blit(alien["image"], (int(alien["pos"][0]), int(alien["pos"][1])))  # **Bild aus Alien-Objekt**
        else:
            screen.blit(alien_img, (int(alien["pos"][0]), int(alien["pos"][1])))

def world2_zeichne_boss_lebensbalken(screen, bosses):
    """Zeichne Lebensbalken fuer alle aktiven Bosse."""
    screen_width = pygame.display.get_surface().get_width()
    bar_height = 20
    bar_gap_x = 20  # Horizontaler Abstand zwischen Balken
    bar_gap_y = 10  # Vertikaler Abstand fuer neue Zeilen

    # **Lebensbalken NUR entfernen, wenn ALLE Bosse tot sind**
    if not any(boss["hitpoints"] > 0 for boss in bosses):  
        return  # Falls ALLE tot sind, Balken nicht mehr anzeigen

    if len(bosses) == 1 and bosses[0]["phase"] == 1:
        # **PHASE 1: Grosser Boss mit zentralem Balken**
        bar_width = 400
        x = (screen_width - bar_width) // 2
        y = 10

        boss = bosses[0]
        health_ratio = max(0, boss["hitpoints"] / boss["max_hitpoints"])
        green_width = int(health_ratio * bar_width)

        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))  # Hintergrund (Rot)
        pygame.draw.rect(screen, (0, 255, 0), (x, y, green_width, bar_height))  # HP-Anzeige (Gruen)
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, bar_height), 2)  # Rahmen

    elif len(bosses) >= 1 and all(boss["phase"] == 2 for boss in bosses):
        # **PHASE 2: Zwei Mini-Bosse mit festen Lebensbalken**
        bar_width = 140
        start_x_left = 250  # Feste Position fuer linken Balken
        start_x_right = 430  # Feste Position fuer rechten Balken
        y = 10  # Hoehe bleibt fix

        # Nach Y-Position sortieren, damit der obere Boss links angezeigt wird
        bosses_sorted = sorted(bosses, key=lambda b: b.get("base_y", b["pos"][1]))

        for i, boss in enumerate(bosses_sorted):
            if "bar_position" not in boss:
                boss["bar_position"] = start_x_left if i == 0 else start_x_right

        # **Lebensbalken fuer beide Bosse anzeigen, auch wenn einer tot ist**
        for boss in bosses_sorted:
            x = boss["bar_position"]
            health_ratio = max(0, boss["hitpoints"] / boss["max_hitpoints"])
            green_width = int(health_ratio * bar_width)

            pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))  # Hintergrund (Rot)

            if boss["hitpoints"] > 0:  
                pygame.draw.rect(screen, (0, 255, 0), (x, y, green_width, bar_height))  # Gruener HP-Balken
            else:
                pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))  # **Dunkelrot = Tot, aber sichtbar**

            pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, bar_height), 2)  # Rahmen


def world2_lade_hintergrundmusik(current_stage, sounds):
    """Starte die Musik fuer die aktuelle Stage in Welt 2."""
    musik_key = "world2_boss_music" if current_stage == 6 else "world2_music"
    if musik_key in sounds["music"]:
        musik_datei = sounds["music"][musik_key]
        lade_musik(musik_datei)
        print(f"Hintergrundmusik fuer Stage {current_stage} geladen: {musik_datei}")
    else:
        print(f"Musikschluessel {musik_key} nicht in sounds['music'] gefunden.")

def world2_boss_shooting(aliens, bullets, current_time, bullet_img, sounds, last_shot_time, cooldown, player_pos, delta_time):
    """Lasse den Welt-2-Boss gezielt auf den Spieler schiessen."""
    screen_width = pygame.display.get_surface().get_width()
    screen_height = pygame.display.get_surface().get_height()
    speed_multiplier = 100  # Fuer FPS-unabhaengige Bewegung

    for alien in aliens:
        if alien.get("is_boss", False):  # Nur der Boss kann schiessen
            # **Phase-1-Boss oder Mini-Boss bestimmen**
            if alien.get("phase", 1) == 1:
                boss_width = 240
                boss_height = 180
            else:
                boss_width = 120  # Mini-Boss ist nur halb so gross
                boss_height = 90

            # **Lebenspunkte & Schussintervall anpassen**
            max_hitpoints = alien.get("max_hitpoints", 20)
            current_hitpoints = alien.get("hitpoints", 20)
            health_percentage = (current_hitpoints / max_hitpoints) * 100

            base_shoot_interval = alien.get("shoot_interval", 3000)

            # **Schussfrequenz anpassen (aggressiver bei weniger HP)**
            if health_percentage <= 33:
                shoot_interval = max(300, base_shoot_interval // 3)
            elif health_percentage <= 66:
                shoot_interval = max(500, base_shoot_interval // 2)
            else:
                shoot_interval = base_shoot_interval

            # **Schiessen, wenn genug Zeit vergangen ist**
            if current_time - alien.get("last_shot_time", 0) >= shoot_interval:
                alien["last_shot_time"] = current_time

                # **Schussposition fuer Phase-1 oder Phase-2-Bosse**
                bullet_x = alien["pos"][0] + (boss_width // 2) - (bullet_img.get_width() // 2)
                bullet_y = alien["pos"][1] + (boss_height // 2)  # Schuss soll aus der Mitte kommen

                # **Zielberechnung: Spieler-Hitbox zentrieren**
                player_x, player_y = player_pos
                player_center_x = player_x + (70 // 2)  # Spielerbreite = 70
                player_center_y = player_y + (46 // 2)  # Spielerhoehe = 46

                dx = player_center_x - bullet_x
                dy = player_center_y - bullet_y

                # **Richtung normalisieren**
                distance = math.hypot(dx, dy)
                if distance == 0:
                    distance = 0.001  # Vermeidung von Division durch 0

                dx /= distance
                dy /= distance

                # **Winkelkorrektur beibehalten**
                angle_correction_factor = 1.3
                dx *= angle_correction_factor

                corrected_distance = math.hypot(dx, dy)
                dx /= corrected_distance
                dy /= corrected_distance

                # **Schussgeschwindigkeit anpassen**
                speed = alien.get("bullet_speed", 3)
                bullet_dx = dx * speed
                bullet_dy = dy * speed

                # **Schuss zur Liste hinzufuegen**
                bullets.append({"pos": [bullet_x, bullet_y], "img": bullet_img, "dx": bullet_dx, "dy": bullet_dy})

                # **Schuss-Sound**
                if current_time - last_shot_time >= cooldown:
                    sounds["effects"]["alien_shoot"].set_volume(sounds["volumes"]["effects_volume"])
                    sounds["effects"]["alien_shoot"].play()

    # **Bewege bestehende Schuesse**
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet.get("dx", 0) * delta_time * speed_multiplier
        bullet["pos"][1] += bullet.get("dy", 5) * delta_time * speed_multiplier

        if bullet["pos"][1] >= screen_height or bullet["pos"][1] <= 0:
            bullets.remove(bullet)

    return bullets

def world2_handle_erste_welle(aliens, speed_x, screen_width, delta_time, alien_bullets, bullet_img, sounds, current_time, global_last_shot_time):
    """Bewege und lasse Aliens der ersten Welle schiessen."""
    speed_multiplier = 100  # Kontrolle der Bewegungsgeschwindigkeit

    for alien in aliens:
        # FPS-unabhaengige horizontale Bewegung basierend auf der Richtung
        direction = alien.get("direction", 1)  # Standard: nach rechts
        alien["pos"][0] += direction * speed_x * delta_time * speed_multiplier

        # Wrap-Around-Logik basierend auf der Bewegungsrichtung
        if direction == 1:  # Bewegung nach rechts
            if alien["pos"][0] > screen_width:
                alien["pos"][0] = -40  # Wieder links erscheinen
                alien["pos"][1] += 20  # Optional: leicht nach unten rutschen
        else:  # Bewegung nach links
            if alien["pos"][0] < -40:
                alien["pos"][0] = screen_width  # Wieder rechts erscheinen
                alien["pos"][1] += 20  # Optional: leicht nach unten rutschen

    # Schusslogik mit globalem Cooldown
    alien_bullets, global_last_shot_time = world2_handle_alien_shooting(
        aliens, alien_bullets, current_time, bullet_img, delta_time, sounds, global_last_shot_time
    )

    return aliens, speed_x, alien_bullets, global_last_shot_time

def world2_handle_zweite_welle(
    aliens,
    zweite_welle,
    speed_x,
    screen_width,
    max_depth=50,
    delta_time=0.016,
    alien_bullets=None,
    bullet_img=None,
    sounds=None,
    current_time=0,
    global_last_shot_time=0,
):
    """Handle the second wave of aliens in world 2."""

    alien_width = 40
    alien_height = 36
    spacing = 80
    speed_multiplier = 100

    if not aliens and not zweite_welle.get("started", False):
        links = []
        rechts = []

        for row in range(2):
            for col in range(8):
                x_offset = col * spacing
                y_offset = row * (alien_height + 20)

                alien = {
                    "pos": [0 + x_offset, 0 + y_offset]
                    if (row + col) % 2 == 0
                    else [screen_width - alien_width - x_offset, 0 + y_offset],
                    "dx": speed_x * 0.5 if (row + col) % 2 == 0 else -speed_x * 0.5,
                    "dy": 0.5,
                    "last_shot_time": 0,
                }

                if (row + col) % 2 == 0:
                    links.append(alien)
                else:
                    rechts.append(alien)

        zweite_welle = {
            "links": links,
            "rechts": rechts,
            "completed": False,
            "started": True,
        }

    if zweite_welle.get("started", False):
        if delta_time == 0:
            if not zweite_welle["links"] and not zweite_welle["rechts"]:
                zweite_welle["completed"] = True
            return zweite_welle, speed_x, False, alien_bullets, global_last_shot_time

        alien_reached_player = False

        def bewege_und_schiess_aliens(alien_list):
            nonlocal alien_reached_player, alien_bullets, global_last_shot_time
            for alien in alien_list:
                alien["pos"][0] += alien["dx"] * delta_time * speed_multiplier
                alien["pos"][1] += alien["dy"] * delta_time * (speed_multiplier / 2)

                if alien["pos"][0] <= 0:
                    alien["pos"][0] = 0
                    alien["dx"] *= -1
                elif alien["pos"][0] >= screen_width - alien_width:
                    alien["pos"][0] = screen_width - alien_width
                    alien["dx"] *= -1

                if alien["pos"][1] + alien_height >= max_depth:
                    alien_reached_player = True

            alien_bullets, global_last_shot_time = world2_handle_alien_shooting(
                alien_list,
                alien_bullets,
                current_time,
                bullet_img,
                delta_time,
                sounds,
                global_last_shot_time,
            )

        bewege_und_schiess_aliens(zweite_welle["links"])
        bewege_und_schiess_aliens(zweite_welle["rechts"])

        if not zweite_welle["links"] and not zweite_welle["rechts"]:
            zweite_welle["completed"] = True

        return (
            zweite_welle,
            speed_x,
            alien_reached_player,
            alien_bullets,
            global_last_shot_time,
        )

    return zweite_welle, speed_x, False, alien_bullets, global_last_shot_time
