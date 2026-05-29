"""Enemy dummy entity.

The current enemy is still a simple rectangle, but this class gives it health,
hurt flash, knockback, and defeated state so future combat can plug in cleanly.
"""

import pygame

from settings import (
    ENEMY_ATTACK_COLOR,
    ENEMY_ATTACK_COOLDOWN,
    ENEMY_ATTACK_DURATION,
    ENEMY_ATTACK_START_DISTANCE,
    ENEMY_CHASE_SPEED,
    ENEMY_COLOR,
    ENEMY_DEFEATED_COLOR,
    ENEMY_HEIGHT,
    ENEMY_HURT_COLOR,
    ENEMY_HURT_FLASH_DURATION,
    ENEMY_KNOCKBACK_FRICTION,
    ENEMY_MAX_HEALTH,
    ENEMY_RETREAT_DURATION,
    ENEMY_RETREAT_SPEED,
    ENEMY_STATE_ATTACK,
    ENEMY_STATE_CHASE,
    ENEMY_STATE_DEFEATED,
    ENEMY_STATE_HURT,
    ENEMY_STATE_IDLE,
    ENEMY_STATE_TELEGRAPH,
    ENEMY_TELEGRAPH_COLOR,
    ENEMY_TELEGRAPH_DURATION,
    ENEMY_WIDTH,
    WHITE,
    WIDTH,
)
from systems.combat import create_enemy_attack_hitbox
from systems.effects import choose_flash_color, draw_enemy_attack_rectangle, draw_enemy_warning
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
        self.facing = -1

        # The enemy AI uses a simple state machine so behavior stays readable.
        self.state = ENEMY_STATE_IDLE
        self.telegraph_timer = 0
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.has_hit_this_attack = False
        self.retreat_timer = 0

    def update(self, player, dt):
        """Update simple AI, attack timing, hurt recoil, and cooldowns."""
        self.update_timers(dt)

        if self.defeated:
            self.state = ENEMY_STATE_DEFEATED
            self.knockback_velocity_x = 0
            return

        if self.hurt_flash_timer > 0:
            self.state = ENEMY_STATE_HURT
            self.update_knockback(dt)
            return

        self.face_player(player)

        if self.retreat_timer > 0:
            self.update_retreat(dt)
        elif self.state == ENEMY_STATE_TELEGRAPH:
            self.update_telegraph(dt)
        elif self.state == ENEMY_STATE_ATTACK:
            self.update_attack(dt)
        else:
            self.update_idle_or_chase(player, dt)

        self.update_knockback(dt)

    def update_timers(self, dt):
        """Count down cooldowns and hurt flash with delta time."""
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer = max(0, self.attack_cooldown_timer - dt)

        if self.hurt_flash_timer > 0:
            self.hurt_flash_timer = max(0, self.hurt_flash_timer - dt)

        if self.retreat_timer > 0:
            self.retreat_timer = max(0, self.retreat_timer - dt)

    def update_knockback(self, dt):
        """Move the enemy while knockback is still active."""
        if self.knockback_velocity_x == 0:
            return

        self.x += self.knockback_velocity_x * dt
        self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
        self.knockback_velocity_x = move_toward_zero(
            self.knockback_velocity_x,
            ENEMY_KNOCKBACK_FRICTION * dt,
        )
        self.rect.x = round(self.x)

    def face_player(self, player):
        """Turn toward the player before chasing or attacking."""
        if player.rect.centerx >= self.rect.centerx:
            self.facing = 1
        else:
            self.facing = -1

    def update_idle_or_chase(self, player, dt):
        """Chase when far away, or start telegraphing when close enough."""
        distance_to_player = abs(player.rect.centerx - self.rect.centerx)

        if distance_to_player > ENEMY_ATTACK_START_DISTANCE:
            self.state = ENEMY_STATE_CHASE
            self.x += self.facing * ENEMY_CHASE_SPEED * dt
            self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
            self.rect.x = round(self.x)
            return

        self.state = ENEMY_STATE_IDLE

        if self.attack_cooldown_timer <= 0:
            self.start_telegraph()

    def update_retreat(self, dt):
        """Step away after attacking to create readable combat spacing."""
        self.state = ENEMY_STATE_IDLE
        self.x -= self.facing * ENEMY_RETREAT_SPEED * dt
        self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
        self.rect.x = round(self.x)

    def start_telegraph(self):
        """Begin a visible warning before the enemy attack."""
        self.state = ENEMY_STATE_TELEGRAPH
        self.telegraph_timer = ENEMY_TELEGRAPH_DURATION

    def update_telegraph(self, dt):
        """Wait briefly so the player has time to dodge."""
        self.telegraph_timer -= dt

        if self.telegraph_timer <= 0:
            self.start_attack()

    def start_attack(self):
        """Start the active enemy attack window."""
        self.state = ENEMY_STATE_ATTACK
        self.attack_timer = ENEMY_ATTACK_DURATION
        self.attack_cooldown_timer = ENEMY_ATTACK_COOLDOWN
        self.has_hit_this_attack = False

    def update_attack(self, dt):
        """End the attack after its short active window."""
        self.attack_timer -= dt

        if self.attack_timer <= 0:
            self.start_retreat()

    def start_retreat(self):
        """Pause pressure briefly after an attack instead of face-hugging."""
        self.state = ENEMY_STATE_IDLE
        self.attack_timer = 0
        self.retreat_timer = ENEMY_RETREAT_DURATION

    def is_attack_active(self):
        """Return True while the enemy hitbox should damage the player."""
        return self.state == ENEMY_STATE_ATTACK and self.attack_timer > 0

    def take_damage(self, amount, knockback_x=0):
        """Receive damage while keeping health from dropping below zero."""
        if self.defeated:
            return

        self.health = max(0, self.health - amount)
        self.hurt_flash_timer = ENEMY_HURT_FLASH_DURATION
        self.knockback_velocity_x = knockback_x
        self.state = ENEMY_STATE_HURT
        self.telegraph_timer = 0
        self.attack_timer = 0
        self.retreat_timer = 0
        self.has_hit_this_attack = False

        if self.health == 0:
            self.defeated = True
            self.state = ENEMY_STATE_DEFEATED

        return True

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

        attack_rect = create_enemy_attack_hitbox(self)

        if self.state == ENEMY_STATE_TELEGRAPH:
            draw_enemy_warning(surface, attack_rect, ENEMY_TELEGRAPH_COLOR, self.telegraph_timer)
        elif self.state == ENEMY_STATE_ATTACK:
            draw_enemy_attack_rectangle(surface, attack_rect, ENEMY_ATTACK_COLOR)
