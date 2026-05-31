"""Shared pause overlay for playable game modes."""

import pygame

from settings import HEIGHT, WHITE, WIDTH


DIM_COLOR = (0, 0, 0, 150)
PANEL = (18, 22, 34)
MUTED = (190, 198, 212)


def draw_pause_overlay(surface, restart_label, input_manager=None):
    """Dim the current scene and draw compact pause actions."""
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill(DIM_COLOR)
    surface.blit(dim, (0, 0))

    title_font = pygame.font.Font(None, 72)
    prompt_font = pygame.font.Font(None, 30)
    panel = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 132, 500, 264)

    pygame.draw.rect(surface, PANEL, panel, border_radius=8)
    pygame.draw.rect(surface, WHITE, panel, 2, border_radius=8)

    title = title_font.render("Paused", True, WHITE)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, panel.top + 62)))

    prompts = (
        f"{binding_label(input_manager, 'pause', 'P')}: Resume",
        f"{binding_label(input_manager, 'retry', 'R')}: {restart_label}",
        f"{binding_label(input_manager, 'help', 'H')}: Controls",
        f"{binding_label(input_manager, 'back', 'Esc')}: Return to Mode Select",
    )
    for index, prompt in enumerate(prompts):
        color = WHITE if index < 2 else MUTED
        rendered = prompt_font.render(prompt, True, color)
        surface.blit(rendered, rendered.get_rect(center=(WIDTH // 2, panel.top + 124 + index * 32)))


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
