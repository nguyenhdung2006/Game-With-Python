"""Simple beam prototype for user-approved character skills."""

import pygame

from settings import WIDTH


BEAM_COLOR = (140, 210, 255)
BEAM_OUTLINE = (235, 245, 255)


class Beam:
    """A short-lived horizontal hitbox that tracks hits once per enemy."""

    def __init__(self, x, y, direction, beam_range, height, damage, duration, knockback=420):
        self.x = x
        self.y = y
        self.direction = 1 if direction >= 0 else -1
        self.range = beam_range
        self.height = height
        self.damage = damage
        self.duration = duration
        self.knockback = knockback
        self.active = True
        self.hit_target_ids = set()
        self.rect = self.create_hitbox()

    def create_hitbox(self):
        """Build the beam rectangle from the player-facing origin."""
        if self.direction >= 0:
            left = self.x
            right = min(WIDTH, self.x + self.range)
        else:
            left = max(0, self.x - self.range)
            right = self.x

        return pygame.Rect(
            round(left),
            round(self.y - self.height / 2),
            round(max(0, right - left)),
            self.height,
        )

    def update(self, dt):
        """Expire the beam after its short active window."""
        if not self.active:
            return

        self.duration = max(0.0, self.duration - dt)
        if self.duration <= 0:
            self.active = False

    def draw(self, surface):
        """Draw a simple placeholder rectangle beam."""
        if not self.active:
            return

        pygame.draw.rect(surface, BEAM_COLOR, self.rect, border_radius=4)
        pygame.draw.rect(surface, BEAM_OUTLINE, self.rect, 2, border_radius=4)

    def can_hit(self, enemy):
        """Return True if this beam has not damaged the enemy yet."""
        return id(enemy) not in self.hit_target_ids

    def mark_hit(self, enemy):
        """Track one hit per enemy per beam use."""
        self.hit_target_ids.add(id(enemy))
