"""Mechanical reward selection UI."""

import pygame

from settings import HEIGHT, WHITE, WIDTH
from ui.fonts import get_font


CARD = (30, 35, 50)
CARD_SELECTED = (48, 58, 82)
ACCENT = (130, 220, 255)
MUTED = (190, 198, 212)
CATEGORY = (255, 220, 150)


def draw_reward_select(surface, reward_manager, input_manager=None):
    """Draw three reward options and confirmation instructions."""
    _draw_center_text(surface, "Room Cleared", 142, 50, ACCENT)
    _draw_center_text(surface, "Choose 1 Reward", 196, 38, WHITE)

    options = reward_manager.current_options
    if not options:
        _draw_center_text(surface, "No rewards available", HEIGHT // 2, 34, MUTED)
        return

    card_width = 300
    card_height = 174
    gap = 26
    total_width = card_width * len(options) + gap * (len(options) - 1)
    start_x = WIDTH // 2 - total_width // 2
    y = 275

    for index, reward in enumerate(options):
        rect = pygame.Rect(start_x + index * (card_width + gap), y, card_width, card_height)
        selected = index == reward_manager.selected_index
        draw_reward_card(surface, rect, reward, reward_manager.stack_count(reward.reward_id), selected)

    left = binding_label(input_manager, "move_left", "A")
    right = binding_label(input_manager, "move_right", "D")
    confirm = binding_label(input_manager, "confirm", "Enter")
    _draw_center_text(surface, f"{left}/{right} or Left/Right to choose. {confirm} confirms.", HEIGHT - 92, 28, MUTED)


def draw_reward_card(surface, rect, reward, stack_count, selected):
    """Draw one reward option card."""
    color = CARD_SELECTED if selected else CARD
    border = ACCENT if selected else MUTED
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, border, rect, 3 if selected else 2, border_radius=6)

    title_font = get_font(34)
    desc_font = get_font(25)
    detail_font = get_font(23)

    title_surface = title_font.render(reward.display_name, True, WHITE)
    desc_surface = desc_font.render(reward.description, True, MUTED)
    stack_label = format_stack_label(stack_count, reward.max_stacks)
    detail_surface = detail_font.render(f"{reward.category.upper()}  |  {stack_label}", True, CATEGORY)

    surface.blit(title_surface, title_surface.get_rect(center=(rect.centerx, rect.top + 42)))
    surface.blit(detail_surface, detail_surface.get_rect(center=(rect.centerx, rect.top + 82)))
    surface.blit(desc_surface, desc_surface.get_rect(center=(rect.centerx, rect.top + 126)))


def format_stack_label(stack_count, max_stacks):
    """Return the next stack number and configured cap for one reward."""
    next_stack = stack_count + 1
    if max_stacks is None:
        return f"Stack {next_stack}"
    return f"Stack {next_stack} / {max_stacks}"


def _draw_center_text(surface, text, center_y, size, color):
    font = get_font(size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, center_y))
    surface.blit(text_surface, text_rect)


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
