"""Lightweight sprite loading helpers with safe placeholder fallback."""

from pathlib import Path

import pygame


_SPRITE_CACHE = {}


def load_sprite(path, size=None, flip_x=False):
    """Load one sprite image, optionally scaled/flipped, or return None safely."""
    if not path:
        return None

    cache_key = (str(path), size, flip_x)
    if cache_key in _SPRITE_CACHE:
        return _SPRITE_CACHE[cache_key]

    sprite_path = Path(path)
    if not sprite_path.exists():
        _SPRITE_CACHE[cache_key] = None
        return None

    try:
        image = pygame.image.load(str(sprite_path))
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            image = image.convert_alpha()
    except (pygame.error, OSError):
        _SPRITE_CACHE[cache_key] = None
        return None

    if size is not None:
        image = pygame.transform.smoothscale(image, size)

    if flip_x:
        image = pygame.transform.flip(image, True, False)

    _SPRITE_CACHE[cache_key] = image
    return image


def get_state_sprite(entity, visual_state, fallback_state="idle"):
    """Return the configured sprite for an entity visual state, if available."""
    sprite_paths = getattr(entity, "sprite_paths", None)
    if not sprite_paths:
        return None

    path = sprite_paths.get(visual_state) or sprite_paths.get(fallback_state)
    size = getattr(entity, "sprite_size", None)
    flip_x = getattr(entity, "sprite_flip_with_facing", True) and getattr(entity, "facing", 1) < 0
    return load_sprite(path, size=size, flip_x=flip_x)


def draw_entity_sprite(surface, entity, draw_rect, visual_state):
    """Draw an entity sprite if configured; return True when drawn."""
    sprite = get_state_sprite(entity, visual_state)
    if sprite is None:
        return False

    offset_x, offset_y = getattr(entity, "sprite_offset", (0, 0))
    sprite_rect = sprite.get_rect()
    sprite_rect.midbottom = draw_rect.midbottom
    sprite_rect.x += offset_x
    sprite_rect.y += offset_y
    surface.blit(sprite, sprite_rect)
    return True
