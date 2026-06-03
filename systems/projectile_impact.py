"""Short projectile impact playback for approved hit effects."""

from pathlib import Path
import pygame


class ProjectileImpact:
    """Play a small transparent sprite sequence once at a collision point."""

    _sprite_cache = {}

    def __init__(self, center, sprite_paths, frame_delay=0.08):
        self.center = center
        self.sprite_paths = tuple(Path(path) for path in sprite_paths)
        self.frame_delay = frame_delay
        self.frame_index = 0
        self.frame_timer = 0.0
        self.active = bool(self.sprite_paths)

    def update(self, dt):
        """Advance once through the approved impact frames."""
        if not self.active:
            return
        self.frame_timer += dt
        while self.frame_timer >= self.frame_delay and self.active:
            self.frame_timer -= self.frame_delay
            self.frame_index += 1
            if self.frame_index >= len(self.sprite_paths):
                self.active = False

    def draw(self, surface):
        """Draw the current impact frame centered on the collision."""
        if not self.active:
            return
        sprite = self.load_sprite()
        if sprite is not None:
            surface.blit(sprite, sprite.get_rect(center=self.center))

    def load_sprite(self):
        """Load the current frame once and tolerate missing optional assets."""
        if not self.active:
            return None
        sprite_path = self.sprite_paths[self.frame_index]
        cache_key = str(sprite_path)
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        if not sprite_path.is_file():
            self._sprite_cache[cache_key] = None
            return None
        try:
            sprite = pygame.image.load(str(sprite_path)).convert_alpha()
        except (OSError, pygame.error):
            sprite = None
        self._sprite_cache[cache_key] = sprite
        return sprite
