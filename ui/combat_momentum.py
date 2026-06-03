"""Compact presentation HUD for combat momentum."""

import pygame

from settings import WIDTH
from ui.fonts import get_font


PANEL = (14, 19, 30)
PANEL_BORDER = (74, 96, 126)
TRACK = (28, 36, 52)
MUTED = (170, 184, 205)
WHITE = (240, 244, 250)


def draw_combat_momentum(surface, momentum):
    """Draw a centered flow meter without covering combat-space actors."""
    panel = pygame.Rect(WIDTH // 2 - 154, 62, 308, 64)
    rank, accent = momentum.current_rank()
    if momentum.pulse_timer > 0:
        accent = brighten(accent, 24)

    pygame.draw.rect(surface, PANEL, panel, border_radius=8)
    pygame.draw.rect(surface, accent if momentum.chain_count else PANEL_BORDER, panel, 2, border_radius=8)

    title = get_font(17).render("COMBAT MOMENTUM", True, MUTED)
    surface.blit(title, (panel.left + 12, panel.top + 7))
    rank_text = get_font(30).render(rank, True, accent)
    surface.blit(rank_text, (panel.right - rank_text.get_width() - 12, panel.top + 4))

    track = pygame.Rect(panel.left + 12, panel.top + 34, panel.width - 24, 9)
    pygame.draw.rect(surface, TRACK, track, border_radius=5)
    fill_width = round(track.width * momentum.score_ratio())
    if fill_width > 0:
        pygame.draw.rect(surface, accent, (track.left, track.top, fill_width, track.height), border_radius=5)

    chain = f"{momentum.chain_count} CHAIN" if momentum.chain_count else momentum.last_event
    detail = get_font(16).render(chain, True, WHITE if momentum.chain_count else MUTED)
    surface.blit(detail, (panel.left + 12, panel.top + 46))


def brighten(color, amount):
    """Return an RGB color with a small readable pulse."""
    return tuple(min(255, channel + amount) for channel in color)
