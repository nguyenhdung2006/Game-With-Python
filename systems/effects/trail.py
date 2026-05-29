"""Trail and timed-effect helpers."""

import pygame


def create_afterimage(rect, lifetime):
    """Create one transparent rectangle copy for a dash trail."""
    return {
        "rect": rect.copy(),
        "timer": lifetime,
    }


def update_timed_effects(effects, dt):
    """Count down effect timers and remove expired effects."""
    for effect in effects:
        effect["timer"] -= dt

    return [effect for effect in effects if effect["timer"] > 0]


def draw_rect_afterimages(surface, afterimages, size, lifetime, color):
    """Draw fading rectangle afterimages."""
    width, height = size

    for afterimage in afterimages:
        fade_amount = afterimage["timer"] / lifetime
        alpha = int(120 * fade_amount)

        trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        trail_surface.fill((*color, alpha))
        surface.blit(trail_surface, afterimage["rect"].topleft)
