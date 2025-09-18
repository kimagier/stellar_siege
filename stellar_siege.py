# -*- coding: utf-8 -*-
import pygame
import time  # Fuer Zeitsteuerung mit time.time()
import highscore
from settings import lade_einstellungen, speichere_einstellungen
from sounds import (
    initialisiere_audio,
    lade_sounds,
    lade_musik,
    setze_soundeffekt_lautstaerke,
    setze_musik_lautstaerke
)
from player import (
    bewege_spieler,
    zeichne_spieler,
    lade_spieler_img,
    handle_player_shots,
    get_player_hitbox,
    update_motion_trail,
    draw_motion_trail,
    player_width,
    player_height
)
from display import (
    BaseScreen,
    MainMenuScreen,
    HighscoreScreen,
    OptionScreen,
    WinScreen,
    LoseScreen,
    PauseMenuScreen
)
from shop import ShopScreen, load_hud_icons, UPGRADES
from highscore import (
    lade_highscores,
    aktualisiere_highscores
)
from world1 import (
    world1_lade_hintergrundbild,
    world1_lade_alien_img,
    world1_erstelle_stage_1_1_aliens,
    world1_erstelle_stage_1_2_aliens,
    world1_erstelle_stage_1_3_aliens,
    world1_erstelle_aliens,
    world1_bewege_aliens,
    world1_bewege_einzelnes_alien,
    world1_zeichne_aliens,
    world1_zeichne_boss_lebensbalken,
    world1_lade_hintergrundmusik,
    world1_handle_boss,
    world1_boss_shooting,
    world1_handle_erste_welle,
    world1_handle_zweite_welle
)
from world2 import (
    world2_lade_hintergrundbild,
    world2_lade_alien_img,
    world2_erstelle_stage_2_1_aliens,
    world2_erstelle_stage_2_2_aliens,
    world2_erstelle_stage_2_3_aliens,
    world2_erstelle_aliens,
    world2_bewege_aliens,
    world2_bewege_einzelnes_alien,
    world2_zeichne_aliens,
    world2_zeichne_boss_lebensbalken,
    world2_lade_hintergrundmusik,
    world2_handle_boss,
    world2_boss_shooting,
    world2_handle_erste_welle,
    world2_handle_zweite_welle,
    world2_handle_alien_shooting,
    apply_color_filter
)
from world3 import (
    world3_lade_hintergrundbild,
    world3_lade_alien_img,
    world3_erstelle_stage_3_1_aliens,
    world3_erstelle_stage_3_2_aliens,
    world3_erstelle_stage_3_3_aliens,
    world3_bewege_aliens,
    world3_zeichne_aliens,
    world3_zeichne_boss_lebensbalken,
    world3_lade_hintergrundmusik,
    world3_handle_alien_shooting,
    world3_handle_stage_3_2,
    world3_handle_boss,
)

TESTMODE = True  # Testmodus aktivieren
god_mode = False  # Persistenter Godmode fuer Tests

# Maximum trail length when speed upgrade is active
# Increased for a more pronounced boost effect
SPEED_TRAIL_LENGTH = 40


def grant_test_points(current_score, amount=1000):
    """Return current_score increased by amount for testing."""
    print(f"Debug: adding {amount} points")
    return current_score + amount

def spiele_level(lade_hintergrund, lade_alien_img, erstelle_aliens, lade_hintergrundmusik, current_level, sounds, score, player_lives, active_upgrades, hud_icons):
    """Runs a single stage and returns the outcome."""
    global god_mode
    print(f"Starte Stage {current_level} mit initialem Score: {score}")
    
    lade_hintergrundmusik(current_level, sounds)

    settings = lade_einstellungen()
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    if settings.get("fullscreen"):
        screen = pygame.display.set_mode((800, 600), flags | pygame.FULLSCREEN, vsync=1)
    else:
        screen = pygame.display.set_mode((800, 600), flags, vsync=1)
    base_screen = BaseScreen(screen)
    win_screen = WinScreen(screen)
    lose_screen = LoseScreen(screen)
    highscore_screen = HighscoreScreen(screen)
    pause_menu = PauseMenuScreen(screen)
    background = pygame.transform.scale(lade_hintergrund(), screen.get_size())
    alien_img = lade_alien_img(current_level)

    player_img, player_x, player_y, player_speed = lade_spieler_img()
    if "speed" in active_upgrades:
        player_speed *= 2

    
    shoot_cooldown = 0.3  # Cooldown in Sekunden
    last_shot_time = 0    # Zeitpunkt des letzten Schusses
    double_shot_delay = 0.1  # Abstand zwischen zwei Kugeln bei "firerate"-Upgrade
    next_shot_time = None  # Zeitpunkt fuer den zweiten Schuss

    shield_available = True if "shield" in active_upgrades else False

    alien_speed_x = 1
    alien_speed_y = 20
    aliens = erstelle_aliens()

    zweite_welle = {"links": [], "rechts": [], "started": False, "completed": False}
    zweite_welle_speed_x = 1.5 if current_level in {2, 5} else None

    stage3_2_state = {"phase": 1, "direction": 1} if current_level == 8 else None

    initial_alien_count = len(aliens)

    # Bullet appearance depends on damage upgrade
    bullet_color = (0, 0, 139)
    bullet_width = 5
    if "damage" in active_upgrades:
        bullet_width = 10
        # Keep empowered shots dark blue as well
        bullet_color = (0, 0, 139)
    bullet_img = pygame.Surface((bullet_width, 15))
    bullet_img.fill(bullet_color)
    player_bullets = []
    bullet_speed = 5

    motion_trail = []
    prev_player_x = player_x

    alien_bullet_img = pygame.Surface((5, 15))
    alien_bullet_img.fill((255, 0, 0))
    alien_bullets = []
    alien_bullet_speed = 5

    # NEU: World 2 Alien-Schuesse initialisieren
    world2_alien_bullets = []  
    world2_alien_bullet_speed = 4  
    global_last_shot_time = 0

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    running = True

    speed_increase_threshold = initial_alien_count * 0.2

    collision_margin_small = {"x": 10, "y": 10}
    collision_margin_boss = {"left": 40, "right": 35, "top": 21, "bottom": 51}

    while running:
        delta_time = clock.tick(0) / 1000.0
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    while paused:
                        pause_result = pause_menu.show(font, sounds)
                        if pause_result == "Resume":
                            clock.tick(0)
                            paused = False
                        elif pause_result == "Highscores":
                            highscore_screen.show(font, lade_highscores(), sounds)
                        elif pause_result == "Options":
                            option_screen = OptionScreen(screen, sounds, settings.get("fullscreen", False))
                            option_screen.show(font)
                            settings = lade_einstellungen()
                            flags = pygame.DOUBLEBUF | pygame.HWSURFACE
                            if settings.get("fullscreen"):
                                screen = pygame.display.set_mode((800, 600), flags | pygame.FULLSCREEN, vsync=1)
                            else:
                                screen = pygame.display.set_mode((800, 600), flags, vsync=1)
                            base_screen.screen = screen
                            win_screen.screen = screen
                            lose_screen.screen = screen
                            highscore_screen.screen = screen
                            pause_menu.screen = screen
                            background = pygame.transform.scale(lade_hintergrund(), screen.get_size())
                            player_img, player_x, player_y, player_speed = lade_spieler_img()
                            if "speed" in active_upgrades:
                                player_speed *= 2
                        elif pause_result == "Exit":
                            pygame.quit()
                            exit()

                if event.key == pygame.K_SPACE:
                    current_time_sec = pygame.time.get_ticks() / 1000
                    if current_time_sec - last_shot_time >= shoot_cooldown:
                        sounds["effects"]["shoot"].set_volume(
                            sounds["volumes"]["effects_volume"]
                        )
                        sounds["effects"]["shoot"].play()
                        start_x = player_x + (player_width // 2) - (bullet_width // 2)
                        start_y = player_y + 5
                        player_bullets.append({"x": start_x, "y": start_y})
                        if "firerate" in active_upgrades:
                            next_shot_time = current_time_sec + double_shot_delay
                        else:
                            next_shot_time = None
                        last_shot_time = current_time_sec

                if TESTMODE and event.key == pygame.K_s:
                    return "Next Stage", score, current_level + 1, player_lives

                if TESTMODE and event.key == pygame.K_g:
                    god_mode = not god_mode
                    print(f"Godmode {'aktiviert' if god_mode else 'deaktiviert'}")

                if TESTMODE and event.key == pygame.K_p:
                    score = grant_test_points(score)

        keys = pygame.key.get_pressed()
        screen_width = screen.get_width()
        player_x = bewege_spieler(
            player_x,
            keys,
            player_speed,
            screen_width,
            player_width,
            delta_time,
        )

        # Zweiten Schuss ausfuehren, falls geplant
        current_time_sec = current_time / 1000
        if next_shot_time is not None and current_time_sec >= next_shot_time:
            sounds["effects"]["shoot"].set_volume(
                sounds["volumes"]["effects_volume"]
            )
            sounds["effects"]["shoot"].play()
            start_x = player_x + (player_width // 2) - (bullet_width // 2)
            start_y = player_y + 5
            player_bullets.append({"x": start_x, "y": start_y})
            next_shot_time = None

        if "speed" in active_upgrades:
            if player_x != prev_player_x:
                motion_trail = update_motion_trail(
                    motion_trail,
                    (player_x, player_y),
                    max_length=SPEED_TRAIL_LENGTH,
                )
            else:
                motion_trail = update_motion_trail(
                    motion_trail,
                    None,
                    max_length=SPEED_TRAIL_LENGTH,
                )
            prev_player_x = player_x
        else:
            motion_trail.clear()
            prev_player_x = player_x

        if current_level in {1, 2, 3}:
            if current_level == 2:
                aliens, alien_speed_x = world1_handle_erste_welle(aliens, alien_speed_x, 800, delta_time)
                zweite_welle, zweite_welle_speed_x, alien_reached_player = world1_handle_zweite_welle(
                    aliens, zweite_welle, zweite_welle_speed_x, 800, max_depth=player_y - 50, delta_time=delta_time
                )
            elif current_level == 3:
                aliens, alien_bullets, alien_speed_x = world1_handle_boss(
                    aliens, alien_bullets, current_time, alien_bullet_img, sounds, (player_x, player_y), alien_speed_x, delta_time
                )
            else:
                aliens, alien_speed_x, _ = world1_bewege_aliens(aliens, alien_speed_x, alien_speed_y, 800, delta_time)

        elif current_level in {4, 5, 6}:
            if current_level == 5:
                # Erste Welle (Parameter anpassen)
                aliens, alien_speed_x, alien_bullets, global_last_shot_time = world2_handle_erste_welle(
                    aliens, alien_speed_x, 800, delta_time,
                    alien_bullets, alien_bullet_img, sounds, current_time, global_last_shot_time
                )
                # Zweite Welle (ebenfalls anpassen)
                zweite_welle, zweite_welle_speed_x, alien_reached_player, alien_bullets, global_last_shot_time = world2_handle_zweite_welle(
                    aliens, zweite_welle, zweite_welle_speed_x, 800,
                    max_depth=player_y - 50,
                    delta_time=delta_time,
                    alien_bullets=alien_bullets,
                    bullet_img=alien_bullet_img,
                    sounds=sounds,
                    current_time=current_time,
                    global_last_shot_time=global_last_shot_time
                )

            elif current_level == 6:
                # Bosskampf in World2
                aliens, alien_bullets, alien_speed_x = world2_handle_boss(
                    aliens,
                    alien_bullets,
                    current_time,
                    alien_bullet_img,
                    sounds,
                    (player_x, player_y),
                    alien_speed_x,
                    delta_time,
                    alien_img,
                )
            else:
                # Normale Alienbewegung fuer Stage 2-1
                aliens, alien_speed_x, _ = world2_bewege_aliens(
                    aliens,
                    alien_speed_x,
                    alien_speed_y,
                    800,
                    delta_time,
                )

            # World 2 Aliens schiessen
            world2_alien_bullets, global_last_shot_time = world2_handle_alien_shooting(
                aliens,
                world2_alien_bullets,
                current_time,
                alien_bullet_img,
                delta_time,
                sounds,
                global_last_shot_time,
            )

        elif current_level in {7, 8, 9}:
            if current_level == 7:
                aliens = world3_bewege_aliens(aliens, alien_speed_y, 800, delta_time)
                world2_alien_bullets, global_last_shot_time = world3_handle_alien_shooting(
                    aliens,
                    world2_alien_bullets,
                    current_time,
                    alien_bullet_img,
                    delta_time,
                    sounds,
                    global_last_shot_time,
                )
            elif current_level == 8:
                aliens, stage3_2_state = world3_handle_stage_3_2(
                    aliens, stage3_2_state, 800, delta_time, current_time
                )
                world2_alien_bullets, global_last_shot_time = world3_handle_alien_shooting(
                    aliens,
                    world2_alien_bullets,
                    current_time,
                    alien_bullet_img,
                    delta_time,
                    sounds,
                    global_last_shot_time,
                )
            else:
                aliens, world2_alien_bullets = world3_handle_boss(
                    aliens,
                    world2_alien_bullets,
                    current_time,
                    alien_bullet_img,
                    sounds,
                    (player_x, player_y),
                    delta_time,
                    800,
                )

        # After player shots update waves/boss phases
        if current_level == 2:
            zweite_welle, zweite_welle_speed_x, _ = world1_handle_zweite_welle(
                aliens, zweite_welle, zweite_welle_speed_x, 800,
                max_depth=player_y - 50, delta_time=0
            )
        elif current_level == 5:
            zweite_welle, zweite_welle_speed_x, _, alien_bullets, global_last_shot_time = world2_handle_zweite_welle(
                aliens, zweite_welle, zweite_welle_speed_x, 800,
                max_depth=player_y - 50, delta_time=0,
                alien_bullets=alien_bullets, bullet_img=alien_bullet_img,
                sounds=sounds, current_time=current_time,
                global_last_shot_time=global_last_shot_time
            )


        for alien_list in [aliens, zweite_welle.get("links", []), zweite_welle.get("rechts", [])]:
            player_bullets, score = handle_player_shots(
                player_bullets,
                bullet_speed,
                alien_list,
                score,
                collision_margin_small,
                collision_margin_boss,
                sounds,
                player_x,
                player_y,
                screen,
                delta_time,
                bullet_img,
                world2_alien_bullets,
                2 if "damage" in active_upgrades else 1,
            )
      
        # Kollisionserkennung fuer World1 Boss-Schuesse
        for alien_bullet in alien_bullets[:]:
            alien_bullet["pos"][0] += alien_bullet.get("dx", 0) * delta_time
            alien_bullet["pos"][1] += alien_bullet.get("dy", 5) * delta_time

            if (
                alien_bullet["pos"][1] >= 600 or alien_bullet["pos"][1] <= 0 or
                alien_bullet["pos"][0] <= 0 or alien_bullet["pos"][0] >= screen_width
            ):
                alien_bullets.remove(alien_bullet)
                continue

            player_hitbox = get_player_hitbox(player_x, player_y)

            bullet_rect = pygame.Rect(
                alien_bullet["pos"][0],
                alien_bullet["pos"][1],
                alien_bullet["img"].get_width(),
                alien_bullet["img"].get_height()
            )

            if player_hitbox.colliderect(bullet_rect) and not god_mode:
                sounds["effects"]["hit"].play()
                score = max(0, score - 100)
                if shield_available:
                    shield_available = False
                    active_upgrades.discard("shield")
                    alien_bullets.remove(alien_bullet)
                    continue
                player_lives -= 1
                active_upgrades.clear()
                if player_lives > 0:
                    return "retry_stage", score, current_level, player_lives
                result = lose_screen.show(font, sounds, score)
                if result == "Retry":
                    return "game_over", 0, 1, 3
                elif result == "Exit":
                    pygame.quit()
                    exit()

        # Kollisionserkennung fuer World2 Alien-Schuesse
        for alien_bullet in world2_alien_bullets[:]:
            alien_bullet["pos"][1] += world2_alien_bullet_speed * delta_time

            if alien_bullet["pos"][1] >= 600:
                world2_alien_bullets.remove(alien_bullet)
                continue

            player_hitbox = get_player_hitbox(player_x, player_y)

            bullet_rect = pygame.Rect(
                alien_bullet["pos"][0],
                alien_bullet["pos"][1],
                alien_bullet["img"].get_width(),
                alien_bullet["img"].get_height()
            )

            if player_hitbox.colliderect(bullet_rect) and not god_mode:
                sounds["effects"]["hit"].play()
                score = max(0, score - 100)
                if shield_available:
                    shield_available = False
                    active_upgrades.discard("shield")
                    world2_alien_bullets.remove(alien_bullet)
                    continue
                player_lives -= 1
                active_upgrades.clear()
                if player_lives > 0:
                    return "retry_stage", score, current_level, player_lives
                result = lose_screen.show(font, sounds, score)
                if result == "Retry":
                    return "game_over", 0, 1, 3
                elif result == "Exit":
                    pygame.quit()
                    exit()

        colliding_aliens = [
            (group, alien)
            for group in [aliens, zweite_welle.get("links", []), zweite_welle.get("rechts", [])]
            for alien in group
            if alien["pos"][1] >= player_y - 50
        ]
        if colliding_aliens and not god_mode:
            sounds["effects"]["game_over"].play()
            score = max(0, score - 100)
            if shield_available:
                shield_available = False
                active_upgrades.discard("shield")
                for group, alien in colliding_aliens:
                    group.remove(alien)
            else:
                player_lives -= 1
                active_upgrades.clear()
                for group, alien in colliding_aliens:
                    group.remove(alien)
                if player_lives > 0:
                    print(f"Du hast noch {player_lives} Leben. Stage wird neu gestartet.")
                    return "retry_stage", score, current_level, player_lives
                result = lose_screen.show(font, sounds, score)
                if result == "Retry":
                    return "game_over", 0, 1, 3
                elif result == "Exit":
                    pygame.quit()
                    exit()

        screen.blit(background, (0, 0))
        if "speed" in active_upgrades:
            draw_motion_trail(screen, motion_trail, player_img)
        zeichne_spieler(screen, player_x, player_y, player_img)
        if shield_available:
            center = (
                int(player_x + player_width / 2),
                int(player_y + player_height / 2),
            )
            radius = max(player_width, player_height) // 2 + 10
            pygame.draw.circle(screen, (0, 150, 255), center, radius, 2)

        for bullet in player_bullets:
            screen.blit(bullet_img, (bullet["x"], bullet["y"]))

        if current_level in {3, 6}:
            for alien in aliens:
                if alien.get("phase") == 2:  # **Phase 2 Bosse: Orange & Halb so gross**
                    mini_boss_img = pygame.transform.scale(alien_img, (120, 90))  # **Halbe Groesse**
                    tinted_images = apply_color_filter(mini_boss_img)  # Korrekt: Gibt ein Dictionary zurueck
                    tinted_img = tinted_images["orange"]  # Das orange eingefaerbte Bild nehmen
                    screen.blit(tinted_img, (int(alien["pos"][0]), int(alien["pos"][1])))
                else:
                    screen.blit(alien_img, (int(alien["pos"][0]), int(alien["pos"][1])))

            if aliens:
                if current_level == 3:
                    world1_zeichne_boss_lebensbalken(screen, aliens[0]["hitpoints"], 20)
                else:
                    # Fuer Stage 6 mehrere Lebensbalken anzeigen
                    bosses = [alien for alien in aliens if alien.get("is_boss", False)]
                    if bosses:
                        world2_zeichne_boss_lebensbalken(screen, bosses)

        elif current_level == 9:
            world3_zeichne_aliens(screen, aliens, alien_img)
            if aliens:
                bosses = [a for a in aliens if a.get("is_boss", False)]
                if bosses:
                    world3_zeichne_boss_lebensbalken(screen, bosses)
        else:
            if current_level in {1, 2, 3}:
                world1_zeichne_aliens(screen, aliens, alien_img)
                if zweite_welle.get("started", False):
                    world1_zeichne_aliens(screen, zweite_welle["links"], alien_img)
                    world1_zeichne_aliens(screen, zweite_welle["rechts"], alien_img)
            elif current_level in {4, 5, 6}:
                world2_zeichne_aliens(screen, aliens, alien_img)
                if zweite_welle.get("started", False):
                    world2_zeichne_aliens(screen, zweite_welle["links"], alien_img)
                    world2_zeichne_aliens(screen, zweite_welle["rechts"], alien_img)
            else:
                world3_zeichne_aliens(screen, aliens, alien_img)

        base_screen.zeichne_punkte(score, font, (255, 255, 255), f"{(current_level - 1) // 3 + 1}-{(current_level - 1) % 3 + 1}")

        # Leben anzeigen (oben rechts)
        life_icon = pygame.transform.scale(player_img, (30, 20))
        screen.blit(life_icon, (710, 10))  # Raumschiff-Symbol
        lives_text = font.render(f"x {player_lives}", True, (255, 255, 255))
        screen.blit(lives_text, (750, 10))

        ordered_upgrades = [
            item["name"]
            for item in UPGRADES
            if item["name"] in active_upgrades and item["name"] != "life"
        ]
        icon_x = 710 - len(ordered_upgrades) * 26 - 10
        for name in ordered_upgrades:
            screen.blit(hud_icons[name], (icon_x, 10))
            icon_x += 26

        for alien_bullet in alien_bullets:
            screen.blit(alien_bullet["img"], (alien_bullet["pos"][0], alien_bullet["pos"][1]))

        for bullet in world2_alien_bullets:
            screen.blit(alien_bullet_img, (bullet["pos"][0], bullet["pos"][1]))

        pygame.display.flip()

        remaining_aliens = len(aliens)
        if initial_alien_count - remaining_aliens >= speed_increase_threshold:
            alien_speed_x *= 1.2
            initial_alien_count -= speed_increase_threshold

        # Pruefen, ob ALLE Aliens besiegt sind (einschliesslich zweite Welle)
        # Bei Stage 3-2 darf die zweite Welle erst nach Phase 1 gestartet werden
        if not aliens and (
            current_level not in {2, 5} or zweite_welle.get("completed", False)
        ) and (current_level != 8 or stage3_2_state.get("phase", 1) != 1):
            stage_name = f"{(current_level - 1) // 3 + 1}-{(current_level - 1) % 3 + 1}"
            result = win_screen.show(stage_name, font, sounds, score)
            if result == "Shop":
                return "Shop", score, current_level + 1, player_lives
            if result == "Next Stage":
                return "Next Stage", score, current_level + 1, player_lives
            elif result == "Exit":
                pygame.quit()
                exit()

def main():
    """Starte das Spiel und verwalte die Menuefuehrung."""
    settings = lade_einstellungen()
    pygame.init()
    initialisiere_audio(kanalanzahl=16)
    sounds = lade_sounds()

    setze_musik_lautstaerke(sounds, settings["music_volume"])
    setze_soundeffekt_lautstaerke(sounds, settings["effects_volume"])

    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    if settings.get("fullscreen"):
        screen = pygame.display.set_mode((800, 600), flags | pygame.FULLSCREEN, vsync=1)
    else:
        screen = pygame.display.set_mode((800, 600), flags, vsync=1)
    main_menu = MainMenuScreen(screen)
    highscore_screen = HighscoreScreen(screen)
    win_screen = WinScreen(screen)
    lose_screen = LoseScreen(screen)
    pause_menu = PauseMenuScreen(screen)
    shop_screen = ShopScreen(screen)
    hud_icons = load_hud_icons()
    font = pygame.font.Font(None, 72)

    lade_musik(sounds["music"]["main_menu_music"])
    setze_musik_lautstaerke(sounds, sounds["volumes"]["music_volume"])

    current_screen = "main_menu"

    while True:
        if current_screen == "main_menu":
            print("Starte Hauptbildschirm...")
            pygame.event.clear()
            result = main_menu.show(font, sounds)
            print(f"Ergebnis aus Hauptbildschirm: {result}")
            if result == "pause":
                current_screen = "pause"
            else:
                current_screen = result

        elif current_screen == "Start Game":
            print("Spielstart wird initialisiert...")
            current_level = 1
            score = 0
            player_lives = 3  # Spieler startet mit 3 Leben
            active_upgrades = set()

            while True:
                print(f"Starte Stage {current_level} mit Score {score}")

                # Musik fuer die aktuelle Stage laden
                if current_level == 1:
                    lade_musik(sounds["music"]["world1_music"])
                elif current_level == 3:
                    lade_musik(sounds["music"]["world1_boss_music"])
                elif current_level == 4:
                    lade_musik(sounds["music"]["world2_music"])
                elif current_level == 6:
                    lade_musik(sounds["music"]["world2_boss_music"])
                elif current_level == 7:
                    lade_musik(sounds["music"]["world3_music"])

                setze_musik_lautstaerke(sounds, sounds["volumes"]["music_volume"])

                # Stage starten
                if current_level in {1, 2, 3}:
                    result, score, current_level, player_lives = spiele_level(
                        world1_lade_hintergrundbild,
                        world1_lade_alien_img,
                        {
                            1: world1_erstelle_stage_1_1_aliens,
                            2: world1_erstelle_stage_1_2_aliens,
                            3: world1_erstelle_stage_1_3_aliens
                        }[current_level],
                        world1_lade_hintergrundmusik,
                        current_level,
                        sounds,
                        score,
                        player_lives,
                        active_upgrades,
                        hud_icons
                    )
                elif current_level in {4, 5, 6}:
                    result, score, current_level, player_lives = spiele_level(
                        world2_lade_hintergrundbild,
                        world2_lade_alien_img,
                        {
                            4: world2_erstelle_stage_2_1_aliens,
                            5: world2_erstelle_stage_2_2_aliens,
                            6: world2_erstelle_stage_2_3_aliens
                        }[current_level],
                        world2_lade_hintergrundmusik,
                        current_level,
                        sounds,
                        score,
                        player_lives,
                        active_upgrades,
                        hud_icons
                    )
                elif current_level in {7, 8, 9}:
                    result, score, current_level, player_lives = spiele_level(
                        world3_lade_hintergrundbild,
                        world3_lade_alien_img,
                        {
                            7: world3_erstelle_stage_3_1_aliens,
                            8: world3_erstelle_stage_3_2_aliens,
                            9: world3_erstelle_stage_3_3_aliens,
                        }.get(current_level, world3_erstelle_stage_3_1_aliens),
                        world3_lade_hintergrundmusik,
                        current_level,
                        sounds,
                        score,
                        player_lives,
                        active_upgrades,
                        hud_icons
                    )
                else:
                    print("Keine weiteren Stages vorhanden")
                    break

                print(f"Ergebnis der Stage: {result}, Score: {score}, Level: {current_level}")

                if result == "Retry":
                    print("Spieler waehlt Retry. Neustart bei Stage 1-1.")
                    current_level = 1
                    score = 0
                elif result == "Next Stage":
                    print(f"Wechsel zu Stage {current_level}")
                elif result == "Shop":
                    prev = set(active_upgrades)
                    score, active_upgrades = shop_screen.show(
                        pygame.font.Font(None, 48), score, active_upgrades, sounds
                    )
                    if "life" in active_upgrades and "life" not in prev:
                        player_lives += 1
                        active_upgrades.remove("life")
                elif result == "Exit":
                    lade_musik(sounds["music"]["main_menu_music"])
                    setze_musik_lautstaerke(sounds, sounds["volumes"]["music_volume"])
                    current_screen = "main_menu"
                    break
                elif result == "game_over":
                    active_upgrades = set()
                    print("Spieler ist gestorben. Upgrades zurueckgesetzt.")
                elif result == "retry_stage":
                    print(f"Neustart der Stage {current_level}. Verbleibende Leben: {player_lives}")
                    continue  # Stage direkt neu starten

        elif current_screen == "Highscores":
            print("Zeige Highscore-Bildschirm...")
            result = highscore_screen.show(font, lade_highscores(), sounds)
            print(f"Ergebnis aus Highscore-Screen: {result}")
            if result == "pause":
                current_screen = "pause"
            elif result == "main_menu":
                pygame.event.clear()
                current_screen = "main_menu"
                print("Wechsle zurueck zum Hauptmenue")

        elif current_screen == "Options":
            print("Starte Options-Bildschirm...")
            option_screen = OptionScreen(screen, sounds, settings.get("fullscreen", False))
            result = option_screen.show(font)
            print(f"Ergebnis aus Options-Bildschirm: {result}")
            settings = lade_einstellungen()
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE
            if settings.get("fullscreen"):
                screen = pygame.display.set_mode((800, 600), flags | pygame.FULLSCREEN, vsync=1)
            else:
                screen = pygame.display.set_mode((800, 600), flags, vsync=1)

            main_menu = MainMenuScreen(screen)
            highscore_screen = HighscoreScreen(screen)
            win_screen = WinScreen(screen)
            lose_screen = LoseScreen(screen)
            pause_menu = PauseMenuScreen(screen)

            if result == "pause":
                current_screen = "pause"
            else:
                current_screen = result

        elif current_screen == "pause":
            result = pause_menu.show(font, sounds)
            if result == "Highscores":
                current_screen = "Highscores"
            elif result == "Options":
                current_screen = "Options"
            elif result == "Exit":
                pygame.quit()
                exit()
            else:
                current_screen = "main_menu"

        elif current_screen == "Exit":
            print("Spieler hat Exit gewaehlt. Beende das Spiel.")
            pygame.quit()
            exit()


if __name__ == "__main__":
    main()