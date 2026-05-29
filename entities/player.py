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
    PLAYER_COLOR,
    PLAYER_HEIGHT,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    WHITE,
    WIDTH,
)
from systems.combat import can_use_action, create_attack_hitbox, get_combo_attack_data, update_cooldown
from systems.effects import (
    create_afterimage,
    draw_attack_rectangle,
    draw_rect_afterimages,
    update_timed_effects,
)
from systems.physics import apply_gravity, clamp_x_to_screen, resolve_ground_collision


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
        self.attack_duration = first_attack["duration"]
        self.attack_timer = 0

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

        # queued_next_attack stores one J press made during a current swing.
        # It lets quick taps chain smoothly without allowing held input to spam.
        self.queued_next_attack = False

    def update(self, keys, dt):
        """Run all per-frame player behavior."""
        self.update_dash_cooldown(dt)
        self.update_attack_timers(dt)
        self.handle_input(keys, dt)
        self.apply_physics(dt)
        self.update_dash_trail(dt)

    def handle_input(self, keys, dt):
        """Move left/right normally, or move by dash velocity during a dash."""
        if self.is_dashing:
            self.x += self.facing * self.dash_speed * dt
            self.dash_timer -= dt
            self.add_dash_trail()

            if self.dash_timer <= 0:
                self.is_dashing = False
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
        if self.is_attacking:
            return self.speed * self.attack_movement_multiplier

        return self.speed

    def jump(self):
        """Start a jump only if the player is standing on the ground."""
        if self.grounded:
            self.velocity_y = -self.jump_strength
            self.grounded = False

    def start_dash(self):
        """Start a short dash if the cooldown has finished."""
        # Dashing during attacks makes combat hard to read, so attacks lock it out.
        if self.is_attacking:
            return

        if not self.is_dashing and self.dash_cooldown_timer <= 0:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            self.add_dash_trail()

    def update_dash_cooldown(self, dt):
        """Count down until the player is allowed to dash again."""
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer = max(0, self.dash_cooldown_timer - dt)

    def start_light_attack(self):
        """Start or queue the next hit in the 3-hit light combo."""
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

        self.is_attacking = True
        self.attack_timer = self.attack_duration
        self.attack_cooldown_timer = self.attack_cooldown
        self.has_hit_this_attack = False

    def update_attack_timers(self, dt):
        """Update attack duration, cooldown, and combo reset using delta time."""
        if self.combo_timer > 0:
            self.combo_timer = max(0, self.combo_timer - dt)

            if self.combo_timer == 0 and not self.is_attacking:
                self.reset_combo()

        if self.is_attacking:
            self.attack_timer -= dt

            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_timer = 0

        if self.combo_timer == 0 and not self.is_attacking:
            self.reset_combo()

        self.attack_cooldown_timer = update_cooldown(self.attack_cooldown_timer, dt)

        if (
            self.queued_next_attack
            and not self.is_attacking
            and self.combo_timer > 0
            and can_use_action(self.attack_cooldown_timer)
        ):
            self.queued_next_attack = False
            self.start_light_attack()

    def reset_combo(self):
        """Return the combo chain to hit 1 after the timing window expires."""
        self.combo_step = 0
        self.combo_timer = 0
        self.queued_next_attack = False

    def get_attack_hitbox(self):
        """Return the active sword hitbox, or None when not attacking."""
        if not self.is_attacking:
            return None

        return create_attack_hitbox(self)

    def apply_physics(self, dt):
        """Apply gravity and stop the player exactly on the ground."""
        self.y, self.velocity_y = apply_gravity(self.y, self.velocity_y, self.gravity, dt)
        self.y, self.velocity_y, self.grounded = resolve_ground_collision(
            self.y,
            self.height,
            self.velocity_y,
            GROUND_Y,
        )
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
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)
