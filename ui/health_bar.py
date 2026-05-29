"""Reusable health bar UI."""

import pygame

from settings import HEALTH_BG, WHITE


def draw_health_bar(surface, x, y, width, height, health, max_health, fill_color, label):
    """Draw a labeled health bar for any character."""
    health = max(0, min(health, max_health))
    fill_width = int(width * (health / max_health))

    pygame.draw.rect(surface, HEALTH_BG, (x, y, width, height))
    pygame.draw.rect(surface, fill_color, (x, y, fill_width, height))
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 3)

    font = pygame.font.Font(None, 32)
    text = font.render(label, True, WHITE)
    surface.blit(text, (x, y - 32))
