"""Shared completion-state overlay for lightweight match and run flow."""

import pygame

from settings import HEIGHT, WHITE, WIDTH


PANEL = (18, 22, 34)
MUTED = (190, 198, 212)


def draw_completion_overlay(surface, title, retry_label):
    """Draw a readable terminal-state panel with retry and menu actions."""
    title_font = pygame.font.Font(None, 72)
    prompt_font = pygame.font.Font(None, 30)
    panel = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 104, 500, 208)

    pygame.draw.rect(surface, PANEL, panel, border_radius=8)
    pygame.draw.rect(surface, WHITE, panel, 2, border_radius=8)

    rendered_title = title_font.render(title, True, WHITE)
    surface.blit(rendered_title, rendered_title.get_rect(center=(WIDTH // 2, panel.top + 66)))

    retry_prompt = prompt_font.render(f"R: {retry_label}", True, WHITE)
    surface.blit(retry_prompt, retry_prompt.get_rect(center=(WIDTH // 2, panel.top + 126)))

    menu_prompt = prompt_font.render("Esc: Return to Mode Select", True, MUTED)
    surface.blit(menu_prompt, menu_prompt.get_rect(center=(WIDTH // 2, panel.top + 162)))
