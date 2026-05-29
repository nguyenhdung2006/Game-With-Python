"""Small UI-facing effect helpers."""

import pygame


def draw_counter_ready_glow(surface, rect, timer, color):
    """Draw a subtle glow while a parry-earned counter window is still active.

    Counter readiness should be visible enough to invite a punish, but calmer
    than a full attack effect so the screen does not become noisy.
    """
    if timer <= 0:
        return

    pulse_on = int(timer * 12) % 2 == 0
    alpha = 60 if pulse_on else 36
    glow_rect = rect.inflate(22, 18)
    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (*color, alpha), glow_surface.get_rect(), border_radius=10)
    surface.blit(glow_surface, glow_rect.topleft)
    pygame.draw.rect(surface, color, glow_rect, 2, border_radius=10)
