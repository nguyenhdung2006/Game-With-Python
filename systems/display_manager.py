"""Small display-mode controller for safe window and fullscreen switching."""

import pygame

from settings import HEIGHT, WIDTH


class DisplayManager:
    """Own the active display surface while preferences change at runtime."""

    def __init__(self):
        self.surface = None

    def apply_fullscreen(self, enabled):
        """Apply one display mode and return pygame's current display surface."""
        flags = pygame.FULLSCREEN | pygame.SCALED if enabled else 0
        try:
            self.surface = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        except pygame.error:
            self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        return self.surface

    def handle_setting_changed(self, key, value):
        """React only to settings that require rebuilding the display surface."""
        if key == "fullscreen_enabled":
            self.apply_fullscreen(value)
