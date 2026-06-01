"""Placeholder dungeon room markers layered over the existing arena."""

import pygame

from settings import GROUND_Y, WHITE, WIDTH
from world.battlefield import draw_arena


WALL_COLOR = (104, 118, 142)
WALL_SHADOW = (42, 48, 62)
BOUNDS_COLOR = (118, 142, 170)
DOOR_COLOR = (112, 210, 180)
DOOR_SHADOW = (34, 72, 72)
LABEL_COLOR = (205, 220, 238)


def draw_dungeon_room(surface, layout, show_exit=False, decor_renderer=None):
    """Draw the arena plus simple layout markers for the current room."""
    draw_arena(surface)
    if layout is None:
        return

    draw_room_interior(surface, layout)
    draw_arena_bounds(surface, layout)
    draw_wall_markers(surface, layout)
    door_drawn = False
    if decor_renderer is not None:
        door_drawn = decor_renderer.draw(surface, layout, show_exit)
    if show_exit and not door_drawn:
        draw_exit_marker(surface, layout)
    draw_room_label(surface, layout)


def draw_room_interior(surface, layout):
    """Give Dungeon rooms a quiet stone interior distinct from the Solo arena."""
    x, y, width, height = layout.room_bounds
    pygame.draw.rect(surface, (26, 31, 42), (x, y, width, height))
    pygame.draw.rect(surface, (38, 45, 58), (x + 18, y + 18, width - 36, height - 18))
    for brick_y in range(y + 34, GROUND_Y, 32):
        row_offset = 0 if (brick_y // 32) % 2 == 0 else 24
        pygame.draw.line(surface, (50, 59, 74), (x + 18, brick_y), (x + width - 18, brick_y), 1)
        for brick_x in range(x + 26 + row_offset, x + width - 18, 48):
            pygame.draw.line(surface, (48, 56, 70), (brick_x, brick_y), (brick_x, brick_y + 31), 1)
    pygame.draw.rect(surface, (54, 60, 72), (x + 18, GROUND_Y - 18, width - 36, 18))


def draw_arena_bounds(surface, layout):
    """Outline the placeholder playable floor bounds."""
    left, right = layout.arena_bounds
    pygame.draw.line(surface, BOUNDS_COLOR, (left, GROUND_Y + 14), (right, GROUND_Y + 14), 3)
    pygame.draw.line(surface, WALL_SHADOW, (left, GROUND_Y + 19), (right, GROUND_Y + 19), 2)


def draw_wall_markers(surface, layout):
    """Draw readable left and right layout boundary markers."""
    x, y, width, height = layout.room_bounds
    marker_width = 18
    pygame.draw.rect(surface, WALL_SHADOW, (x, y, marker_width, height))
    pygame.draw.rect(surface, WALL_COLOR, (x + 4, y, 6, height))
    pygame.draw.rect(surface, WALL_SHADOW, (x + width - marker_width, y, marker_width, height))
    pygame.draw.rect(surface, WALL_COLOR, (x + width - 10, y, 6, height))


def draw_exit_marker(surface, layout):
    """Draw a neutral open-door marker after a combat room is cleared."""
    if layout.exit_position is None:
        return

    x, y = layout.exit_position
    door_rect = pygame.Rect(x, y, 42, GROUND_Y - y)
    pygame.draw.rect(surface, DOOR_SHADOW, door_rect)
    pygame.draw.rect(surface, DOOR_COLOR, door_rect, 3)
    pygame.draw.line(surface, WHITE, (x + 12, y + 18), (x + 30, y + 18), 2)


def draw_room_label(surface, layout):
    """Draw a compact mechanical room label."""
    font = pygame.font.Font(None, 28)
    rendered = font.render(layout.label, True, LABEL_COLOR)
    panel = rendered.get_rect(center=(WIDTH // 2, 28)).inflate(24, 12)
    pygame.draw.rect(surface, WALL_SHADOW, panel, border_radius=4)
    pygame.draw.rect(surface, BOUNDS_COLOR, panel, 2, border_radius=4)
    surface.blit(rendered, rendered.get_rect(center=panel.center))
