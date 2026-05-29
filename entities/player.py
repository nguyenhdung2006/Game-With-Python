"""Player entity.

The Player class owns player input, movement state, jump physics, dash timers,
and drawing. Main.py only asks the player to update and draw.
"""

import pygame

from settings import (
    COMBO_RESET_TIME,
    DASH_COOLDOWN,
    DASH_DURATION,
    DASH_SPEED,
    DASH_TRAIL_LIFETIME,
    GRAVITY,
    GROUND_Y,
    JUMP_STRENGTH,
    LIGHT_ATTACK_COMBO,
    PLAYER_BLOCK_COLOR,
    PLAYER_BLOCK_DAMAGE_REDUCTION,
    PLAYER_BLOCK_FLASH_COLOR,
    PLAYER_BLOCK_FLASH_DURATION,
    PLAYER_BLOCK_HITSTOP,
    PLAYER_BLOCK_MOVE_MULTIPLIER,
    PLAYER_BLOCK_PUSHBACK,
    PLAYER_BLOCK_SHAKE_DURATION,
    PLAYER_BLOCK_SHAKE_STRENGTH,
    PLAYER_COLOR,
    PLAYER_DEFEATED_COLOR,
    PLAYER_DODGE_COLOR,
    PLAYER_DODGE_COOLDOWN,
    PLAYER_DODGE_DURATION,
    PLAYER_DODGE_INVULNERABILITY_DURATION,
    PLAYER_DODGE_RECOVERY_DURATION,
    PLAYER_DODGE_SHAKE_DURATION,
    PLAYER_DODGE_SHAKE_STRENGTH,
    PLAYER_DODGE_SPEED,
    PLAYER_HARD_LANDING_RECOVERY_DURATION,
    PLAYER_HARD_LANDING_SPEED,
    PLAYER_HEIGHT,
    PLAYER_ATTACK_BUFFER_DURATION,
    PLAYER_HURT_COLOR,
    PLAYER_HURT_DURATION,
    PLAYER_HURT_FLASH_DURATION,
    PLAYER_INVULNERABILITY_DURATION,
    PLAYER_INVULNERABLE_COLOR,
    PLAYER_LANDING_RECOVERY_DURATION,
    PLAYER_KNOCKBACK_FRICTION,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    WHITE,
    WIDTH,
)
from systems.combat import can_use_action, create_attack_hitbox, get_combo_attack_data, update_cooldown
from systems.effects import (
    choose_flash_color,
    create_afterimage,
    draw_block_guard,
    draw_attack_rectangle,
    draw_dodge_overlay,
    draw_rect_afterimages,
    update_timed_effects,
)
from systems.physics import apply_gravity, clamp_x_to_screen, resolve_ground_collision
from systems.physics import move_toward_zero


class Player:
    """A simple player object with movement, jumping, and dashing."""

    def __init__(self, x, y):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Float positions keep movement smooth when using delta time.
        self.x = float(x)
        self.y = float(y)

        # velocity_y is the player's current up/down speed.
        # Negative velocity moves the player up, positive velocity moves down.
        self.velocity_y = 0

        # gravity pulls the player down a little more every frame.
        self.gravity = GRAVITY

        # jump_strength is the upward force used when the player presses W.
        self.jump_strength = JUMP_STRENGTH

        # grounded tells us whether the player is standing on the floor.
        # The player can only jump when this is True.
        self.grounded = True

        # facing stores the direction the player is looking.
        # 1 means right, -1 means left.
        self.facing = 1

        # dash_speed is much faster than normal movement, but only for a short time.
        self.dash_speed = DASH_SPEED

        # dash_duration is how long the dash lasts in seconds.
        # dash_timer counts down from this value while a dash is active.
        self.dash_duration = DASH_DURATION
        self.dash_timer = 0

        # dash_cooldown is the waiting time before another dash can start.
        # dash_cooldown_timer counts down after each dash begins.
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_cooldown_timer = 0
        self.is_dashing = False

        # Each trail entry stores an old player rectangle and how long it should fade.
        self.dash_trail = []
        self.trail_lifetime = DASH_TRAIL_LIFETIME

        first_attack = LIGHT_ATTACK_COMBO[0]
        self.attack_damage = first_attack["damage"]
        self.attack_range = first_attack["range"]
        self.attack_height = first_attack["height"]
        self.attack_knockback = first_attack["knockback"]
        self.attack_movement_multiplier = first_attack["movement_multiplier"]
        self.attack_color = first_attack["color"]

        # attack_duration is how long one light attack stays active.
        # attack_timer counts down while the swing is happening.
        # attack_recovery_timer adds the committed end lag after the active swing.
        self.attack_duration = first_attack["duration"]
        self.attack_timer = 0
        self.attack_recovery = first_attack["recovery"]
        self.attack_cancel_window = first_attack["cancel_window"]
        self.attack_recovery_timer = 0

        # attack_cooldown_timer prevents instant repeated attacks.
        # Holding J will not keep starting attacks because this must reach 0 first.
        self.attack_cooldown = first_attack["cooldown"]
        self.attack_cooldown_timer = 0
        self.is_attacking = False

        # has_hit_this_attack makes sure one swing damages an enemy only once.
        self.has_hit_this_attack = False

        # combo_step tracks which part of the 3-hit combo is active or ready.
        # combo_timer is the short window where pressing J continues the chain.
        self.combo_step = 0
        self.combo_timer = 0
        self.combo_reset_time = COMBO_RESET_TIME
        self.attack_buffer_timer = 0
        self.buffered_attack = False

        # queued_next_attack stores one J press made during a current swing.
        # It lets quick taps chain smoothly without allowing held input to spam.
        self.queued_next_attack = False

        # Hurt timers make damage readable before sprites/animations exist.
        self.hurt_timer = 0
        self.hurt_flash_timer = 0

        # Invulnerability frames prevent rapid repeated damage from one enemy.
        self.invulnerability_timer = 0
        self.is_hurt = False
        self.defeated = False
        self.knockback_velocity_x = 0

        # Blocking reduces damage from attacks coming from the front.
        # This is guard, not parry: it lowers damage but does not counterattack.
        self.is_blocking = False
        self.block_direction = self.facing
        self.block_damage_reduction = PLAYER_BLOCK_DAMAGE_REDUCTION
        self.block_pushback = PLAYER_BLOCK_PUSHBACK
        self.block_stamina = 100
        self.block_flash_timer = 0
        self.block_flash_duration = PLAYER_BLOCK_FLASH_DURATION
        self.block_move_multiplier = PLAYER_BLOCK_MOVE_MULTIPLIER
        self.block_color = PLAYER_BLOCK_COLOR
        self.block_flash_color = PLAYER_BLOCK_FLASH_COLOR

        # Dodge is a short defensive burst with temporary i-frames.
        # Unlike dash, it is for avoiding attacks rather than covering distance.
        self.is_dodging = False
        self.dodge_timer = 0
        self.dodge_duration = PLAYER_DODGE_DURATION
        self.dodge_cooldown = PLAYER_DODGE_COOLDOWN
        self.dodge_cooldown_timer = 0
        self.dodge_invulnerability_timer = 0
        self.dodge_direction = self.facing
        self.dodge_speed = PLAYER_DODGE_SPEED
        self.dodge_color = PLAYER_DODGE_COLOR
        self.dodge_recovery_timer = 0

        # Landing recovery adds a tiny pause after touching ground.
        # It is stronger after faster falls so jumps do not feel weightless.
        self.landing_recovery_timer = 0

    def take_damage(self, amount):
        """Receive enemy attack damage and start hurt/i-frame feedback."""
        if not self.can_take_damage():
            return False

        self.health = max(0, self.health - amount)
        self.hurt_timer = PLAYER_HURT_DURATION
        self.hurt_flash_timer = PLAYER_HURT_FLASH_DURATION
        self.invulnerability_timer = PLAYER_INVULNERABILITY_DURATION
        self.is_hurt = True
        self.is_attacking = False
        self.is_dashing = False

        if self.health == 0:
            self.defeated = True

        return True

    def can_take_damage(self):
        """Return True only when i-frames are not protecting the player."""
        return (
            not self.defeated
            and self.invulnerability_timer <= 0
            and self.dodge_invulnerability_timer <= 0
        )

    def update(self, keys, dt):
        """Run all per-frame player behavior."""
        self.update_hurt_timers(dt)

        if self.defeated:
            self.apply_physics(dt)
            return

        self.update_dash_cooldown(dt)
        self.update_dodge_timers(dt)
        self.update_attack_timers(dt)
        self.update_block_state(keys)
        self.handle_input(keys, dt)
        self.update_knockback(dt)
        self.apply_physics(dt)
        self.update_dash_trail(dt)

    def update_hurt_timers(self, dt):
        """Count down hurt, flash, and invulnerability timers."""
        if self.hurt_timer > 0:
            self.hurt_timer = max(0, self.hurt_timer - dt)

            if self.hurt_timer == 0:
                self.is_hurt = False

        if self.hurt_flash_timer > 0:
            self.hurt_flash_timer = max(0, self.hurt_flash_timer - dt)

        if self.invulnerability_timer > 0:
            self.invulnerability_timer = max(0, self.invulnerability_timer - dt)

        if self.dodge_invulnerability_timer > 0:
            self.dodge_invulnerability_timer = max(0, self.dodge_invulnerability_timer - dt)

        if self.block_flash_timer > 0:
            self.block_flash_timer = max(0, self.block_flash_timer - dt)

        if self.attack_buffer_timer > 0:
            self.attack_buffer_timer = max(0, self.attack_buffer_timer - dt)

        if self.landing_recovery_timer > 0:
            self.landing_recovery_timer = max(0, self.landing_recovery_timer - dt)

    def update_block_state(self, keys):
        """Hold K to guard without turning this into a full parry system."""
        can_block = (
            not self.defeated
            and not self.is_hurt
            and not self.is_dashing
            and not self.is_dodging
            and (
                not self.is_attacking
                or self.can_cancel_attack_to_block()
                or self.attack_recovery_timer > 0
            )
        )

        if keys[pygame.K_k] and can_block:
            if not self.is_blocking:
                self.block_direction = self.facing
            self.is_blocking = True
            self.facing = self.block_direction
        else:
            self.is_blocking = False

    def update_knockback(self, dt):
        """Move the player while hurt knockback is active."""
        if self.knockback_velocity_x == 0:
            return

        self.x += self.knockback_velocity_x * dt
        self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
        self.knockback_velocity_x = move_toward_zero(
            self.knockback_velocity_x,
            PLAYER_KNOCKBACK_FRICTION * dt,
        )
        self.rect.x = round(self.x)

    def handle_input(self, keys, dt):
        """Move left/right normally, or move by dash velocity during a dash."""
        if self.is_dodging:
            self.x += self.dodge_direction * self.dodge_speed * dt
            self.add_dash_trail()
        elif self.is_dashing:
            self.x += self.facing * self.dash_speed * dt
            self.dash_timer -= dt
            self.add_dash_trail()

            if self.dash_timer <= 0:
                self.is_dashing = False
        elif self.is_blocking:
            if keys[pygame.K_a]:
                self.x -= self.get_current_move_speed() * dt
            if keys[pygame.K_d]:
                self.x += self.get_current_move_speed() * dt
            self.facing = self.block_direction
        elif keys[pygame.K_a]:
            self.x -= self.get_current_move_speed() * dt
            self.facing = -1
        elif keys[pygame.K_d]:
            self.x += self.get_current_move_speed() * dt
            self.facing = 1

        self.x = clamp_x_to_screen(self.x, self.width, WIDTH)
        self.rect.x = round(self.x)

    def get_current_move_speed(self):
        """Reduce movement during attacks so combo hits feel committed."""
        if self.is_hurt:
            return self.speed * 0.25

        if self.is_dodging:
            return 0

        if self.is_blocking:
            return self.speed * self.block_move_multiplier

        if self.is_attacking:
            return self.speed * self.attack_movement_multiplier

        return self.speed

    def can_cancel_attack_to_block(self):
        """Allow guarding near the end of an attack instead of only after it ends."""
        return self.is_attacking and self.attack_timer <= self.attack_cancel_window

    def is_in_action_recovery(self):
        """Recovery timers stop instant action spam between states."""
        return (
            self.attack_recovery_timer > 0
            or self.dodge_recovery_timer > 0
            or self.landing_recovery_timer > 0
        )

    def jump(self):
        """Start a jump only if the player is standing on the ground."""
        if self.defeated or self.is_hurt:
            return

        if self.grounded:
            self.velocity_y = -self.jump_strength
            self.grounded = False

    def start_dash(self):
        """Start a short dash if the cooldown has finished."""
        if self.defeated or self.is_hurt:
            return

        # Dashing during attacks makes combat hard to read, so attacks lock it out.
        if self.is_attacking or self.is_blocking or self.is_dodging or self.is_in_action_recovery():
            return

        if not self.is_dashing and self.dash_cooldown_timer <= 0:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            self.add_dash_trail()

    def start_dodge(self):
        """Start a short evade burst with temporary invulnerability."""
        if self.defeated or self.is_hurt or self.is_attacking or self.is_blocking:
            return None

        if self.is_dodging or self.dodge_cooldown_timer > 0 or self.is_in_action_recovery():
            return None

        self.is_dodging = True
        self.is_dashing = False
        self.dodge_direction = self.facing
        self.dodge_timer = self.dodge_duration
        self.dodge_cooldown_timer = self.dodge_cooldown
        self.dodge_invulnerability_timer = PLAYER_DODGE_INVULNERABILITY_DURATION
        self.add_dash_trail()

        return {
            "hitstop": 0,
            "shake_duration": PLAYER_DODGE_SHAKE_DURATION,
            "shake_strength": PLAYER_DODGE_SHAKE_STRENGTH,
        }

    def update_dash_cooldown(self, dt):
        """Count down until the player is allowed to dash again."""
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer = max(0, self.dash_cooldown_timer - dt)

    def update_dodge_timers(self, dt):
        """Count dodge duration and cooldown with delta time."""
        ended_dodge_this_frame = False

        if self.is_dodging:
            self.dodge_timer -= dt

            if self.dodge_timer <= 0:
                self.is_dodging = False
                self.dodge_timer = 0
                self.dodge_recovery_timer = PLAYER_DODGE_RECOVERY_DURATION
                ended_dodge_this_frame = True

        if self.dodge_cooldown_timer > 0:
            self.dodge_cooldown_timer = max(0, self.dodge_cooldown_timer - dt)

        if self.dodge_recovery_timer > 0 and not ended_dodge_this_frame:
            self.dodge_recovery_timer = max(0, self.dodge_recovery_timer - dt)

    def start_light_attack(self):
        """Start or queue the next hit in the 3-hit light combo."""
        if self.defeated or self.is_hurt or self.is_blocking or self.is_dodging:
            return

        if self.is_in_action_recovery():
            self.buffered_attack = True
            self.attack_buffer_timer = PLAYER_ATTACK_BUFFER_DURATION
            return

        if self.is_attacking:
            if self.combo_step < len(LIGHT_ATTACK_COMBO) and self.combo_timer > 0:
                self.queued_next_attack = True
            return

        if not can_use_action(self.attack_cooldown_timer):
            return

        if self.combo_timer <= 0 or self.combo_step >= len(LIGHT_ATTACK_COMBO):
            next_combo_step = 1
        else:
            next_combo_step = self.combo_step + 1

        self.begin_combo_attack(next_combo_step)

    def begin_combo_attack(self, combo_step):
        """Apply the timing, damage, and hitbox data for one combo hit."""
        attack_data = get_combo_attack_data(combo_step)

        self.combo_step = combo_step
        self.combo_timer = self.combo_reset_time

        self.attack_damage = attack_data["damage"]
        self.attack_range = attack_data["range"]
        self.attack_height = attack_data["height"]
        self.attack_knockback = attack_data["knockback"]
        self.attack_movement_multiplier = attack_data["movement_multiplier"]
        self.attack_color = attack_data["color"]
        self.attack_duration = attack_data["duration"]
        self.attack_cooldown = attack_data["cooldown"]
        self.attack_recovery = attack_data["recovery"]
        self.attack_cancel_window = attack_data["cancel_window"]

        self.is_attacking = True
        self.attack_timer = self.attack_duration
        self.attack_cooldown_timer = self.attack_cooldown
        self.has_hit_this_attack = False

    def update_attack_timers(self, dt):
        """Update attack duration, cooldown, and combo reset using delta time."""
        ended_attack_this_frame = False

        if self.combo_timer > 0:
            self.combo_timer = max(0, self.combo_timer - dt)

            if self.combo_timer == 0 and not self.is_attacking:
                self.reset_combo()

        if self.is_attacking:
            self.attack_timer -= dt

            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_timer = 0
                self.attack_recovery_timer = self.attack_recovery
                ended_attack_this_frame = True

        if self.combo_timer == 0 and not self.is_attacking:
            self.reset_combo()

        self.attack_cooldown_timer = update_cooldown(self.attack_cooldown_timer, dt)
        if self.attack_recovery_timer > 0 and not ended_attack_this_frame:
            self.attack_recovery_timer = max(0, self.attack_recovery_timer - dt)

        if (
            self.queued_next_attack
            and not self.is_attacking
            and self.combo_timer > 0
            and can_use_action(self.attack_cooldown_timer)
            and self.attack_recovery_timer <= 0
        ):
            self.queued_next_attack = False
            self.start_light_attack()

        if (
            self.buffered_attack
            and not self.is_attacking
            and not self.is_in_action_recovery()
            and can_use_action(self.attack_cooldown_timer)
        ):
            self.buffered_attack = False
            self.start_light_attack()

        if self.buffered_attack and self.attack_buffer_timer == 0 and not self.is_attacking:
            self.buffered_attack = False

    def reset_combo(self):
        """Return the combo chain to hit 1 after the timing window expires."""
        self.combo_step = 0
        self.combo_timer = 0
        self.queued_next_attack = False

    def start_landing_recovery(self, fall_speed):
        """Add a tiny grounded pause after landing, stronger on fast falls."""
        if fall_speed >= PLAYER_HARD_LANDING_SPEED:
            self.landing_recovery_timer = PLAYER_HARD_LANDING_RECOVERY_DURATION
        else:
            self.landing_recovery_timer = PLAYER_LANDING_RECOVERY_DURATION

    def get_attack_hitbox(self):
        """Return the active sword hitbox, or None when not attacking."""
        if not self.is_attacking:
            return None

        return create_attack_hitbox(self)

    def can_block_attack_from(self, attacker_direction):
        """Block only works when the player is guarding toward the attacker."""
        return self.is_blocking and self.block_direction == -attacker_direction

    def block_hit(self, amount, attacker_direction):
        """Absorb part of an enemy hit without entering full hurt stun."""
        if self.defeated:
            return None

        blocked_damage = max(1, round(amount * self.block_damage_reduction))
        self.health = max(0, self.health - blocked_damage)
        self.block_flash_timer = self.block_flash_duration
        self.knockback_velocity_x = attacker_direction * self.block_pushback

        if self.health == 0:
            self.defeated = True
            self.is_blocking = False

        return {
            "hitstop": PLAYER_BLOCK_HITSTOP,
            "shake_duration": PLAYER_BLOCK_SHAKE_DURATION,
            "shake_strength": PLAYER_BLOCK_SHAKE_STRENGTH,
        }

    def apply_physics(self, dt):
        """Apply gravity and stop the player exactly on the ground."""
        was_grounded = self.grounded
        landing_speed = self.velocity_y
        self.y, self.velocity_y = apply_gravity(self.y, self.velocity_y, self.gravity, dt)
        self.y, self.velocity_y, self.grounded = resolve_ground_collision(
            self.y,
            self.height,
            self.velocity_y,
            GROUND_Y,
        )

        if not was_grounded and self.grounded:
            self.start_landing_recovery(landing_speed)

        self.rect.y = round(self.y)

    def add_dash_trail(self):
        """Save a copy of the current rectangle for the dash afterimage effect."""
        self.dash_trail.append(create_afterimage(self.rect, self.trail_lifetime))

    def update_dash_trail(self, dt):
        """Fade old dash afterimages over time."""
        self.dash_trail = update_timed_effects(self.dash_trail, dt)

    def draw(self, surface):
        """Draw the dash trail and placeholder rectangle player."""
        draw_rect_afterimages(
            surface,
            self.dash_trail,
            (self.width, self.height),
            self.trail_lifetime,
            PLAYER_COLOR,
        )
        draw_attack_rectangle(surface, self.get_attack_hitbox(), self.attack_color, self.combo_step)
        draw_block_guard(
            surface,
            self.rect,
            self.block_direction,
            self.is_blocking,
            self.block_flash_timer,
            self.block_color,
            self.block_flash_color,
        )
        if self.is_dodging or self.dodge_invulnerability_timer > 0:
            draw_dodge_overlay(surface, self.rect, self.dodge_color)

        color = PLAYER_COLOR
        if self.defeated:
            color = PLAYER_DEFEATED_COLOR
        elif self.invulnerability_timer > 0:
            # Blinking during i-frames makes temporary safety visible to the player.
            blink_on = int(self.invulnerability_timer * 20) % 2 == 0
            color = PLAYER_INVULNERABLE_COLOR if blink_on else PLAYER_COLOR

        color = choose_flash_color(color, PLAYER_HURT_COLOR, self.hurt_flash_timer)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)
