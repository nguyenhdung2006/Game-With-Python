"""Shared cached default fonts for lightweight Pygame UI."""

import pygame


_FONT_CACHE = {}


def get_font(size):
    """Return one reused default font for the requested pixel size."""
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = pygame.font.Font(None, size)
    return _FONT_CACHE[size]
