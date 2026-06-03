"""Dungeon room status and progression UI helpers."""

import pygame

from managers.room_state import ROOM_BOSS_ENCOUNTER, ROOM_DUNGEON_CLEAR, ROOM_ENCOUNTER
from settings import HEIGHT, WHITE, WIDTH
from ui.fonts import get_font


ACCENT = (130, 220, 255)
CLEAR_COLOR = (255, 240, 180)
MUTED = (190, 198, 212)
PANEL = (18, 22, 34)


def draw_room_status(surface, room_manager, input_manager=None):
    """Draw the current room number and type during dungeon play."""
    if room_manager.is_dungeon_complete():
        draw_dungeon_cleared(surface, input_manager)
        return

    room_type = room_manager.current_room_type()
    room_label = format_room_type(room_type)
    text = f"Room {room_manager.room_number()} / {room_manager.total_rooms()} - {room_label}"
    _draw_panel_text(surface, text, 112, 32, ACCENT)


def draw_room_cleared(surface, input_manager=None):
    """Draw the room clear prompt shown between rooms."""
    _draw_center_text(surface, "Room Cleared", HEIGHT // 2 - 28, 54, CLEAR_COLOR)
    _draw_center_text(surface, "Reward selection next", HEIGHT // 2 + 26, 30, MUTED)
    confirm = binding_label(input_manager, "confirm", "Enter")
    _draw_center_text(surface, f"Press {confirm} to continue", HEIGHT // 2 + 66, 32, WHITE)


def draw_dungeon_cleared(surface, input_manager=None):
    """Draw final dungeon clear state."""
    _draw_center_text(surface, "Dungeon Cleared", HEIGHT // 2 - 18, 58, CLEAR_COLOR)
    back = binding_label(input_manager, "back", "Esc")
    _draw_center_text(surface, f"{back} returns to Mode Select", HEIGHT // 2 + 42, 30, MUTED)


def format_room_type(room_type):
    """Return readable labels for current room types."""
    if room_type == ROOM_ENCOUNTER:
        return "Encounter"
    if room_type == ROOM_BOSS_ENCOUNTER:
        return "Boss Encounter"
    if room_type == ROOM_DUNGEON_CLEAR:
        return "Dungeon Cleared"
    return room_type.replace("_", " ").title()


def _draw_panel_text(surface, text, center_y, size, color):
    font = get_font(size)
    text_surface = font.render(text, True, color)
    padding_x = 22
    padding_y = 10
    panel_rect = text_surface.get_rect(center=(WIDTH // 2, center_y)).inflate(padding_x * 2, padding_y * 2)
    pygame.draw.rect(surface, PANEL, panel_rect, border_radius=6)
    pygame.draw.rect(surface, color, panel_rect, 2, border_radius=6)
    surface.blit(text_surface, text_surface.get_rect(center=panel_rect.center))


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
