"""Simple mode select and locked-mode screens."""

import pygame

from settings import HEIGHT, WHITE, WIDTH


MENU_BG = (12, 14, 24)
PANEL = (28, 31, 44)
PANEL_HIGHLIGHT = (45, 54, 76)
ACCENT = (130, 220, 255)
LOCKED = (165, 170, 184)
TEXT_MUTED = (185, 192, 206)


def draw_mode_select(surface):
    """Draw the launch menu for choosing the current game mode."""
    surface.fill(MENU_BG)
    _draw_center_text(surface, "ANIME COMBAT PROJECT", 118, 64, ACCENT)
    _draw_center_text(surface, "Select Mode", 185, 42, WHITE)

    options = [
        ("1", "Solo / Versus", "Playable 1v1 arena sandbox", True),
        ("2", "Dungeon / Wave Mode", "Playable combat vertical slice", True),
        ("3", "Team Round 3v3", "Coming soon", False),
    ]

    start_y = 255
    for index, option in enumerate(options):
        _draw_mode_option(surface, start_y + index * 92, *option)

    _draw_center_text(surface, "Press 1 / 2 / 3 to choose. Esc quits.", HEIGHT - 72, 28, TEXT_MUTED)


def draw_team_locked(surface):
    """Draw the Team Round 3v3 locked screen."""
    draw_placeholder_screen(
        surface,
        "Team Round 3v3 - Coming Soon",
        "Future mode: fighters battle round-by-round until one team is defeated.",
    )


def draw_placeholder_screen(surface, title, description):
    """Draw a shared coming-soon screen with back navigation."""
    surface.fill(MENU_BG)
    _draw_center_text(surface, "ANIME COMBAT PROJECT", 118, 54, ACCENT)
    _draw_center_text(surface, title, 262, 46, WHITE)
    _draw_center_text(surface, description, 330, 30, TEXT_MUTED)
    _draw_center_text(surface, "Esc returns to Mode Select", HEIGHT - 90, 28, TEXT_MUTED)


def _draw_mode_option(surface, y, key_label, title, subtitle, playable):
    rect = pygame.Rect(WIDTH // 2 - 310, y, 620, 66)
    color = PANEL_HIGHLIGHT if playable else PANEL
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, ACCENT if playable else LOCKED, rect, 2, border_radius=6)

    key_font = pygame.font.Font(None, 42)
    title_font = pygame.font.Font(None, 36)
    subtitle_font = pygame.font.Font(None, 25)

    key_color = ACCENT if playable else LOCKED
    title_color = WHITE if playable else LOCKED

    key_surface = key_font.render(f"[{key_label}]", True, key_color)
    title_surface = title_font.render(title, True, title_color)
    subtitle_surface = subtitle_font.render(subtitle, True, TEXT_MUTED)

    surface.blit(key_surface, (rect.left + 24, rect.centery - key_surface.get_height() // 2))
    surface.blit(title_surface, (rect.left + 112, rect.top + 12))
    surface.blit(subtitle_surface, (rect.left + 112, rect.top + 40))


def _draw_center_text(surface, text, center_y, size, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, center_y))
    surface.blit(text_surface, text_rect)
