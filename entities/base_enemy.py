"""Shared enemy behavior.

BaseEnemy holds the reusable AI state machine, hurt logic, stagger logic,
movement, and drawing. Enemy archetype subclasses only provide stats and
visual identity so the project can scale to more enemy types cleanly.
"""

import pygame

from settings import (
    ENEMY_STATE_ATTACK,
    ENEMY_STATE_CHASE,
    ENEMY_STATE_DEFEATED,
    ENEMY_STATE_HURT,
    ENEMY_STATE_IDLE,
    ENEMY_STATE_STAGGER,
    ENEMY_STATE_TELEGRAPH,
    GROUND_Y,
    WHITE,
    WIDTH,
)
from systems.combat import create_enemy_attack_hitbox
from systems.effects import choose_flash_color, draw_enemy_attack_rectangle, draw_enemy_warning
from systems.physics import clamp_x_to_screen, move_toward_zero


class BaseEnemy:
    """Reusable enemy base class for melee archetypes."""

    def __init__(self, x, y, config):
        self.config = config
        self.label = config["label"]
        self.width = config["width"]
        self.height = config["height"]
        self.max_health = config["max_health"]
        self.health = config["max_health"]

        if y is None:
            y = GROUND_Y - self.height

        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x = float(x)

        # Archetype values live on the instance so combat helpers can work
        # with any enemy type through the same interface.
        self.hurt_flash_duration = config["hurt_flash_duration"]
        self.knockback_friction = config["knockback_friction"]
        self.chase_speed = config["chase_speed"]
        self.attack_start_distance = config["attack_start_distance"]
        self.telegraph_duration = config["telegraph_duration"]
        self.attack_duration = config["attack_duration"]
        self.attack_cooldown = config["attack_cooldown"]
        self.attack_damage = config["attack_damage"]
        self.attack_range = config["attack_range"]
        self.attack_height = config["attack_height"]
        self.attack_knockback = config["attack_knockback"]
        self.retreat_duration = config["retreat_duration"]
        self.retreat_speed = config["retreat_speed"]
        self.attack_hitstop = config["attack_hitstop"]
        self.attack_shake_duration = config["attack_shake_duration"]
        self.attack_shake_strength = config["attack_shake_strength"]
        self.recovery_duration = config["recovery_duration"]
        self.stagger_duration = config["stagger_duration"]

        self.body_color = config["body_color"]
        self.hurt_color = config["hurt_color"]
        self.defeated_color = config["defeated_color"]
        self.telegraph_color = config["telegraph_color"]
        self.attack_color = config["attack_color"]
        self.telegraph_pulse_speed = config["telegraph_pulse_speed"]
        self.recoil_outline_color = config["recoil_outline_color"]

        self.hurt_flash_timer = 0
        self.knockback_velocity_x = 0
        self.defeated = False
        self.facing = -1

        self.state = ENEMY_STATE_IDLE
        self.telegraph_timer = 0
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.has_hit_this_attack = False
        self.retreat_timer = 0
        self.recovery_timer = 0
        self.stagger_timer = 0

    def update(self, player, dt, allow_attack=True):
        """Run the shared melee enemy state machine.

        allow_attack lets encounter logic throttle how many enemies try to
        start attacks at once. That keeps multi-enemy fights readable.
        """
        self.update_timers(dt)

        if self.defeated:
            self.state = ENEMY_STATE_DEFEATED
            self.knockback_velocity_x = 0
            return

        if self.hurt_flash_timer > 0:
            self.state = ENEMY_STATE_HURT
            self.update_knockback(dt)
            return

        if self.stagger_timer > 0:
            # Stagger is short, readable vulnerability. Archetypes can tune the
            # duration to feel more or less punishable.
            self.state = ENEMY_STATE_STAGGER
            self.update_knockback(dt)
            return

        self.face_player(player)

        if self.retreat_timer > 0:
            self.update_retreat(dt)
        elif self.recovery_timer > 0:
            self.update_recovery(dt)
        elif self.state == ENEMY_STATE_TELEGRAPH:
            self.update_telegraph(dt)
        elif self.state == ENEMY_STATE_ATTACK:
            self.update_attack(dt)
        else:
            self.update_idle_or_chase(player, dt, allow_attack)

        self.update_knockback(dt)

    def update_timers(self, dt):
        """Count down the shared state timers."""
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer = max(0, self.attack_cooldown_timer - dt)

        if self.hurt_flash_timer > 0:
            self.hurt_flash_timer = max(0, self.hurt_flash_timer - dt)

        if self.retreat_timer > 0:
            self.retreat_timer = max(0, self.retreat_timer - dt)

        if self.recovery_timer > 0:
            self.recovery_timer = max(0, self.recovery_timer - dt)

        if self.stagger_timer > 0:
            self.stagger_timer = max(0, self.stagger_timer - dt)

    def update_knockback(self, dt):
        """Move the enemy while knockback is still active."""
        if self.knockback_velocity_x == 0:
            return

        self.x += self.knockback_velocity_x * dt
        self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
        self.knockback_velocity_x = move_toward_zero(
            self.knockback_velocity_x,
            self.knockback_friction * dt,
        )
        self.rect.x = round(self.x)

    def face_player(self, player):
        """Turn toward the player before chasing or attacking."""
        if player.rect.centerx >= self.rect.centerx:
            self.facing = 1
        else:
            self.facing = -1

    def update_idle_or_chase(self, player, dt, allow_attack=True):
        """Chase while far away, or telegraph when close enough to attack."""
        distance_to_player = abs(player.rect.centerx - self.rect.centerx)

        if distance_to_player > self.attack_start_distance:
            self.state = ENEMY_STATE_CHASE
            self.x += self.facing * self.chase_speed * dt
            self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
            self.rect.x = round(self.x)
            return

        self.state = ENEMY_STATE_IDLE

        if self.attack_cooldown_timer <= 0 and allow_attack:
            self.start_telegraph()

    def update_retreat(self, dt):
        """Step away after attacking so enemies do not just face-hug forever."""
        self.state = ENEMY_STATE_IDLE
        self.x -= self.facing * self.retreat_speed * dt
        self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
        self.rect.x = round(self.x)

    def update_recovery(self, dt):
        """Pause briefly after an attack before restarting pressure."""
        self.state = ENEMY_STATE_IDLE

    def start_telegraph(self):
        """Begin the readable warning before the enemy strike."""
        self.state = ENEMY_STATE_TELEGRAPH
        self.telegraph_timer = self.telegraph_duration

    def update_telegraph(self, dt):
        """Wait through the telegraph, then start the attack."""
        self.telegraph_timer -= dt

        if self.telegraph_timer <= 0:
            self.start_attack()

    def start_attack(self):
        """Open the active attack window."""
        self.state = ENEMY_STATE_ATTACK
        self.attack_timer = self.attack_duration
        self.attack_cooldown_timer = self.attack_cooldown
        self.has_hit_this_attack = False

    def update_attack(self, dt):
        """Close the active attack window and move to retreat."""
        self.attack_timer -= dt

        if self.attack_timer <= 0:
            self.start_retreat()

    def start_retreat(self):
        """Create spacing after an attack instead of constant contact."""
        self.state = ENEMY_STATE_IDLE
        self.attack_timer = 0
        self.retreat_timer = self.retreat_duration
        self.recovery_timer = self.recovery_duration

    def start_stagger(self, duration=None):
        """Interrupt the current action and leave the enemy briefly vulnerable."""
        if self.defeated:
            return

        if duration is None:
            duration = self.stagger_duration

        self.state = ENEMY_STATE_STAGGER
        self.telegraph_timer = 0
        self.attack_timer = 0
        self.retreat_timer = 0
        self.recovery_timer = 0
        self.has_hit_this_attack = True
        self.stagger_timer = duration

    def is_attack_active(self):
        """Return True while the enemy attack hitbox should be dangerous."""
        return self.state == ENEMY_STATE_ATTACK and self.attack_timer > 0

    def take_damage(self, amount, knockback_x=0):
        """Receive damage while keeping health above zero."""
        if self.defeated:
            return

        self.health = max(0, self.health - amount)
        self.hurt_flash_timer = self.hurt_flash_duration
        self.knockback_velocity_x = knockback_x
        self.state = ENEMY_STATE_HURT
        self.telegraph_timer = 0
        self.attack_timer = 0
        self.retreat_timer = 0
        self.recovery_timer = 0
        self.stagger_timer = 0
        self.has_hit_this_attack = False

        if self.health == 0:
            self.defeated = True
            self.state = ENEMY_STATE_DEFEATED

        return True

    def draw(self, surface):
        """Draw the enemy and its current telegraph or attack effect."""
        if self.defeated:
            color = self.defeated_color
        elif self.state == ENEMY_STATE_STAGGER:
            color = (255, 245, 185)
        else:
            color = choose_flash_color(self.body_color, self.hurt_color, self.hurt_flash_timer)

        if self.hurt_flash_timer > 0 and not self.defeated:
            recoil_rect = self.rect.copy()
            recoil_rect.x -= 6 if self.knockback_velocity_x > 0 else -6
            pygame.draw.rect(surface, self.recoil_outline_color, recoil_rect, 3)

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        if self.state == ENEMY_STATE_STAGGER:
            spark_center = (self.rect.centerx, self.rect.top - 12)
            pygame.draw.circle(surface, WHITE, spark_center, 10, 2)
            pygame.draw.line(
                surface,
                WHITE,
                (spark_center[0] - 14, spark_center[1]),
                (spark_center[0] + 14, spark_center[1]),
                2,
            )
            pygame.draw.line(
                surface,
                WHITE,
                (spark_center[0], spark_center[1] - 14),
                (spark_center[0], spark_center[1] + 14),
                2,
            )

        attack_rect = create_enemy_attack_hitbox(self)

        if self.state == ENEMY_STATE_TELEGRAPH:
            draw_enemy_warning(
                surface,
                attack_rect,
                self.telegraph_color,
                self.telegraph_timer,
                self.telegraph_pulse_speed,
            )
        elif self.state == ENEMY_STATE_ATTACK:
            draw_enemy_attack_rectangle(surface, attack_rect, self.attack_color)
