"""Reusable health bar UI."""

import pygame

from settings import HEALTH_BG, WHITE
from ui.fonts import get_font


PANEL = (14, 19, 30)
PANEL_BORDER = (74, 96, 126)
MUTED = (198, 208, 222)


def draw_health_bar(surface, x, y, width, height, health, max_health, fill_color, label):
    """Draw a polished labeled health bar for any character."""
    max_health = max(1, max_health)
    health = max(0, min(health, max_health))
    fill_width = int(width * (health / max_health))
    track = pygame.Rect(x, y, width, height)

    pygame.draw.rect(surface, PANEL, track.inflate(8, 8), border_radius=5)
    pygame.draw.rect(surface, PANEL_BORDER, track.inflate(8, 8), 2, border_radius=5)
    pygame.draw.rect(surface, HEALTH_BG, track)
    if fill_width > 0:
        fill = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(surface, fill_color, fill)
        highlight = pygame.Rect(fill.left, fill.top, fill.width, max(3, fill.height // 3))
        pygame.draw.rect(surface, brighten(fill_color, 26), highlight)

    for segment in range(1, 4):
        segment_x = x + round(width * segment / 4)
        pygame.draw.line(surface, PANEL, (segment_x, y + 1), (segment_x, y + height - 2), 1)

    pygame.draw.rect(surface, WHITE, track, 2)
    text = get_font(28).render(label, True, WHITE)
    surface.blit(text, (x, y - 32))
    value = get_font(22).render(f"{format_number(health)} / {format_number(max_health)}", True, MUTED)
    surface.blit(value, (x + width - value.get_width(), y - 27))


def brighten(color, amount):
    """Return a slightly brighter RGB color."""
    return tuple(min(255, channel + amount) for channel in color)


def format_number(value):
    """Render health as an integer where possible."""
    if int(value) == value:
        return str(int(value))
    return f"{value:.1f}"
