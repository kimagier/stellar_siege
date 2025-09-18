# -*- coding: utf-8 -*-
import pygame

def initialisiere_audio(kanalanzahl=16):
    """
    Initialisiert das Audio-System mit einer angegebenen Anzahl an Kanaelen.
    """
    pygame.mixer.init()
    pygame.mixer.set_num_channels(kanalanzahl)
    print(f"Audio initialisiert mit {kanalanzahl} Kanaelen")

def lade_sounds():
    """
    Lade Soundeffekte und Hintergrundmusik und gib ein verschachteltes Dictionary zurueck.
    """
    sounds = {
        "effects": {
            "shoot": pygame.mixer.Sound("shoot.wav"),
            "hit": pygame.mixer.Sound("hit.wav"),
            "game_over": pygame.mixer.Sound("game_over.wav"),
            "win": pygame.mixer.Sound("win_sound.wav"),
            "alien_shoot": pygame.mixer.Sound("alien_shoot.wav"),
            "alien_shoot_klein": pygame.mixer.Sound("alien_shoot_klein.wav"),
            "mouse_over": pygame.mixer.Sound("mouse_over.wav"),
            "mouse_click": pygame.mixer.Sound("mouse_click.wav"),
        },
        "music": {
            "main_menu_music": "main.wav",
            "world1_music": "world1.wav",
            "world2_music": "world2.wav",
            "world3_music": "world3.wav",
            "world1_boss_music": "world1-boss.wav",
            "world2_boss_music": "world2-boss.wav",
            "world3_boss_music": "world3-boss.wav",
            "shop_music": "shop.wav",
        },
        "volumes": {
            "music_volume": 0.5,
            "effects_volume": 0.5,
        }
    }

    # Setze die Lautstaerke fuer alle Soundeffekte
    for sound in sounds["effects"].values():
        sound.set_volume(sounds["volumes"]["effects_volume"])
    
    print("Soundeffekte und Hintergrundmusik geladen:", list(sounds["effects"].keys()) + list(sounds["music"].keys()))
    return sounds

def lade_musik(datei):
    """
    Lade und starte die Hintergrundmusik.
    :param datei: Pfad zur Musikdatei.
    """
    try:
        pygame.mixer.music.load(datei)
        print(f"Hintergrundmusik {datei} erfolgreich geladen.")
        pygame.mixer.music.play(-1)  # Musik im Loop abspielen
    except pygame.error as e:
        print(f"Fehler beim Laden der Musikdatei {datei}: {e}")

def setze_soundeffekt_lautstaerke(sounds, volume):
    """
    Setzt die Lautstaerke aller Soundeffekte.
    :param sounds: Dictionary der Sounds.
    :param volume: Lautstaerke (0.0 bis 1.0).
    """
    sounds["volumes"]["effects_volume"] = volume  # Speichere die neue Lautstaerke
    for sound in sounds["effects"].values():
        sound.set_volume(volume)
    print(f"Soundeffekt-Lautstaerke auf {volume} gesetzt.")

def setze_musik_lautstaerke(sounds, volume):
    """
    Setzt die Lautstaerke der Hintergrundmusik.
    :param sounds: Dictionary der Sounds.
    :param volume: Lautstaerke (0.0 bis 1.0).
    """
    sounds["volumes"]["music_volume"] = volume  # Speichere die neue Lautstaerke
    pygame.mixer.music.set_volume(volume)
    print(f"Hintergrundmusik-Lautstaerke auf {volume} gesetzt.")
