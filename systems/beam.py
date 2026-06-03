"""Simple beam prototype for user-approved character skills."""

from pathlib import Path
import pygame

from settings import WIDTH


BEAM_COLOR = (140, 210, 255)
BEAM_OUTLINE = (235, 245, 255)


class Beam:
    """A short-lived horizontal hitbox that penetrates every enemy in range."""

    _sprite_cache = {}

    def __init__(
        self,
        x,
        y,
        direction,
        beam_range,
        height,
        damage,
        duration,
        knockback=420,
        sprite_path=None,
    ):
        self.x = x
        self.y = y
        self.direction = 1 if direction >= 0 else -1
        self.range = beam_range
        self.height = height
        self.damage = damage
        self.duration = duration
        self.knockback = knockback
        self.sprite_path = Path(sprite_path) if sprite_path is not None else None
        self.active = True
        self.hit_target_ids = set()
        self.extended_sprite_cache = {}
        self.rect = self.create_hitbox()

    def create_hitbox(self, beam_range=None):
        """Build the beam rectangle from the player-facing origin."""
        if beam_range is None:
            beam_range = self.range
        if self.direction >= 0:
            left = self.x
            right = min(WIDTH, self.x + beam_range)
        else:
            left = max(0, self.x - beam_range)
            right = self.x

        return pygame.Rect(
            round(left),
            round(self.y - self.height / 2),
            round(max(0, right - left)),
            self.height,
        )

    def refresh_hitbox(self, enemies):
        """Keep the full beam length so the blast visually pierces targets."""
        self.rect = self.create_hitbox()

    def update(self, dt):
        """Expire the beam after its short active window."""
        if not self.active:
            return

        self.duration = max(0.0, self.duration - dt)
        if self.duration <= 0:
            self.active = False

    def draw(self, surface):
        """Draw the approved beam sprite or retain the rectangle fallback."""
        if not self.active:
            return

        sprite = self.load_sprite()
        if sprite is not None and self.rect.width > 0:
            sprite = self.get_extended_sprite(sprite, self.rect.width)
            surface.blit(sprite, sprite.get_rect(center=self.rect.center))
            return

        pygame.draw.rect(surface, BEAM_COLOR, self.rect, border_radius=4)
        pygame.draw.rect(surface, BEAM_OUTLINE, self.rect, 2, border_radius=4)

    def get_extended_sprite(self, sprite, target_width):
        """Reuse the expensive beam-body extension while its width is stable."""
        cache_key = (target_width, self.direction)
        if cache_key not in self.extended_sprite_cache:
            extended = self.extend_sprite_body(sprite, target_width)
            if self.direction < 0:
                extended = pygame.transform.flip(extended, True, False)
            self.extended_sprite_cache[cache_key] = extended
        return self.extended_sprite_cache[cache_key]

    def extend_sprite_body(self, sprite, target_width):
        """Preserve both beam ends and repeat only its center column."""
        source_width = sprite.get_width()
        if target_width <= source_width:
            return sprite.copy()

        midpoint = source_width // 2
        left_half = sprite.subsurface((0, 0, midpoint, sprite.get_height()))
        right_half = sprite.subsurface(
            (midpoint, 0, source_width - midpoint, sprite.get_height())
        )
        center_column = sprite.subsurface((midpoint, 0, 1, sprite.get_height()))
        extended = pygame.Surface((target_width, sprite.get_height()), pygame.SRCALPHA)
        extended.blit(left_half, (0, 0))
        for x in range(left_half.get_width(), target_width - right_half.get_width()):
            extended.blit(center_column, (x, 0))
        extended.blit(right_half, (target_width - right_half.get_width(), 0))
        return extended

    def load_sprite(self):
        """Load the optional beam art once and fail back to placeholder safely."""
        if self.sprite_path is None:
            return None
        cache_key = str(self.sprite_path)
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        if not self.sprite_path.is_file():
            self._sprite_cache[cache_key] = None
            return None
        try:
            sprite = pygame.image.load(str(self.sprite_path)).convert_alpha()
        except (OSError, pygame.error):
            sprite = None
        self._sprite_cache[cache_key] = sprite
        return sprite

    def can_hit(self, enemy):
        """Return True if this beam has not damaged the enemy yet."""
        return id(enemy) not in self.hit_target_ids

    def mark_hit(self, enemy):
        """Track one hit per enemy per beam use."""
        self.hit_target_ids.add(id(enemy))
