# -*- coding: utf-8 -*-
"""Shop system that allows players to buy upgrades between stages."""

import math
import pygame

from display import BaseScreen, BUTTON_COLORS
from sounds import lade_musik, setze_musik_lautstaerke

# Consistent neon blue color for shop text
NEON_BLUE = (0, 200, 255)


UPGRADES = [
    {
        "name": "life",
        "file": "leben.png",
        "pos": (110, 452),
        "cost": 500,
        "description": "Adds one extra life",
    },
    {
        "name": "speed",
        "file": "bewegung.png",
        "pos": (230, 452),
        "cost": 750,
        "description": "Increases ship speed",
    },
    {
        "name": "firerate",
        "file": "schussrate.png",
        "pos": (350, 452),
        "cost": 1500,
        "description": "Shoot two bullets",
    },
    {
        "name": "damage",
        "file": "schaden.png",
        "pos": (470, 452),
        "cost": 2000,
        "description": "Bullets deal more damage",
    },
    {
        "name": "shield",
        "file": "schild.png",
        "pos": (590, 452),
        "cost": 1000,
        "description": "Blocks one hit without losing a life",
    },
]


class ShopScreen(BaseScreen):
    """Screen that lets the player buy upgrades."""

    def __init__(self, screen):
        super().__init__(screen)
        self.background = self.lade_hintergrundbild("shop.jpg")
        self.icons = {}
        for item in UPGRADES:
            img = pygame.image.load(item["file"]).convert_alpha()
            self.icons[item["name"]] = pygame.transform.scale(img, (48, 48))

    def show(self, font, points, active_upgrades, sounds=None):
        """Display the shop and handle input.

        Parameters
        ----------
        font : pygame.font.Font
            Font used for rendering text.
        points : int
            Current player points available for spending.
        active_upgrades : set[str]
            Upgrades already purchased.
        sounds : dict | None
            Loaded sound dictionary. If provided, plays a sound when the
            selection changes and starts shop music if available.
        """
        if sounds and "shop_music" in sounds.get("music", {}):
            lade_musik(sounds["music"]["shop_music"])
            setze_musik_lautstaerke(sounds, sounds["volumes"]["music_volume"])

        clock = pygame.time.Clock()
        running = True
        selection = 0
        popup = False
        popup_choice = 0
        error_timer = 0
        leave_hovered = False
        # Mark upgrades as sold out if they are currently active (except life)
        sold_out = {name for name in active_upgrades if name != "life"}

        leave_rect = pygame.Rect(650, 520, 120, 50)

        while running:
            delta_time = clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    if popup:
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                            popup_choice = 1 - popup_choice
                        elif event.key == pygame.K_SPACE:
                            if popup_choice == 0:
                                item = UPGRADES[selection]
                                name = item["name"]
                                cost = item["cost"]
                                if points >= cost and name not in active_upgrades:
                                    points -= cost
                                    active_upgrades.add(name)
                                    sold_out.add(name)
                                else:
                                    error_timer = 60
                            popup = False
                        elif event.key == pygame.K_ESCAPE:
                            popup = False
                    else:
                        if event.key == pygame.K_LEFT:
                            selection = (selection - 1) % len(UPGRADES)
                            if sounds and "mouse_over" in sounds["effects"]:
                                sounds["effects"]["mouse_over"].set_volume(
                                    sounds["volumes"]["effects_volume"]
                                )
                                sounds["effects"]["mouse_over"].play()
                        elif event.key == pygame.K_RIGHT:
                            selection = (selection + 1) % len(UPGRADES)
                            if sounds and "mouse_over" in sounds["effects"]:
                                sounds["effects"]["mouse_over"].set_volume(
                                    sounds["volumes"]["effects_volume"]
                                )
                                sounds["effects"]["mouse_over"].play()
                        elif event.key == pygame.K_SPACE:
                            if UPGRADES[selection]["name"] not in sold_out:
                                popup = True
                                popup_choice = 0
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                if event.type == pygame.MOUSEBUTTONDOWN and not popup:
                    if leave_rect.collidepoint(event.pos):
                        if sounds and "mouse_click" in sounds["effects"]:
                            sounds["effects"]["mouse_click"].set_volume(
                                sounds["volumes"]["effects_volume"]
                            )
                            sounds["effects"]["mouse_click"].play()
                        running = False

            self.screen.blit(self.background, (0, 0))

            # Larger spaced title with neon color
            title_font = pygame.font.Font(None, 72)
            title_surface = title_font.render("S    H    O    P", True, NEON_BLUE)
            title_rect = title_surface.get_rect(center=(400, 80))
            self.screen.blit(title_surface, title_rect)

            points_font = pygame.font.Font(None, 36)
            points_display_font = pygame.font.Font(None, 48)
            points_text = points_display_font.render(
                f"Your Points: {points}", True, NEON_BLUE
            )
            points_pos = (150, 200)
            self.screen.blit(points_text, points_pos)

            description = UPGRADES[selection].get("description", "")
            desc_surface = points_display_font.render(description, True, NEON_BLUE)
            self.screen.blit(desc_surface, (points_pos[0], points_pos[1] + 70))

            time_now = pygame.time.get_ticks() / 500
            for idx, item in enumerate(UPGRADES):
                base_x, base_y = item["pos"]
                offset = math.sin(time_now + idx) * 5
                icon_y = base_y - 24 + offset
                if item["name"] in sold_out:
                    sold_text = points_font.render("SOLD", True, (255, 0, 0))
                    sold_rect = sold_text.get_rect(center=(base_x + 24, icon_y + 24))
                    self.screen.blit(sold_text, sold_rect)
                else:
                    img = self.icons[item["name"]]
                    self.screen.blit(img, (base_x, icon_y))
                price = points_font.render(str(item["cost"]), True, NEON_BLUE)
                price_rect = price.get_rect(center=(base_x + 24, base_y + 41))
                self.screen.blit(price, price_rect)
                if idx == selection and not popup:
                    pygame.draw.rect(
                        self.screen,
                        (0, 255, 0),
                        pygame.Rect(base_x - 4, icon_y - 4, 56, 56),
                        2,
                    )

            if popup:
                rect = pygame.Rect(200, 250, 400, 100)
                pygame.draw.rect(self.screen, (0, 0, 0), rect)
                pygame.draw.rect(self.screen, (0, 255, 0), rect, 2)
                item = UPGRADES[selection]
                msg = (
                    f"Purchase upgrade {item['name']} for {item['cost']} points?"
                )
                popup_text = points_font.render(msg, True, (255, 255, 255))
                self.screen.blit(
                    popup_text,
                    popup_text.get_rect(center=(400, 285)),
                )
                options = ["Yes", "No"]
                for i, opt in enumerate(options):
                    color = (0, 255, 0) if i == popup_choice else (255, 255, 255)
                    opt_surface = points_font.render(opt, True, color)
                    pos_x = 330 + i * 80
                    self.screen.blit(opt_surface, (pos_x, 320))

            if error_timer > 0:
                err_surface = points_font.render(
                    "Not enough points!", True, (255, 0, 0)
                )
                self.screen.blit(
                    err_surface, err_surface.get_rect(center=(400, 285))
                )
                error_timer -= 1

            is_hovered = self.draw_button(
                "Leave",
                leave_rect,
                BUTTON_COLORS["Leave"]["normal"],
                BUTTON_COLORS["Leave"]["hover"],
                points_font,
                pygame.mouse.get_pos(),
            )

            if is_hovered and not leave_hovered and sounds:
                if "mouse_over" in sounds["effects"]:
                    sounds["effects"]["mouse_over"].set_volume(
                        sounds["volumes"]["effects_volume"]
                    )
                    sounds["effects"]["mouse_over"].play()
            leave_hovered = is_hovered

            pygame.display.flip()

        return points, active_upgrades


def load_hud_icons():
    """Return scaled icons for HUD usage."""
    icons = {}
    for item in UPGRADES:
        if item["name"] == "life":
            continue
        img = pygame.image.load(item["file"]).convert_alpha()
        icons[item["name"]] = pygame.transform.scale(img, (24, 24))
    return icons

