"""Enemy dummy entity.

The current enemy is still a simple rectangle, but this class gives it health,
hurt flash, knockback, and defeated state so future combat can plug in cleanly.
"""

import pygame

from settings import (
    ENEMY_COLOR,
    ENEMY_DEFEATED_COLOR,
    ENEMY_HEIGHT,
    ENEMY_HURT_COLOR,
    ENEMY_HURT_FLASH_DURATION,
    ENEMY_KNOCKBACK_FRICTION,
    ENEMY_MAX_HEALTH,
    ENEMY_WIDTH,
    WHITE,
    WIDTH,
)
from systems.effects import choose_flash_color
from systems.physics import clamp_x_to_screen, move_toward_zero


class Enemy:
    """A training dummy enemy for testing future combat."""

    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.max_health = ENEMY_MAX_HEALTH
        self.health = ENEMY_MAX_HEALTH
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.x = float(x)

        # hurt_flash_timer briefly changes the enemy color after taking damage.
        self.hurt_flash_timer = 0
        self.knockback_velocity_x = 0
        self.defeated = False

    def update(self, dt):
        """Update future hit feedback without changing idle dummy behavior."""
        if self.hurt_flash_timer > 0:
            self.hurt_flash_timer = max(0, self.hurt_flash_timer - dt)

        if self.knockback_velocity_x != 0:
            self.x += self.knockback_velocity_x * dt
            self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
            self.knockback_velocity_x = move_toward_zero(
                self.knockback_velocity_x,
                ENEMY_KNOCKBACK_FRICTION * dt,
            )
            self.rect.x = round(self.x)

    def take_damage(self, amount, knockback_x=0):
        """Receive damage while keeping health from dropping below zero."""
        if self.defeated:
            return

        self.health = max(0, self.health - amount)
        self.hurt_flash_timer = ENEMY_HURT_FLASH_DURATION
        self.knockback_velocity_x = knockback_x

        if self.health == 0:
            self.defeated = True

    def draw(self, surface):
        """Draw the enemy dummy rectangle."""
        if self.defeated:
            color = ENEMY_DEFEATED_COLOR
        else:
            color = choose_flash_color(ENEMY_COLOR, ENEMY_HURT_COLOR, self.hurt_flash_timer)

        # A small offset outline makes hits read more clearly before sprites exist.
        if self.hurt_flash_timer > 0 and not self.defeated:
            recoil_rect = self.rect.copy()
            recoil_rect.x -= 6 if self.knockback_velocity_x > 0 else -6
            pygame.draw.rect(surface, (120, 35, 45), recoil_rect, 3)

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)
