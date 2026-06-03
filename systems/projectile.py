"""Projectile primitive with optional user-approved visuals."""

from pathlib import Path
import pygame

from settings import HEIGHT, WIDTH


PROJECTILE_COLOR = (235, 235, 240)
PROJECTILE_OUTLINE = (95, 108, 128)


class Projectile:
    """A simple projectile that falls back safely when a visual is missing."""

    _sprite_cache = {}
    _transformed_sprite_cache = {}

    def __init__(
        self,
        x,
        y,
        direction,
        speed,
        damage,
        lifetime,
        width=18,
        height=10,
        knockback=180,
        sprite_path=None,
        sprite_paths=None,
        sprite_frame_delay=0.08,
        impact_sprite_paths=(),
        sprite_scale=1.0,
    ):
        self.x = float(x)
        self.y = float(y)
        self.direction = 1 if direction >= 0 else -1
        self.velocity_x = self.direction * speed
        self.damage = damage
        self.lifetime = lifetime
        self.width = width
        self.height = height
        self.knockback = knockback
        if sprite_paths is None:
            sprite_paths = (sprite_path,) if sprite_path is not None else ()
        self.sprite_paths = tuple(Path(path) for path in sprite_paths if path is not None)
        self.sprite_path = self.sprite_paths[0] if self.sprite_paths else None
        self.sprite_frame_delay = sprite_frame_delay
        self.sprite_frame_timer = 0.0
        self.sprite_frame_index = 0
        self.impact_sprite_paths = tuple(Path(path) for path in impact_sprite_paths)
        self.sprite_scale = sprite_scale
        self.active = True
        self.hit_target_ids = set()
        self.rect = pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt, animation_dt=None):
        """Move and expire the projectile."""
        if not self.active:
            return

        if animation_dt is None:
            animation_dt = dt
        self.x += self.velocity_x * dt
        if len(self.sprite_paths) > 1:
            self.sprite_frame_timer += animation_dt
            while self.sprite_frame_timer >= self.sprite_frame_delay:
                self.sprite_frame_timer -= self.sprite_frame_delay
                self.sprite_frame_index = (self.sprite_frame_index + 1) % len(self.sprite_paths)
        self.lifetime = max(0.0, self.lifetime - dt)
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

        if self.lifetime <= 0 or self.rect.right < 0 or self.rect.left > WIDTH:
            self.active = False
        elif self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.active = False

    def draw(self, surface):
        """Draw an approved visual or retain the neutral rectangle fallback."""
        if not self.active:
            return

        sprite = self.load_sprite()
        if sprite is not None:
            sprite = self.get_transformed_sprite(sprite)
            surface.blit(sprite, sprite.get_rect(center=self.rect.center))
            return

        pygame.draw.rect(surface, PROJECTILE_COLOR, self.rect, border_radius=3)
        pygame.draw.rect(surface, PROJECTILE_OUTLINE, self.rect, 1, border_radius=3)

    def load_sprite(self):
        """Load an optional sprite once without making missing assets fatal."""
        if not self.sprite_paths:
            return None
        sprite_path = self.sprite_paths[self.sprite_frame_index % len(self.sprite_paths)]
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

    def get_transformed_sprite(self, sprite):
        """Reuse scaled and flipped projectile variants at high render rates."""
        sprite_path = self.sprite_paths[self.sprite_frame_index % len(self.sprite_paths)]
        cache_key = (str(sprite_path), self.sprite_scale, self.direction)
        if cache_key in self._transformed_sprite_cache:
            return self._transformed_sprite_cache[cache_key]
        transformed = sprite
        if self.sprite_scale != 1.0:
            transformed = pygame.transform.scale_by(transformed, self.sprite_scale)
        if self.direction < 0:
            transformed = pygame.transform.flip(transformed, True, False)
        self._transformed_sprite_cache[cache_key] = transformed
        return transformed

    def can_hit(self, enemy):
        """Return True if this projectile can damage the given enemy once."""
        return id(enemy) not in self.hit_target_ids

    def mark_hit(self, enemy):
        """Remember a hit target so damage is not repeated every frame."""
        self.hit_target_ids.add(id(enemy))
