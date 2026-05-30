"""Neutral projectile primitive for future skill-defined attacks."""

import pygame

from settings import HEIGHT, WIDTH


PROJECTILE_COLOR = (235, 235, 240)
PROJECTILE_OUTLINE = (95, 108, 128)


class Projectile:
    """A simple mechanical projectile with no fantasy identity."""

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
        self.active = True
        self.hit_target_ids = set()
        self.rect = pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt):
        """Move and expire the projectile."""
        if not self.active:
            return

        self.x += self.velocity_x * dt
        self.lifetime = max(0.0, self.lifetime - dt)
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

        if self.lifetime <= 0 or self.rect.right < 0 or self.rect.left > WIDTH:
            self.active = False
        elif self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.active = False

    def draw(self, surface):
        """Draw a neutral rectangle so future visuals can replace it cleanly."""
        if not self.active:
            return

        pygame.draw.rect(surface, PROJECTILE_COLOR, self.rect, border_radius=3)
        pygame.draw.rect(surface, PROJECTILE_OUTLINE, self.rect, 1, border_radius=3)

    def can_hit(self, enemy):
        """Return True if this projectile can damage the given enemy once."""
        return id(enemy) not in self.hit_target_ids

    def mark_hit(self, enemy):
        """Remember a hit target so damage is not repeated every frame."""
        self.hit_target_ids.add(id(enemy))
