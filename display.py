# -*- coding: utf-8 -*-
import pygame
import math
import highscore  # Highscore-Logik importieren
from settings import lade_einstellungen, speichere_einstellungen
from sounds import (
    setze_soundeffekt_lautstaerke,
    setze_musik_lautstaerke
)


def leave_fullscreen():
    """Switch to windowed mode and update saved settings."""
    if not pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
        return pygame.display.get_surface()

    settings = lade_einstellungen()
    settings["fullscreen"] = False
    speichere_einstellungen(settings)

    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    screen = pygame.display.set_mode((800, 600), flags, vsync=1)
    return screen

# Zentrale Farbdefinitionen fuer Buttons
BUTTON_COLORS = {
    "Next Stage": {"normal": (30, 60, 30), "hover": (30, 255, 30)},
    "Retry": {"normal": (30, 60, 30), "hover": (30, 255, 30)},
    "Exit": {"normal": (60, 30, 30), "hover": (255, 0, 0)},
    "Start Game": {"normal": (30, 60, 30), "hover": (30, 255, 30)},
    "Highscores": {"normal": (30, 30, 60), "hover": (30, 30, 255)},
    "Options": {"normal": (60, 30, 60), "hover": (255, 30, 255)},
    "Back": {"normal": (30, 60, 30), "hover": (30, 255, 30)},
    "Input": {"normal": (255, 255, 255), "hover": (200, 200, 200)},
    "Save & Back": {"normal": (30, 60, 30), "hover": (30, 255, 30)},
    "Fullscreen": {"normal": (60, 30, 60), "hover": (255, 30, 255)},
    "Resume": {"normal": (30, 60, 30), "hover": (30, 255, 30)},
    "Shop": {"normal": (30, 60, 30), "hover": (30, 255, 30)},
    "Leave": {"normal": (60, 30, 30), "hover": (255, 0, 0)}
}

class BaseScreen:
    """Basisklasse fuer alle Bildschirmdarstellungen."""

    def __init__(self, screen):
        """Speichere die Pygame-Oberflaeche, auf der gezeichnet wird."""
        self.screen = screen

    def lade_hintergrundbild(self, dateiname):
        """Lade und skaliere ein Hintergrundbild."""
        try:
            bild = pygame.image.load(dateiname)
            return pygame.transform.scale(bild, self.screen.get_size())
        except pygame.error as e:
            print(f"Fehler beim Laden des Hintergrundbildes {dateiname}: {e}")
            return None

    def berechne_animationsfarbe(self):
        """Berechne eine animierte Farbe fuer Neon-Effekte."""
        zeit = pygame.time.get_ticks() / 500
        rot = int((math.sin(zeit) + 1) * 127.5)
        gruen = int((math.sin(zeit + 2 * math.pi / 3) + 1) * 127.5)
        blau = int((math.sin(zeit + 4 * math.pi / 3) + 1) * 127.5)
        return (rot, gruen, blau)

    def draw_button(self, text, rect, base_color, hover_color, font, mouse_pos):
        """Zeichne einen Button und liefere zurueck, ob er gehovt wird."""
        is_hovered = rect.collidepoint(mouse_pos)
        color = hover_color if is_hovered else base_color

        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        neon_color = self.berechne_animationsfarbe()
        pygame.draw.rect(self.screen, neon_color, rect.inflate(4, 4), width=4, border_radius=12)

        shimmer_surface = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        shimmer_color = self.berechne_animationsfarbe()
        pygame.draw.rect(shimmer_surface, (shimmer_color[0], shimmer_color[1], shimmer_color[2], 50),
                         shimmer_surface.get_rect(), border_radius=15)
        self.screen.blit(shimmer_surface, (rect.x - 4, rect.y - 4))

        glass_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass_surface, (255, 255, 255, 50), glass_surface.get_rect(), border_radius=10)
        pygame.draw.rect(glass_surface, (255, 255, 255, 30), glass_surface.get_rect(), width=3, border_radius=10)
        self.screen.blit(glass_surface, rect.topleft)

        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

        return is_hovered

    def zeichne_punkte(self, score, font, color, stage_name):
        """
        Zeichnet den Punktestand und den Stagenamen auf den Bildschirm.
        """
        # Punktestand anzeigen
        score_text = font.render(f"Score: {score}", True, color)
        self.screen.blit(score_text, (10, 10))

        # Stage-Namen anzeigen
        stage_text = font.render(f"Stage: {stage_name}", True, color)
        self.screen.blit(stage_text, (10, 40))

class MainMenuScreen(BaseScreen):
    """Startbildschirm mit den Hauptoptionen."""

    def __init__(self, screen):
        """Initialisiere den Hauptmenue-Bildschirm."""
        super().__init__(screen)
        self.background = self.lade_hintergrundbild("main_screen.png")

    def show(self, font, sounds=None):
        """Zeige das Hauptmenue und liefere den gewaehlten Button."""
        pygame.event.clear()
        message = "STELLAR SIEGE"
        screen_width, screen_height = self.screen.get_size()
        scale_x = screen_width / 800
        scale_y = screen_height / 600

        button_font = pygame.font.Font(None, int(36 * scale_y))
        button_width = int(200 * scale_x)
        button_height = int(50 * scale_y)
        x_pos = (screen_width - button_width) // 2
        layout = {
            "Start Game": pygame.Rect(x_pos, int(200 * scale_y), button_width, button_height),
            "Highscores": pygame.Rect(x_pos, int(280 * scale_y), button_width, button_height),
            "Options": pygame.Rect(x_pos, int(360 * scale_y), button_width, button_height),
            "Exit": pygame.Rect(x_pos, int(440 * scale_y), button_width, button_height),
        }
        hovered_button = None

        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button, rect in layout.items():
                        if rect.collidepoint(event.pos):
                            if sounds and "mouse_click" in sounds["effects"]:
                                sounds["effects"]["mouse_click"].set_volume(
                                    sounds["volumes"]["effects_volume"]
                                )
                                sounds["effects"]["mouse_click"].play()
                            return button

            self.screen.blit(self.background, (0, 0))

            # Glow-Effekt fuer "STELLAR SIEGE"
            animated_color = self.berechne_animationsfarbe()
            title_font = pygame.font.Font(None, int(72 * scale_y))
            title_surface = title_font.render(message, True, animated_color)
            title_rect = title_surface.get_rect(center=(screen_width // 2, int(80 * scale_y)))

            # Perfekt zentrierter Hintergrund fuer Glow
            glow_title_width = title_rect.width + int(60 * scale_x)
            glow_title_height = title_rect.height + int(20 * scale_y)
            glow_title_surface = pygame.Surface((glow_title_width, glow_title_height), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_title_surface,
                (animated_color[0], animated_color[1], animated_color[2], 100),
                glow_title_surface.get_rect(),
                border_radius=15,
            )
            glow_title_rect = glow_title_surface.get_rect(center=title_rect.center)
            self.screen.blit(glow_title_surface, glow_title_rect.topleft)

            # Zeichnen des Titels
            self.screen.blit(title_surface, title_rect)

            # Buttons rendern mit Glanz-Effekt
            for button, rect in layout.items():
                colors = BUTTON_COLORS[button]
                text = button
                if button == "Fullscreen":
                    text = f"Fullscreen: {'OFF' if self.fullscreen else 'ON'}"
                is_hovered = self.draw_button(text, rect, colors["normal"], colors["hover"], button_font, mouse_pos)

                # Glanz-Effekt fuer Buttons
                shimmer_surface = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
                shimmer_color = self.berechne_animationsfarbe()
                pygame.draw.rect(
                    shimmer_surface,
                    (shimmer_color[0], shimmer_color[1], shimmer_color[2], 50),
                    shimmer_surface.get_rect(),
                    border_radius=15,
                )
                self.screen.blit(shimmer_surface, (rect.x - 4, rect.y - 4))

                # Mouse-Over-Sound
                if is_hovered and hovered_button != button and sounds:
                    if "mouse_over" in sounds["effects"]:
                        sounds["effects"]["mouse_over"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["mouse_over"].play()
                    hovered_button = button
                elif not is_hovered and hovered_button == button:
                    hovered_button = None

            pygame.display.flip()

class PauseMenuScreen(BaseScreen):
    """Menue fuer Pausen mit eingeschraenkten Optionen."""

    def __init__(self, screen):
        """Initialisiere den Pause-Bildschirm."""
        super().__init__(screen)
        self.background = self.lade_hintergrundbild("main_screen.png")

    def show(self, font, sounds=None):
        """Zeige das Pausenmenue und liefere den gewaehlten Button."""
        pygame.event.clear()
        button_font = pygame.font.Font(None, 36)
        layout = {
            "Resume": pygame.Rect(300, 200, 200, 50),
            "Highscores": pygame.Rect(300, 280, 200, 50),
            "Options": pygame.Rect(300, 360, 200, 50),
            "Exit": pygame.Rect(300, 440, 200, 50),
        }
        hovered_button = None

        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button, rect in layout.items():
                        if rect.collidepoint(event.pos):
                            if sounds and "mouse_click" in sounds["effects"]:
                                sounds["effects"]["mouse_click"].set_volume(
                                    sounds["volumes"]["effects_volume"]
                                )
                                sounds["effects"]["mouse_click"].play()
                            return button
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pass

            self.screen.blit(self.background, (0, 0))

            animated_color = self.berechne_animationsfarbe()
            title_surface = font.render("PAUSED", True, animated_color)
            title_rect = title_surface.get_rect(center=(400, 80))

            glow_title_width = title_rect.width + 60
            glow_title_height = title_rect.height + 20
            glow_surface = pygame.Surface((glow_title_width, glow_title_height), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surface,
                (animated_color[0], animated_color[1], animated_color[2], 100),
                glow_surface.get_rect(),
                border_radius=15,
            )
            glow_rect = glow_surface.get_rect(center=title_rect.center)
            self.screen.blit(glow_surface, glow_rect.topleft)

            self.screen.blit(title_surface, title_rect)

            for button, rect in layout.items():
                colors = BUTTON_COLORS[button]
                is_hovered = self.draw_button(button, rect, colors["normal"], colors["hover"], button_font, mouse_pos)

                shimmer_surface = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
                shimmer_color = self.berechne_animationsfarbe()
                pygame.draw.rect(
                    shimmer_surface,
                    (shimmer_color[0], shimmer_color[1], shimmer_color[2], 50),
                    shimmer_surface.get_rect(),
                    border_radius=15,
                )
                self.screen.blit(shimmer_surface, (rect.x - 4, rect.y - 4))

                if is_hovered and hovered_button != button and sounds:
                    if "mouse_over" in sounds["effects"]:
                        sounds["effects"]["mouse_over"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["mouse_over"].play()
                    hovered_button = button
                elif not is_hovered and hovered_button == button:
                    hovered_button = None

            pygame.display.flip()

class HighscoreScreen(BaseScreen):
    """Anzeige der gespeicherten Highscores."""

    def __init__(self, screen):
        """Initialisiere den Highscore-Bildschirm."""
        super().__init__(screen)
        self.background = self.lade_hintergrundbild("highscore_screen.png")

    def show(self, font, highscores, sounds=None):
        """Zeige die Highscore-Liste und warte auf eine Eingabe."""
        clock = pygame.time.Clock()
        running = True
        base_button_rect = pygame.Rect(300, 500, 200, 50)
        base_button_font_size = 36
        base_score_font_size = 36
        last_hovered = False  # Statusvariable fuer Mouse-Over

        col_idx = 100
        col_name = 140
        col_dash = 400
        col_score = 450

        while running:
            screen_w, screen_h = self.screen.get_size()
            scale_x = screen_w / 800
            scale_y = screen_h / 600

            mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(self.background, (0, 0))

            button_font = pygame.font.Font(None, int(base_button_font_size * scale_y))
            score_font = pygame.font.Font(None, int(base_score_font_size * scale_y))
            button_rect = pygame.Rect(
                int(base_button_rect.x * scale_x),
                int(base_button_rect.y * scale_y),
                int(base_button_rect.width * scale_x),
                int(base_button_rect.height * scale_y),
            )

            col_position_idx = int(col_idx * scale_x)
            col_position_name = int(col_name * scale_x)
            col_position_dash = int(col_dash * scale_x)
            col_position_score = int(col_score * scale_x)

            # Titel des Highscore-Bildschirms
            animated_color = self.berechne_animationsfarbe()
            title_surface = font.render("HIGHSCORES", True, animated_color)
            title_rect = title_surface.get_rect(center=(screen_w // 2, int(40 * scale_y)))
            self.screen.blit(title_surface, title_rect)

            # Highscores anzeigen (sicherstellen, dass highscores eine Liste ist)
            if isinstance(highscores, list):
                y_offset = int(100 * scale_y)
                for idx, entry in enumerate(highscores, start=1):
                    player_name = entry.get("player", "Unknown")
                    score = entry.get("score", 0)

                    # Platznummer anzeigen
                    idx_surface = score_font.render(f"{idx}.", True, animated_color)
                    self.screen.blit(idx_surface, (col_position_idx, y_offset))

                    # Spielername anzeigen
                    name_surface = score_font.render(player_name, True, animated_color)
                    self.screen.blit(name_surface, (col_position_name, y_offset))

                    # Bindestrich anzeigen
                    dash_surface = score_font.render("-", True, animated_color)
                    self.screen.blit(dash_surface, (col_position_dash, y_offset))

                    # Punktzahl anzeigen
                    score_surface = score_font.render(str(score), True, animated_color)
                    self.screen.blit(score_surface, (col_position_score, y_offset))

                    y_offset += int(40 * scale_y)

            # "Back"-Button mit Glanz-Effekt
            colors = BUTTON_COLORS["Back"]
            is_hovered = self.draw_button("Back", button_rect, colors["normal"], colors["hover"], button_font, mouse_pos)

            # Glanz-Effekt fuer den "Back"-Button
            shimmer_surface = pygame.Surface((button_rect.width + 8, button_rect.height + 8), pygame.SRCALPHA)
            shimmer_color = self.berechne_animationsfarbe()
            pygame.draw.rect(
                shimmer_surface,
                (shimmer_color[0], shimmer_color[1], shimmer_color[2], 50),
                shimmer_surface.get_rect(),
                border_radius=15,
            )
            self.screen.blit(shimmer_surface, (button_rect.x - 4, button_rect.y - 4))

            # Mouse-Over-Sound (angepasst fuer neue Soundstruktur)
            if is_hovered and not last_hovered:
                if sounds and "mouse_over" in sounds["effects"]:
                    sounds["effects"]["mouse_over"].set_volume(sounds["volumes"]["effects_volume"])
                    sounds["effects"]["mouse_over"].play()
                last_hovered = True
            elif not is_hovered:
                last_hovered = False

            # Event-Verarbeitung
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pass
                if event.type == pygame.MOUSEBUTTONDOWN and is_hovered:
                    # Mouse-Click-Sound abspielen
                    if sounds and "mouse_click" in sounds["effects"]:
                        sounds["effects"]["mouse_click"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["mouse_click"].play()
                    running = False

            pygame.display.flip()
            clock.tick(60)

        return "main_menu"
        
class OptionScreen(BaseScreen):
    """Bildschirm zur Anpassung der Lautstaerke."""

    def __init__(self, screen, sounds, fullscreen=False):
        """Speichere Sounds und lade den Optionshintergrund."""
        super().__init__(screen)
        self.sounds = sounds
        self.fullscreen = fullscreen
        # Urspruengliche Lautstaerken sichern
        self.original_music_volume = sounds["volumes"]["music_volume"]
        self.original_effects_volume = sounds["volumes"]["effects_volume"]

        # Aktuelle Lautstaerken auf die gespeicherten Werte setzen
        self.music_volume = self.original_music_volume
        self.effects_volume = self.original_effects_volume

        self.background = self.lade_hintergrundbild("option_screen.png")

    def show(self, font):
        """Zeige die Optionsmenue und erlaube Lautstaerkeanpassungen."""
        clock = pygame.time.Clock()
        running = True
        base_layout = {
            "Back": pygame.Rect(150, 500, 200, 50),
            "Save & Back": pygame.Rect(450, 500, 200, 50),
            "Fullscreen": pygame.Rect(300, 400, 200, 50),
        }

        base_music_slider = pygame.Rect(250, 200, 400, 20)
        base_effects_slider = pygame.Rect(250, 300, 400, 20)
        base_slider_knob_width = 20

        dragging_music = False
        dragging_effects = False
        hovered_button = None
        prev_mouse_pressed = False

        while running:
            screen_width, screen_height = self.screen.get_size()
            scale_x = screen_width / 800
            scale_y = screen_height / 600

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            mouse_clicked = mouse_pressed[0] and not prev_mouse_pressed
            prev_mouse_pressed = mouse_pressed[0]
            self.screen.blit(self.background, (0, 0))

            button_font = pygame.font.Font(None, int(36 * scale_y))
            title_font = pygame.font.Font(None, int(72 * scale_y))

            layout = {
                k: pygame.Rect(
                    int(v.x * scale_x),
                    int(v.y * scale_y),
                    int(v.width * scale_x),
                    int(v.height * scale_y),
                )
                for k, v in base_layout.items()
            }

            music_slider_rect = pygame.Rect(
                int(base_music_slider.x * scale_x),
                int(base_music_slider.y * scale_y),
                int(base_music_slider.width * scale_x),
                int(base_music_slider.height * scale_y),
            )
            effects_slider_rect = pygame.Rect(
                int(base_effects_slider.x * scale_x),
                int(base_effects_slider.y * scale_y),
                int(base_effects_slider.width * scale_x),
                int(base_effects_slider.height * scale_y),
            )
            slider_knob_width = int(base_slider_knob_width * scale_x)

            animated_color = self.berechne_animationsfarbe()
            title_surface = title_font.render("OPTIONS", True, animated_color)
            title_rect = title_surface.get_rect(
                center=(screen_width // 2, int(100 * scale_y))
            )
            self.screen.blit(title_surface, title_rect)

            music_volume_font = pygame.font.Font(None, int(38 * scale_y))
            effects_volume_font = pygame.font.Font(None, int(38 * scale_y))

            # Music Volume Slider
            pygame.draw.rect(self.screen, animated_color, music_slider_rect)
            music_knob_x = music_slider_rect.x + int(self.music_volume * music_slider_rect.width) - slider_knob_width // 2
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                pygame.Rect(
                    music_knob_x,
                    music_slider_rect.y - int(5 * scale_y),
                    slider_knob_width,
                    int(30 * scale_y),
                ),
            )
            music_text = music_volume_font.render("Music Vol.", True, animated_color)
            self.screen.blit(
                music_text,
                (music_slider_rect.x - int(200 * scale_x), music_slider_rect.y - int(5 * scale_y)),
            )

            # Effects Volume Slider
            pygame.draw.rect(self.screen, animated_color, effects_slider_rect)
            effects_knob_x = effects_slider_rect.x + int(self.effects_volume * effects_slider_rect.width) - slider_knob_width // 2
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                pygame.Rect(
                    effects_knob_x,
                    effects_slider_rect.y - int(5 * scale_y),
                    slider_knob_width,
                    int(30 * scale_y),
                ),
            )
            effects_text = effects_volume_font.render("Effects Vol.", True, animated_color)
            self.screen.blit(
                effects_text,
                (effects_slider_rect.x - int(200 * scale_x), effects_slider_rect.y - int(5 * scale_y)),
            )

            # Buttons
            for button, rect in layout.items():
                colors = BUTTON_COLORS[button]
                text = button
                if button == "Fullscreen":
                    text = f"Fullscreen: {'OFF' if self.fullscreen else 'ON'}"
                is_hovered = self.draw_button(text, rect, colors["normal"], colors["hover"], button_font, mouse_pos)

                if is_hovered and self.sounds and "mouse_over" in self.sounds["effects"]:
                    if hovered_button != button:
                        self.sounds["effects"]["mouse_over"].set_volume(self.sounds["volumes"]["effects_volume"])
                        self.sounds["effects"]["mouse_over"].play()
                    hovered_button = button
                elif not is_hovered and hovered_button == button:
                    hovered_button = None

                # Button-Aktionen
                if is_hovered and mouse_clicked:
                    if self.sounds and "mouse_click" in self.sounds["effects"]:
                        self.sounds["effects"]["mouse_click"].set_volume(self.sounds["volumes"]["effects_volume"])
                        self.sounds["effects"]["mouse_click"].play()

                    if button == "Back":
                        # Lautstaerke wiederherstellen
                        self.sounds["volumes"]["music_volume"] = self.original_music_volume
                        self.sounds["volumes"]["effects_volume"] = self.original_effects_volume

                        # Pygame-Lautstaerke setzen
                        setze_musik_lautstaerke(self.sounds, self.original_music_volume)
                        setze_soundeffekt_lautstaerke(self.sounds, self.original_effects_volume)

                        return "main_menu"  # Zurueck ohne Speichern

                    elif button == "Save & Back":
                        # Einstellungen speichern
                        self.sounds["volumes"]["music_volume"] = self.music_volume
                        self.sounds["volumes"]["effects_volume"] = self.effects_volume
                        speichere_einstellungen({
                            "music_volume": self.music_volume,
                            "effects_volume": self.effects_volume,
                            "fullscreen": self.fullscreen
                        })
                        return "main_menu"
                    elif button == "Fullscreen":
                        self.fullscreen = not self.fullscreen
                        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode(
                                (800, 600),
                                flags | pygame.FULLSCREEN,
                                vsync=1,
                            )
                        else:
                            self.screen = pygame.display.set_mode((800, 600), flags, vsync=1)
                        self.background = self.lade_hintergrundbild("option_screen.png")

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if music_slider_rect.collidepoint(event.pos):
                        dragging_music = True
                    if effects_slider_rect.collidepoint(event.pos):
                        dragging_effects = True

                if event.type == pygame.MOUSEBUTTONUP:
                    dragging_music = dragging_effects = False

                if event.type == pygame.MOUSEMOTION:
                    if dragging_music:
                        self.music_volume = min(1.0, max(0.0, (mouse_pos[0] - music_slider_rect.x) / music_slider_rect.width))
                        setze_musik_lautstaerke(self.sounds, self.music_volume)
                    if dragging_effects:
                        self.effects_volume = min(1.0, max(0.0, (mouse_pos[0] - effects_slider_rect.x) / effects_slider_rect.width))
                        self.sounds["effects"]["mouse_over"].set_volume(self.effects_volume)
                        self.sounds["effects"]["mouse_over"].play()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pass

            pygame.display.flip()
            clock.tick(60)

class WinScreen(BaseScreen):
    """Bildschirm nach erfolgreich abgeschlossener Stage."""

    def __init__(self, screen):
        """Lade das Hintergrundbild fuer den Win-Screen."""
        super().__init__(screen)
        self.background = self.lade_hintergrundbild("win_screen.png")

    def show(self, stage_name, font, sounds=None, score=None):
        """
        Zeigt den Win-Screen mit Stage-Name und Score an.
        """
        if sounds and "win" in sounds["effects"]:
            sounds["effects"]["win"].set_volume(sounds["volumes"]["effects_volume"])
            sounds["effects"]["win"].play()

        buttons = ["Shop", "Next Stage", "Exit"]
        return self._show_message_screen(
            font, f"STAGE {stage_name} COMPLETE!", buttons, sounds, score
        )

    def _show_message_screen(self, font, message, buttons, sounds, score):
        """
        Rendert den Win-Screen und verarbeitet Eingaben.
        """
        clock = pygame.time.Clock()
        running = True
        base_layout = {
            "Shop": pygame.Rect(300, 300, 200, 50),
            "Next Stage": pygame.Rect(300, 380, 200, 50),
            "Exit": pygame.Rect(300, 460, 200, 50),
        }
        hovered_button = None

        while running:
            mouse_pos = pygame.mouse.get_pos()
            screen_w, screen_h = self.screen.get_size()
            scale_x = screen_w / 800
            scale_y = screen_h / 600
            layout = {
                k: pygame.Rect(
                    int(base_layout[k].x * scale_x),
                    int(base_layout[k].y * scale_y),
                    int(base_layout[k].width * scale_x),
                    int(base_layout[k].height * scale_y),
                )
                for k in buttons
                if k in base_layout
            }

            self.screen.blit(self.background, (0, 0))

            # Animierter Titel fuer STAGE X-Y COMPLETE!
            animated_color = self.berechne_animationsfarbe()
            message_font = pygame.font.Font(None, int(72 * scale_y))
            message_surface = message_font.render(message, True, animated_color)
            message_rect = message_surface.get_rect(center=(int(400 * scale_x), int(100 * scale_y)))
            self.screen.blit(message_surface, message_rect)

            # Anzeige des Scores
            if score is not None:
                score_font = pygame.font.Font(None, int(72 * scale_y))
                score_surface = score_font.render(f"SCORE: {score}", True, animated_color)
                score_rect = score_surface.get_rect(center=(int(400 * scale_x), int(180 * scale_y)))
                self.screen.blit(score_surface, score_rect)

            # Buttons zeichnen
            for button, rect in layout.items():
                colors = BUTTON_COLORS[button]
                button_font = pygame.font.Font(None, int(36 * scale_y))
                is_hovered = self.draw_button(button, rect, colors["normal"], colors["hover"], button_font, mouse_pos)

                # Mouse-Over-Sound
                if is_hovered and sounds and "mouse_over" in sounds["effects"]:
                    if hovered_button != button:
                        sounds["effects"]["mouse_over"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["mouse_over"].play()
                    hovered_button = button
                elif not is_hovered and hovered_button == button:
                    hovered_button = None

                # Mouse-Click-Sound und Button-Aktion
                if is_hovered and pygame.mouse.get_pressed()[0]:
                    if sounds and "mouse_click" in sounds["effects"]:
                        sounds["effects"]["mouse_click"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["mouse_click"].play()
                    return button

            pygame.display.flip()

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "pause"

            clock.tick(60)

class LoseScreen(BaseScreen):
    """Bildschirm der bei einem Verlust erscheint."""

    def __init__(self, screen):
        """Lade das Hintergrundbild fuer den Game-Over-Screen."""
        super().__init__(screen)
        self.background = self.lade_hintergrundbild("lose_screen.png")

    def show(self, font, sounds=None, score=None):
        """
        Zeigt den Verlust-Bildschirm an und spielt den "Game Over"-Sound ab.
        """
        if sounds and "game_over" in sounds["effects"]:
            sounds["effects"]["game_over"].set_volume(sounds["volumes"]["effects_volume"])
            sounds["effects"]["game_over"].play()

        return self._show_message_screen(font, f"Score: {score}", ["Retry", "Exit"], sounds, score)

    def _show_message_screen(self, font, message, buttons, sounds, score):
        """
        Rendert den Verlust-Bildschirm und verarbeitet Eingaben.
        """
        clock = pygame.time.Clock()
        running = True
        user_text = ""  # Eingabefeld fuer den Spielernamen
        input_active = False
        cursor_visible = True  # Steuerung fuer blinkenden Cursor
        cursor_timer = 0  # Timer fuer Cursor-Blinken

        base_layout = {
            "Retry": pygame.Rect(300, 370, 200, 50),
            "Exit": pygame.Rect(300, 450, 200, 50),
        }
        base_input_rect = pygame.Rect(300, 290, 200, 50)  # Eingabefeld fuer Spielernamen

        hovered_button = None  # Speichert den zuletzt gehighlighteten Button

        while running:
            mouse_pos = pygame.mouse.get_pos()
            screen_w, screen_h = self.screen.get_size()
            scale_x = screen_w / 800
            scale_y = screen_h / 600
            layout = {
                k: pygame.Rect(
                    int(v.x * scale_x),
                    int(v.y * scale_y),
                    int(v.width * scale_x),
                    int(v.height * scale_y),
                )
                for k, v in base_layout.items()
            }
            input_rect = pygame.Rect(
                int(base_input_rect.x * scale_x),
                int(base_input_rect.y * scale_y),
                int(base_input_rect.width * scale_x),
                int(base_input_rect.height * scale_y),
            )

            self.screen.blit(self.background, (0, 0))

            # Titel: Score-Anzeige oben mittig mit animierten Farben
            animated_color = self.berechne_animationsfarbe()
            title_font = pygame.font.Font(None, int(72 * scale_y))
            title_surface = title_font.render(message, True, animated_color)
            title_rect = title_surface.get_rect(center=(int(400 * scale_x), int(100 * scale_y)))
            self.screen.blit(title_surface, title_rect)

            # Eingabefeld
            input_color = (200, 200, 200) if input_active else (255, 255, 255)
            pygame.draw.rect(self.screen, input_color, input_rect, border_radius=10)

            input_font = pygame.font.Font(None, int(36 * scale_y))
            input_text_surface = input_font.render(user_text or ("Enter Name" if not input_active else ""), True, (0, 0, 0))
            input_text_rect = input_text_surface.get_rect(midleft=(input_rect.x + int(10 * scale_x), input_rect.centery))
            self.screen.blit(input_text_surface, input_text_rect)

            # Cursor
            if input_active and cursor_visible:
                cursor_x = input_text_rect.right + int(5 * scale_x)
                cursor_y = input_text_rect.top
                pygame.draw.line(self.screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + input_text_rect.height), 2)

            cursor_timer += clock.get_time()
            if cursor_timer >= 500:  # Blinkt alle 500 ms
                cursor_visible = not cursor_visible
                cursor_timer = 0

            # Buttons
            for button, rect in layout.items():
                colors = BUTTON_COLORS[button]
                button_font = pygame.font.Font(None, int(36 * scale_y))
                is_hovered = self.draw_button(button, rect, colors["normal"], colors["hover"], button_font, mouse_pos)

                # Mouse-Over-Sound
                if is_hovered and sounds and "mouse_over" in sounds["effects"]:
                    if hovered_button != button:
                        sounds["effects"]["mouse_over"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["mouse_over"].play()
                    hovered_button = button
                elif not is_hovered and hovered_button == button:
                    hovered_button = None

                # Mouse-Click-Sound und Button-Aktion
                if is_hovered and pygame.mouse.get_pressed()[0]:
                    if sounds and "mouse_click" in sounds["effects"]:
                        sounds["effects"]["mouse_click"].set_volume(sounds["volumes"]["effects_volume"])
                        sounds["effects"]["mouse_click"].play()
                    if button == "Retry" and user_text.strip():
                        highscore.aktualisiere_highscores(score, user_text.strip())
                    elif button == "Exit" and user_text.strip():
                        highscore.aktualisiere_highscores(score, user_text.strip())
                        pygame.quit()
                        exit()
                    return button

            pygame.display.flip()

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False

                if input_active and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

            clock.tick(60)