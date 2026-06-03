"""Shared completion-state overlay for lightweight match and run flow."""

import pygame

from settings import HEIGHT, WHITE, WIDTH
from ui.fonts import get_font


PANEL = (18, 22, 34)
MUTED = (190, 198, 212)


def draw_completion_overlay(surface, title, retry_label, input_manager=None):
    """Draw a readable terminal-state panel with retry and menu actions."""
    title_font = get_font(72)
    prompt_font = get_font(30)
    panel = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 104, 500, 208)

    pygame.draw.rect(surface, PANEL, panel, border_radius=8)
    pygame.draw.rect(surface, WHITE, panel, 2, border_radius=8)

    rendered_title = title_font.render(title, True, WHITE)
    surface.blit(rendered_title, rendered_title.get_rect(center=(WIDTH // 2, panel.top + 66)))

    retry_key = binding_label(input_manager, "retry", "R")
    retry_prompt = prompt_font.render(f"{retry_key}: {retry_label}", True, WHITE)
    surface.blit(retry_prompt, retry_prompt.get_rect(center=(WIDTH // 2, panel.top + 126)))

    back_key = binding_label(input_manager, "back", "Esc")
    menu_prompt = prompt_font.render(f"{back_key}: Return to Mode Select", True, MUTED)
    surface.blit(menu_prompt, menu_prompt.get_rect(center=(WIDTH // 2, panel.top + 162)))


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
