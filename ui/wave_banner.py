"""Wave intro and encounter banner helpers."""

import pygame

from settings import ENCOUNTER_WAVE_BANNER_FADE_TIME, WHITE, WIDTH


def draw_wave_banner(surface, text, timer, duration):
    """Draw a centered wave banner that fades out over time."""
    if timer <= 0 or not text:
        return

    alpha = get_banner_alpha(timer, duration)
    font = pygame.font.Font(None, 72)
    text_surface = font.render(text, True, WHITE)

    banner_surface = pygame.Surface(
        (text_surface.get_width() + 48, text_surface.get_height() + 28),
        pygame.SRCALPHA,
    )
    pygame.draw.rect(
        banner_surface,
        (18, 20, 34, int(alpha * 0.45)),
        banner_surface.get_rect(),
        border_radius=10,
    )
    line_rect = pygame.Rect(18, banner_surface.get_height() - 10, banner_surface.get_width() - 36, 3)
    pygame.draw.rect(
        banner_surface,
        (255, 226, 150, int(alpha * 0.75)),
        line_rect,
        border_radius=3,
    )
    text_surface.set_alpha(alpha)
    banner_surface.blit(text_surface, (24, 14))

    banner_rect = banner_surface.get_rect(center=(WIDTH // 2, 230))
    surface.blit(banner_surface, banner_rect)


def get_banner_alpha(timer, duration):
    """Return a fade alpha for the current banner timer."""
    fade_in = min(1.0, (duration - timer) / max(0.001, ENCOUNTER_WAVE_BANNER_FADE_TIME))
    fade_out = min(1.0, timer / max(0.001, ENCOUNTER_WAVE_BANNER_FADE_TIME))
    return int(255 * min(fade_in, fade_out))
