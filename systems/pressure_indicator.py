"""Subtle pressure and aggressor readability helpers."""

import pygame

from settings import PRESSURE_ACTIVE_COLOR, PRESSURE_INDICATOR_COLOR


def draw_pressure_indicator(surface, enemy):
    """Draw a small anticipation pulse over enemies about to pressure."""
    if enemy.pressure_indicator_timer <= 0:
        return

    pulse = int(enemy.pressure_indicator_timer * 18) % 2 == 0
    radius = 10 if pulse else 8
    alpha = 120 if pulse else 70
    center = (enemy.rect.centerx, enemy.rect.top - 18)

    indicator_surface = pygame.Surface((36, 36), pygame.SRCALPHA)
    pygame.draw.circle(indicator_surface, (*PRESSURE_INDICATOR_COLOR, alpha), (18, 18), radius, 3)
    pygame.draw.circle(indicator_surface, (*PRESSURE_INDICATOR_COLOR, alpha // 2), (18, 18), 4)
    surface.blit(indicator_surface, (center[0] - 18, center[1] - 18))


def draw_active_aggressor_indicator(surface, enemy):
    """Draw a brief focus outline for the currently emphasized aggressor."""
    if enemy.aggression_focus_timer <= 0:
        return

    outline_rect = enemy.rect.inflate(12, 12)
    pulse = int(enemy.aggression_focus_timer * 16) % 2 == 0
    color = PRESSURE_ACTIVE_COLOR if pulse else PRESSURE_INDICATOR_COLOR
    outline_surface = pygame.Surface((outline_rect.width, outline_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(
        outline_surface,
        (*color, 60),
        outline_surface.get_rect(),
        border_radius=8,
    )
    surface.blit(outline_surface, outline_rect.topleft)
    pygame.draw.rect(surface, color, outline_rect, 3, border_radius=8)
