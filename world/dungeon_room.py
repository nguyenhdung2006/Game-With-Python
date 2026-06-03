"""Dungeon room identity and geometry layered over the existing arena."""

from pathlib import Path

import pygame

from settings import GROUND_Y, HEIGHT, WHITE, WIDTH
from ui.fonts import get_font
from world.battlefield import draw_arena


WALL_COLOR = (104, 118, 142)
WALL_SHADOW = (42, 48, 62)
BOUNDS_COLOR = (118, 142, 170)
DOOR_COLOR = (112, 210, 180)
DOOR_SHADOW = (34, 72, 72)
LABEL_COLOR = (205, 220, 238)
_ROOM_BACKGROUND_CACHE = {}
_DUNGEON_BACKDROP_CACHE = {}
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DUNGEON_BACKDROP_PATH = PROJECT_ROOT / "assets" / "sprites" / "backgrounds" / "seeone-old-dungeon-runtime.png"


def draw_dungeon_room(surface, layout, show_exit=False, decor_renderer=None):
    """Draw the arena plus simple layout markers for the current room."""
    if layout is None:
        draw_arena(surface)
        return

    surface.blit(get_room_background(layout), (0, 0))
    door_drawn = False
    if decor_renderer is not None:
        door_drawn = decor_renderer.draw(surface, layout, show_exit)
    if show_exit and not door_drawn:
        draw_exit_marker(surface, layout)
    draw_room_label(surface, layout)


def get_room_background(layout):
    """Cache fixed room masonry and bounds while decor remains dynamic."""
    cached = _ROOM_BACKGROUND_CACHE.get(layout.layout_id)
    if cached is not None:
        return cached

    background = pygame.Surface((WIDTH, HEIGHT))
    draw_arena(background)
    draw_room_interior(background, layout)
    draw_arena_bounds(background, layout)
    draw_wall_markers(background, layout)
    _ROOM_BACKGROUND_CACHE[layout.layout_id] = background
    return background
def draw_room_interior(surface, layout):
    """Give Dungeon rooms a quiet stone interior distinct from the Solo arena."""
    x, y, width, height = layout.room_bounds
    pygame.draw.rect(surface, (26, 31, 42), (x, y, width, height))
    pygame.draw.rect(surface, (38, 45, 58), (x + 18, y + 18, width - 36, height - 18))
    draw_dungeon_backdrop(surface, (x + 18, y + 18, width - 36, height - 18))
    for brick_y in range(y + 34, GROUND_Y, 32):
        row_offset = 0 if (brick_y // 32) % 2 == 0 else 24
        pygame.draw.line(surface, (50, 59, 74), (x + 18, brick_y), (x + width - 18, brick_y), 1)
        for brick_x in range(x + 26 + row_offset, x + width - 18, 48):
            pygame.draw.line(surface, (48, 56, 70), (brick_x, brick_y), (brick_x, brick_y + 31), 1)
    pygame.draw.rect(surface, (54, 60, 72), (x + 18, GROUND_Y - 18, width - 36, 18))


def draw_dungeon_backdrop(surface, bounds):
    """Blend one licensed side-view backdrop under masonry for readable depth."""
    backdrop = get_dungeon_backdrop(bounds[2:])
    if backdrop is None:
        return

    surface.blit(backdrop, bounds[:2])
    shade = pygame.Surface(bounds[2:], pygame.SRCALPHA)
    shade.fill((7, 10, 18, 78))
    surface.blit(shade, bounds[:2])


def get_dungeon_backdrop(size):
    """Load and scale the optional runtime backdrop once per room size."""
    if size in _DUNGEON_BACKDROP_CACHE:
        return _DUNGEON_BACKDROP_CACHE[size]

    if not DUNGEON_BACKDROP_PATH.exists():
        _DUNGEON_BACKDROP_CACHE[size] = None
        return None

    try:
        source = pygame.image.load(str(DUNGEON_BACKDROP_PATH)).convert_alpha()
    except pygame.error:
        _DUNGEON_BACKDROP_CACHE[size] = None
        return None

    backdrop = pygame.transform.scale(source, size)
    _DUNGEON_BACKDROP_CACHE[size] = backdrop
    return backdrop


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
    """Draw a compact authored room label without hiding combat space."""
    title_font = get_font(28)
    subtitle_font = get_font(20)
    title = title_font.render(layout.label, True, LABEL_COLOR)
    subtitle = subtitle_font.render(layout.subtitle.upper(), True, BOUNDS_COLOR)
    width = max(title.get_width(), subtitle.get_width()) + 30
    panel = pygame.Rect(WIDTH // 2 - width // 2, 8, width, 48)
    pygame.draw.rect(surface, WALL_SHADOW, panel, border_radius=4)
    pygame.draw.rect(surface, BOUNDS_COLOR, panel, 2, border_radius=4)
    surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + 15)))
    surface.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.top + 34)))
