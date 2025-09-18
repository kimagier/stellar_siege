# -*- coding: utf-8 -*-
"""World 3 alien logic for Stellar Siege."""

import random
import math
import pygame
from world2 import world2_handle_alien_shooting, apply_color_filter
from player import player_width, player_height
from sounds import lade_musik

# Dimensions of the standard world 3 alien image
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 36


def world3_lade_hintergrundbild():
    """Load the background image for world 3."""
    return pygame.image.load("world3.jpg")


def world3_lade_alien_img(current_stage):
    """Load the appropriate alien image for world 3."""
    alien_img = pygame.image.load("alien3.png")
    if current_stage == 9:
        alien_img = pygame.transform.scale(alien_img, (240, 180))
    else:
        alien_img = pygame.transform.scale(alien_img, (40, 36))
    return alien_img


def world3_erstelle_stage_3_1_aliens():
    """Create the alien formation for stage 3-1."""
    return world3_erstelle_aliens(5, 6, 80, 20, 80, 60)


def world3_erstelle_stage_3_2_aliens():
    """Create a V-shaped alien formation for stage 3-2."""
    aliens = []
    rows = 4
    spacing_x = 50
    spacing_y = 40
    start_y = 60
    screen_width = pygame.display.get_surface().get_width()

    for row in range(rows):
        num_aliens = 7 - 2 * row
        start_x = (screen_width - (num_aliens * ALIEN_WIDTH + (num_aliens - 1) * spacing_x)) // 2
        for col in range(num_aliens):
            x = start_x + col * (spacing_x + ALIEN_WIDTH)
            y = start_y + row * (spacing_y + ALIEN_HEIGHT)

            alien = {
                "pos": [x, y],
                "hitpoints": 1,
                "is_boss": False,
                "split_on_death": True,
                "split_callback": world3_split_alien,
                "can_shoot": True,
                "is_tip": row == rows - 1 and col == num_aliens // 2,
            }
            if alien["is_tip"]:
                alien["base_x"] = x
                alien["base_y"] = y
            aliens.append(alien)
    return aliens


def world3_erstelle_stage_3_3_aliens():
    """Create the boss for stage 3-3."""
    screen_width = pygame.display.get_surface().get_width()
    boss_width, boss_height = 240, 180
    return [
        {
            # Start ausserhalb des Bildschirms fuer den Einflugeffekt
            "pos": [screen_width // 2 - boss_width // 2, -boss_height],
            "hitpoints": 40,
            "max_hitpoints": 40,
            "is_boss": True,
            "image": pygame.transform.scale(pygame.image.load("alien3.png"), (boss_width, boss_height)),
            "split_on_death": True,
            "split_callback": world3_split_boss,
            "direction": 1,
            "speed_multiplier": 1.0,
            "shoot_interval": 2000,
            "last_shot_time": 0,
            "shield_active": False,
            "shield_duration": 3000,
            "shield_cooldown": (5000, 10000),
            "next_shield_time": pygame.time.get_ticks() + random.randint(5000, 10000),
            "flicker_duration": 500,
            "split_level": 0,
            "bullet_speed": 5,
            # Zusaetzliche Attribute fuer das Einfliegen und spaetere Anpassungen
            "is_invulnerable": True,
            "is_entering": True,
            "entry_speed": 1,
            "target_y": 80,
            "phase": 0,
            "speed_stage": 0,
        }
    ]


def world3_erstelle_aliens(rows, cols, start_x, start_y, spacing_x, spacing_y):
    """Generate a grid of aliens for world 3."""
    aliens = []
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (spacing_x + ALIEN_WIDTH)
            y = start_y + row * (spacing_y + ALIEN_HEIGHT)

            alien = {
                "pos": [x, y],
                "hitpoints": 1,
                "is_boss": False,
                "split_on_death": True,
                "split_callback": world3_split_alien,
                "can_shoot": True,
            }
            aliens.append(alien)
    return aliens


def world3_split_alien(alien, aliens):
    """Split a defeated alien into two smaller orange variants."""
    x, y = alien["pos"]
    offset = 15

    base_img = pygame.image.load("alien3.png")
    small_img = pygame.transform.scale(base_img, (20, 18))
    small_img = apply_color_filter(small_img, (255, 165, 0))

    for direction in (-offset, offset):
        new_alien = {
            "pos": [x + direction, y],
            "hitpoints": 1,
            "is_boss": False,
            "split_on_death": False,
            "can_shoot": True,
            "image": small_img,
            "initial_x": x + direction,
            "initial_y": y,
            "wave_offset": random.uniform(0, 2 * math.pi),
        }
        aliens.append(new_alien)


def world3_split_boss(alien, aliens):
    """Split the stage 3-3 boss into smaller variants without overlap."""
    level = alien.get("split_level", 0)
    base_img = pygame.image.load("alien3.png")
    if level == 0:
        size = (120, 90)
        hp = 20
        shield_duration = 2000
        cooldown = (4000, 8000)
        next_level = 1
        split = True
    elif level == 1:
        size = (60, 45)
        hp = 10
        shield_duration = 1000
        cooldown = (3000, 6000)
        next_level = 2
        split = False
    else:
        return

    spawn_y = alien["pos"][1]
    screen_width = pygame.display.get_surface().get_width()
    spacing = 20
    width_new = size[0]
    group_width = 2 * width_new + spacing
    old_center = alien["pos"][0] + alien.get("image").get_width() // 2
    group_left = max(0, min(int(old_center - group_width / 2), screen_width - group_width))
    positions = [group_left, group_left + width_new + spacing]

    for direction, new_x in zip((-1, 1), positions):
        img = pygame.transform.scale(base_img, size)
        new_alien = {
            "pos": [new_x, spawn_y],
            "hitpoints": hp,
            "max_hitpoints": hp,
            "is_boss": True,
            "image": img,
            "split_on_death": split,
            "split_callback": world3_split_boss if split else None,
            "direction": direction,
            "speed_multiplier": alien.get("speed_multiplier", 1.0) * 1.1,
            "shoot_interval": alien.get("shoot_interval", 2000),
            "last_shot_time": 0,
            "shield_active": False,
            "shield_duration": shield_duration,
            "shield_cooldown": cooldown,
            "next_shield_time": pygame.time.get_ticks() + random.randint(*cooldown),
            "flicker_duration": 500,
            "split_level": next_level,
            "bullet_speed": alien.get("bullet_speed", 5),
            "is_invulnerable": False,
            "is_entering": False,
            "phase": 0,
            "speed_stage": alien.get("speed_stage", 0),
        }
        aliens.append(new_alien)


def world3_erstelle_kreis_formation(center, radius, count=12):
    """Create aliens arranged in a circular formation."""
    aliens = []
    for i in range(count):
        angle = 2 * math.pi * i / count
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)

        aliens.append(
            {
                "pos": [x, y],
                "hitpoints": 1,
                "is_boss": False,
                "split_on_death": True,
                "split_callback": world3_split_alien,
                "can_shoot": True,
                "angle": angle,
            }
        )
    return aliens


def world3_bewege_aliens(aliens, alien_speed_y, screen_width, delta_time):
    """Wobble aliens around their spawn positions without descending."""
    wave_amplitude = 40
    wave_speed = 2000

    for alien in aliens:
        if "initial_x" not in alien:
            alien["initial_x"] = alien["pos"][0]
        if "initial_y" not in alien:
            alien["initial_y"] = alien["pos"][1]
        if "wave_offset" not in alien:
            alien["wave_offset"] = random.uniform(0, 2 * math.pi)

        t = pygame.time.get_ticks() + alien["wave_offset"] * wave_speed
        horizontal_offset = wave_amplitude * math.sin(t / wave_speed)
        vertical_offset = (wave_amplitude / 2) * math.sin(t / (wave_speed * 1.5))
        jitter_x = random.uniform(-1, 1)
        jitter_y = random.uniform(-0.5, 0.5)

        img = alien.get("image", world3_lade_alien_img(7))
        width, height = img.get_width(), img.get_height()

        alien["pos"][0] = alien["initial_x"] + horizontal_offset + jitter_x
        alien["pos"][1] = alien["initial_y"] + vertical_offset + jitter_y

        alien["pos"][0] = max(0, min(alien["pos"][0], screen_width - width))
        screen_height = pygame.display.get_surface().get_height()
        alien["pos"][1] = max(0, min(alien["pos"][1], screen_height - height))

    return aliens


def world3_handle_alien_shooting(
    aliens,
    alien_bullets,
    current_time,
    bullet_img,
    delta_time,
    sounds,
    global_last_shot_time,
):
    """Handle alien shooting for world 3 with centered bullets."""
    screen_height = pygame.display.get_surface().get_height()
    shooting_chance = 0.01
    bullet_speed = 5
    speed_multiplier = 100
    alien_cooldown = 3000
    global_cooldown = 1000

    if len(alien_bullets) < 2 and (
        current_time - global_last_shot_time >= global_cooldown
    ):
        random.shuffle(aliens)
        for alien in aliens:
            if not alien.get("is_boss", False):
                if "last_shot_time" not in alien:
                    alien["last_shot_time"] = 0

                if current_time - alien["last_shot_time"] >= alien_cooldown:
                    if random.random() < shooting_chance:
                        img = alien.get("image", world3_lade_alien_img(7))
                        width = img.get_width()
                        height = img.get_height()
                        bullet_x = alien["pos"][0] + width // 2
                        bullet_y = alien["pos"][1] + height

                        alien_bullets.append(
                            {
                                "start_x": bullet_x,
                                "pos": [bullet_x, bullet_y],
                                "img": bullet_img,
                                "dy": bullet_speed,
                            }
                        )

                        alien["last_shot_time"] = current_time
                        global_last_shot_time = current_time

                        sounds["effects"]["alien_shoot_klein"].set_volume(
                            sounds["volumes"]["effects_volume"]
                        )
                        sounds["effects"]["alien_shoot_klein"].play()

                        break

    for bullet in alien_bullets[:]:
        bullet["pos"][1] += bullet["dy"] * delta_time * speed_multiplier
        bullet["pos"][0] = bullet["start_x"]
        if bullet["pos"][1] > screen_height:
            alien_bullets.remove(bullet)

    return alien_bullets, global_last_shot_time


def world3_zeichne_aliens(screen, aliens, alien_img):
    """Draw aliens for world 3."""
    for alien in aliens:
        img = alien.get("image", alien_img)
        x = int(alien["pos"][0])
        y = int(alien["pos"][1])
        screen.blit(img, (x, y))
        if alien.get("shield_active") or (
            "shield_flicker_start" in alien and (pygame.time.get_ticks() // 100) % 2 == 0
        ):
            radius = max(img.get_width(), img.get_height()) // 2 + 5
            center = (x + img.get_width() // 2, y + img.get_height() // 2)
            pygame.draw.circle(screen, (160, 32, 240), center, radius, 2)


def world3_handle_stage_3_2(aliens, state, screen_width, delta_time, current_time):
    """Update movement for stage 3-2 including both waves."""
    speed_multiplier = 100

    if state.get("phase", 1) == 1:
        formation_aliens = [a for a in aliens if "wave_offset" not in a]
        for alien in formation_aliens:
            alien["pos"][0] += state.get("direction", 1) * delta_time * speed_multiplier
            if alien.get("is_tip"):
                alien["base_x"] += state.get("direction", 1) * delta_time * speed_multiplier

        if formation_aliens:
            left = min(a["pos"][0] for a in formation_aliens)
            right = max(a["pos"][0] + ALIEN_WIDTH for a in formation_aliens)
            if left <= 0 or right >= screen_width:
                state["direction"] = -state.get("direction", 1)
                move_down = ALIEN_HEIGHT // 2
                overshoot = 0
                if left <= 0:
                    overshoot = -left
                elif right >= screen_width:
                    overshoot = screen_width - right
                for alien in formation_aliens:
                    alien["pos"][1] += move_down
                    alien["pos"][0] += overshoot
                    if alien.get("is_tip"):
                        alien["base_y"] += move_down
                        alien["base_x"] += overshoot

        tip_offset = 15 * math.sin(current_time / 500)
        for alien in formation_aliens:
            if alien.get("is_tip"):
                alien["pos"][0] = alien.get("base_x", alien["pos"][0]) + tip_offset

        small_aliens = [a for a in aliens if "wave_offset" in a]
        if small_aliens:
            small_aliens = world3_bewege_aliens(small_aliens, 0, screen_width, delta_time)
        aliens = formation_aliens + small_aliens

        if not aliens:
            state["phase"] = 2
            state["center"] = [screen_width // 2, -100]
            state["target_center"] = [screen_width // 2, 150]
            state["direction"] = 1
            state["radius"] = 80
            state["base_radius"] = 80
            state["start_time"] = current_time
            state["entering"] = True
            aliens.extend(world3_erstelle_kreis_formation(state["center"], state["radius"]))
    else:
        center = state.get("center", [screen_width // 2, 150])
        target_center = state.get("target_center", [screen_width // 2, 150])
        radius_base = state.get("base_radius", 80)
        radius = radius_base + 20 * math.sin(current_time / 1000)
        rotation_speed = 1

        circle_aliens = [a for a in aliens if "angle" in a]
        split_aliens = [a for a in aliens if "wave_offset" in a and "angle" not in a and "dx" not in a]
        if split_aliens:
            split_aliens = world3_bewege_aliens(split_aliens, 0, screen_width, delta_time)

        if state.get("entering", False):
            # Accelerate entry of the circle formation for a snappier appearance
            center[1] += delta_time * speed_multiplier * 0.8
            if center[1] >= target_center[1]:
                center[1] = target_center[1]
                state["entering"] = False
            for alien in circle_aliens:
                alien["angle"] += rotation_speed * delta_time
                alien["pos"][0] = center[0] + radius * math.cos(alien["angle"])
                alien["pos"][1] = center[1] + radius * math.sin(alien["angle"])
        elif not state.get("dissolved", False):
            center[0] += state.get("direction", 1) * delta_time * speed_multiplier * 0.5
            center[1] = min(center[1] + delta_time * speed_multiplier * 0.1, target_center[1])
            if center[0] - radius <= 0:
                center[0] = radius
                state["direction"] = 1
            elif center[0] + radius >= screen_width:
                center[0] = screen_width - radius
                state["direction"] = -1

            for alien in circle_aliens:
                alien["angle"] += rotation_speed * delta_time
                alien["pos"][0] = center[0] + radius * math.cos(alien["angle"])
                alien["pos"][1] = center[1] + radius * math.sin(alien["angle"])

            if current_time - state.get("start_time", 0) > 6000:
                state["dissolved"] = True
                for alien in circle_aliens:
                    alien["dx"] = state.get("direction", 1)
                    alien["dy"] = 0.4
        else:
            for alien in circle_aliens:
                alien["pos"][0] += alien.get("dx", 0) * delta_time * speed_multiplier
                alien["pos"][1] += alien.get("dy", 0) * delta_time * (speed_multiplier / 2)
                if alien["pos"][0] <= 0 or alien["pos"][0] >= screen_width - ALIEN_WIDTH:
                    alien["dx"] *= -1
                if alien["pos"][1] >= 400 or alien["pos"][1] <= 0:
                    alien["dy"] *= -1

        state["center"] = center
        aliens = circle_aliens + split_aliens

    return aliens, state


def world3_boss_shooting(bosses, bullets, current_time, bullet_img, sounds, last_shot_time, cooldown, player_pos, delta_time):
    """Let world 3 bosses shoot at the player."""
    screen_width = pygame.display.get_surface().get_width()
    screen_height = pygame.display.get_surface().get_height()
    speed_multiplier = 100

    for boss in bosses:
        if current_time - boss.get("last_shot_time", 0) >= boss.get("shoot_interval", 2000):
            boss["last_shot_time"] = current_time
            width = boss["image"].get_width()
            height = boss["image"].get_height()

            bullet_x = boss["pos"][0] + width // 2 - bullet_img.get_width() // 2
            bullet_y = boss["pos"][1] + height // 2

            player_x, player_y = player_pos
            dx = player_x + player_width // 2 - bullet_x
            dy = player_y + player_height // 2 - bullet_y
            distance = math.hypot(dx, dy) or 0.001
            dx /= distance
            dy /= distance
            angle_correction_factor = 1.3
            dx *= angle_correction_factor
            corrected_distance = math.hypot(dx, dy)
            dx /= corrected_distance
            dy /= corrected_distance

            speed = boss.get("bullet_speed", 5)
            bullet_dx = dx * speed
            bullet_dy = dy * speed

            bullets.append({"pos": [bullet_x, bullet_y], "img": bullet_img, "dx": bullet_dx, "dy": bullet_dy})

            if current_time - last_shot_time >= cooldown:
                sounds["effects"]["alien_shoot"].set_volume(sounds["volumes"]["effects_volume"])
                sounds["effects"]["alien_shoot"].play()

    for bullet in bullets[:]:
        bullet["pos"][0] += bullet.get("dx", 0) * delta_time * speed_multiplier
        bullet["pos"][1] += bullet.get("dy", 5) * delta_time * speed_multiplier
        if (
            bullet["pos"][1] >= screen_height
            or bullet["pos"][1] <= 0
            or bullet["pos"][0] <= 0
            or bullet["pos"][0] >= screen_width
        ):
            bullets.remove(bullet)

    return bullets


def world3_handle_boss(aliens, alien_bullets, current_time, bullet_img, sounds, player_pos, delta_time, screen_width):
    """Move stage 3-3 bosses and manage shield timers."""
    speed_multiplier = 100

    for alien in aliens:
        if not alien.get("is_boss", False):
            continue

        img = alien.get("image")
        width = img.get_width()

        if "direction" not in alien:
            alien["direction"] = 1

        # Einflugphase: Boss ist unbesiegbar und bewegt sich nach unten
        if alien.get("is_entering", False):
            alien["pos"][1] += alien.get("entry_speed", 1) * delta_time * speed_multiplier
            alien["is_invulnerable"] = True
            if alien["pos"][1] >= alien.get("target_y", 80):
                alien["pos"][1] = alien.get("target_y", 80)
                alien["is_invulnerable"] = False
                alien["is_entering"] = False
                alien["last_shot_time"] = current_time
        else:
            alien["pos"][0] += alien["direction"] * delta_time * speed_multiplier * alien.get("speed_multiplier", 1.0)

        if alien["pos"][0] <= 0 or alien["pos"][0] >= screen_width - width:
            alien["pos"][0] = max(0, min(alien["pos"][0], screen_width - width))
            alien["direction"] *= -1

        # Geschwindigkeitserhoehung und kuerzere Schildpausen bei 25%-Schritten
        hp_ratio = alien.get("hitpoints", 0) / alien.get("max_hitpoints", 1)
        thresholds = [0.75, 0.5, 0.25]
        stage = alien.get("speed_stage", 0)
        if stage < len(thresholds) and hp_ratio <= thresholds[stage]:
            alien["speed_multiplier"] *= 1.2
            cooldown = alien.get("shield_cooldown", (5000, 10000))
            alien["shield_cooldown"] = (int(cooldown[0] * 0.8), int(cooldown[1] * 0.8))
            alien["speed_stage"] = stage + 1

        if not alien.get("shield_active", False):
            if current_time >= alien.get("next_shield_time", 0):
                if "shield_flicker_start" not in alien:
                    alien["shield_flicker_start"] = current_time
                elif current_time - alien["shield_flicker_start"] >= alien.get("flicker_duration", 500):
                    alien["shield_active"] = True
                    alien["shield_end_time"] = current_time + alien.get("shield_duration", 3000)
                    alien.pop("shield_flicker_start", None)
        else:
            if current_time >= alien.get("shield_end_time", 0):
                alien["shield_active"] = False
                alien["next_shield_time"] = current_time + random.randint(*alien.get("shield_cooldown", (5000, 10000)))

    bosses = [a for a in aliens if a.get("is_boss", False)]
    for i, boss_a in enumerate(bosses):
        img_a = boss_a.get("image")
        rect_a = pygame.Rect(boss_a["pos"][0], boss_a["pos"][1], img_a.get_width(), img_a.get_height())
        for boss_b in bosses[i + 1 :]:
            img_b = boss_b.get("image")
            rect_b = pygame.Rect(boss_b["pos"][0], boss_b["pos"][1], img_b.get_width(), img_b.get_height())
            if rect_a.colliderect(rect_b):
                overlap = rect_a.clip(rect_b).width / 2 + 1
                if boss_a["pos"][0] < boss_b["pos"][0]:
                    boss_a["pos"][0] -= overlap
                    boss_b["pos"][0] += overlap
                    boss_a["direction"] = -1
                    boss_b["direction"] = 1
                else:
                    boss_a["pos"][0] += overlap
                    boss_b["pos"][0] -= overlap
                    boss_a["direction"] = 1
                    boss_b["direction"] = -1

                boss_a["pos"][0] = max(0, min(boss_a["pos"][0], screen_width - img_a.get_width()))
                boss_b["pos"][0] = max(0, min(boss_b["pos"][0], screen_width - img_b.get_width()))

    alien_bullets = world3_boss_shooting(
        [a for a in aliens if a.get("is_boss", False)],
        alien_bullets,
        current_time,
        bullet_img,
        sounds,
        0,
        300,
        player_pos,
        delta_time,
    )

    return aliens, alien_bullets


def world3_zeichne_boss_lebensbalken(screen, bosses):
    """Draw health bars for stage 3-3 bosses."""
    screen_width = pygame.display.get_surface().get_width()
    bar_height = 20

    if not any(b["hitpoints"] > 0 for b in bosses):
        return

    bar_width = 160 if len(bosses) > 1 else 400
    gap = 20
    total_width = len(bosses) * (bar_width + gap) - gap
    start_x = (screen_width - total_width) // 2
    for i, boss in enumerate(bosses):
        x = start_x + i * (bar_width + gap)
        y = 10
        health_ratio = max(0, boss["hitpoints"] / boss["max_hitpoints"])
        green_width = int(health_ratio * bar_width)
        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (x, y, green_width, bar_height))
        border_color = (160, 32, 240) if boss.get("shield_active") else (0, 0, 0)
        pygame.draw.rect(screen, border_color, (x, y, bar_width, bar_height), 2)

def world3_lade_hintergrundmusik(current_stage, sounds):
    """Play the background music for world 3."""
    musik_key = "world3_boss_music" if current_stage == 9 else "world3_music"
    if musik_key in sounds["music"]:
        musik_datei = sounds["music"][musik_key]
        lade_musik(musik_datei)
    else:
        print(f"Musikschluessel {musik_key} nicht gefunden.")
