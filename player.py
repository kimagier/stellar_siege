# -*- coding: utf-8 -*-
import pygame

# Globale Konstanten fuer die Spielergroesse
player_width = 70    # Nach der Skalierung (35 * 2)
player_height = 46   # Nach der Skalierung (23 * 2)

def bewege_spieler(player_x, keys, speed, screen_width, player_width, delta_time):
    """Bewege den Spieler horizontal basierend auf Tasteneingaben."""
    speed_multiplier = 100  # Geschwindigkeitsskala fuer fluessige Steuerung

    if keys[pygame.K_LEFT]:
        player_x -= speed * delta_time * speed_multiplier  # Bewegung nach links
    if keys[pygame.K_RIGHT]:
        player_x += speed * delta_time * speed_multiplier  # Bewegung nach rechts

    # Dynamische Begrenzung basierend auf Bildschirm- und Spielergroesse
    return max(0, min(player_x, screen_width - player_width))

def zeichne_spieler(screen, x, y, player_img, debug=False):
    """Zeichne den Spieler und optional seine Hitbox."""
    screen.blit(player_img, (x, y))  # Spieler auf Bildschirm zeichnen
    
    # Debug: Hitbox sichtbar machen (optional)
    if debug:
        hitbox = get_player_hitbox(x, y)
        pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)  # Rote Hitbox

def lade_spieler_img():
    """Lade das Spielerbild und initiale Positionsdaten."""
    player_img = pygame.image.load("raumschiff.png")  # Spielerbild laden
    player_img = pygame.transform.scale(player_img, (player_width, player_height))  # Bild skalieren
    player_x, player_y = 375, 500  # Startposition des Spielers
    player_speed = 3  # Geschwindigkeit des Spielers
    return player_img, player_x, player_y, player_speed

# Neue Funktion: Hitbox des Spielers basierend auf der Bildgroesse
def get_player_hitbox(player_x, player_y):
    """Gib die aktuelle Hitbox des Spielers zurueck."""
    scale_factor = 2  # Da wir das Bild verdoppelt haben
    hitbox_width = 35 * scale_factor  # 70
    hitbox_height = 23 * scale_factor  # 46

    hitbox_offset_x = 0  # Kein Offset noetig, da das Bild exakt zugeschnitten ist
    hitbox_offset_y = 0

    return pygame.Rect(player_x + hitbox_offset_x, player_y + hitbox_offset_y, hitbox_width, hitbox_height)


def update_motion_trail(trail, position=None, max_length=5):
    """Return updated list of recent player positions.

    If ``position`` is ``None``, the trail is shortened by one element,
    creating a retracting effect when the player stops moving.
    """
    if position is not None:
        trail.append(position)
    elif trail:
        trail.pop(0)
    while len(trail) > max_length:
        trail.pop(0)
    return trail


def draw_motion_trail(screen, trail, player_img):
    """Draw a fading trail behind the player."""
    length = len(trail)
    for index, (x_pos, y_pos) in enumerate(trail):
        alpha = int(255 * (index + 1) / (length + 1))
        trail_img = player_img.copy()
        trail_img.set_alpha(alpha)
        screen.blit(trail_img, (x_pos, y_pos))

def handle_player_shots(
    bullets,
    bullet_speed,
    aliens,
    score,
    collision_margin_small,
    collision_margin_boss,
    sounds,
    player_x,
    player_y,
    screen,
    delta_time,
    bullet_img=None,
    reflected_bullets=None,
    bullet_damage=1,
):
    """Update player bullets, handle collisions and reflections."""
    bullet_width = bullet_img.get_width() if bullet_img else 5
    bullet_height = bullet_img.get_height() if bullet_img else 15

    updated_bullets = []
    for bullet in bullets:
        bullet["y"] -= bullet_speed * delta_time * 100

        if bullet["y"] <= 0:
            score = max(0, score - 10)
            continue

        bullet_rect = pygame.Rect(bullet["x"], bullet["y"], bullet_width, bullet_height)

        hit = False
        for alien in aliens[:]:
            alien_pos = alien.get("pos", [0, 0])
            img = alien.get("image")
            if img is not None:
                alien_width = img.get_width()
                alien_height = img.get_height()
            else:
                if alien.get("is_boss", False):
                    if alien.get("phase", 1) == 2:
                        alien_width = 120
                        alien_height = 90
                    else:
                        alien_width = 240
                        alien_height = 180
                else:
                    alien_width = 40
                    alien_height = 36

            alien_rect = pygame.Rect(alien_pos[0], alien_pos[1], alien_width, alien_height)

            if bullet_rect.colliderect(alien_rect):
                if alien.get("shield_active"):
                    if reflected_bullets is not None and bullet_img is not None:
                        reflected_bullets.append({"pos": [bullet["x"], bullet["y"]], "img": bullet_img})
                    hit = True
                    break

                if not alien.get("is_invulnerable", False):
                    sounds["effects"]["hit"].set_volume(sounds["volumes"]["effects_volume"])
                    sounds["effects"]["hit"].play()

                    if alien.get("hitpoints", 1) > bullet_damage:
                        alien["hitpoints"] -= bullet_damage
                    else:
                        if alien.get("is_boss", False) and alien.get("phase", 1) == 1:
                            alien["hitpoints"] = 0
                            alien["defeated"] = True
                        else:
                            if alien.get("split_on_death") and alien.get("split_callback"):
                                alien["split_callback"](alien, aliens)
                            aliens.remove(alien)

                    score += 10
                    hit = True
                    break

        if not hit:
            updated_bullets.append(bullet)

    return updated_bullets, score