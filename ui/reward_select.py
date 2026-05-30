"""Mechanical reward selection UI."""

import pygame

from settings import HEIGHT, WHITE, WIDTH


CARD = (30, 35, 50)
CARD_SELECTED = (48, 58, 82)
ACCENT = (130, 220, 255)
MUTED = (190, 198, 212)


def draw_reward_select(surface, reward_manager):
    """Draw three reward options and confirmation instructions."""
    _draw_center_text(surface, "Room Cleared", 142, 50, ACCENT)
    _draw_center_text(surface, "Choose 1 Reward", 196, 38, WHITE)

    options = reward_manager.current_options
    if not options:
        _draw_center_text(surface, "No rewards available", HEIGHT // 2, 34, MUTED)
        return

    card_width = 300
    card_height = 150
    gap = 26
    total_width = card_width * len(options) + gap * (len(options) - 1)
    start_x = WIDTH // 2 - total_width // 2
    y = 275

    for index, reward in enumerate(options):
        rect = pygame.Rect(start_x + index * (card_width + gap), y, card_width, card_height)
        selected = index == reward_manager.selected_index
        draw_reward_card(surface, rect, reward, selected)

    _draw_center_text(surface, "A/D or Left/Right to choose. Enter confirms.", HEIGHT - 92, 28, MUTED)


def draw_reward_card(surface, rect, reward, selected):
    """Draw one reward option card."""
    color = CARD_SELECTED if selected else CARD
    border = ACCENT if selected else MUTED
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, border, rect, 3 if selected else 2, border_radius=6)

    title_font = pygame.font.Font(None, 34)
    desc_font = pygame.font.Font(None, 25)

    title_surface = title_font.render(reward.display_name, True, WHITE)
    desc_surface = desc_font.render(reward.description, True, MUTED)

    surface.blit(title_surface, title_surface.get_rect(center=(rect.centerx, rect.top + 46)))
    surface.blit(desc_surface, desc_surface.get_rect(center=(rect.centerx, rect.top + 94)))


def _draw_center_text(surface, text, center_y, size, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, center_y))
    surface.blit(text_surface, text_rect)
