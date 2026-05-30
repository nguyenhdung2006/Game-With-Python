"""Player movement, dodge, dash, and physics helpers."""

import pygame

from settings import (
    GROUND_Y,
    PLAYER_DODGE_INVULNERABILITY_DURATION,
    PLAYER_DODGE_RECOVERY_DURATION,
    PLAYER_DODGE_SHAKE_DURATION,
    PLAYER_DODGE_SHAKE_STRENGTH,
    PLAYER_HARD_LANDING_RECOVERY_DURATION,
    PLAYER_HARD_LANDING_SPEED,
    PLAYER_LANDING_RECOVERY_DURATION,
    WIDTH,
)
from systems.effects import create_afterimage, update_timed_effects
from systems.physics import apply_gravity, clamp_x_to_screen, move_toward_zero, resolve_ground_collision


def update_knockback(player, dt):
    """Move the player while hurt knockback is active."""
    if player.knockback_velocity_x == 0:
        return

    player.x += player.knockback_velocity_x * dt
    player.x = clamp_x_to_screen(player.x, player.width, WIDTH)
    player.knockback_velocity_x = move_toward_zero(
        player.knockback_velocity_x,
        player.knockback_friction * dt,
    )
    player.rect.x = round(player.x)


def handle_input(player, keys, dt):
    """Move left/right normally, or move by dash velocity during a dash."""
    player.last_move_direction = 0

    if player.is_dodging:
        player.x += player.dodge_direction * player.dodge_speed * dt
        add_dash_trail(player)
    elif player.is_dashing:
        player.x += player.facing * player.dash_speed * dt
        player.dash_timer -= dt
        add_dash_trail(player)

        if player.dash_timer <= 0:
            player.is_dashing = False
    elif player.is_blocking or player.is_parrying:
        if keys[pygame.K_a]:
            player.x -= get_current_move_speed(player) * dt
            player.last_move_direction = -1
        if keys[pygame.K_d]:
            player.x += get_current_move_speed(player) * dt
            player.last_move_direction = 1
        player.facing = player.block_direction
    elif keys[pygame.K_a]:
        player.x -= get_current_move_speed(player) * dt
        player.facing = -1
        player.last_move_direction = -1
    elif keys[pygame.K_d]:
        player.x += get_current_move_speed(player) * dt
        player.facing = 1
        player.last_move_direction = 1

    player.x = clamp_x_to_screen(player.x, player.width, WIDTH)
    player.rect.x = round(player.x)


def get_current_move_speed(player):
    """Reduce movement during attacks so combo hits feel committed."""
    if player.is_hurt:
        return player.speed * 0.25

    if player.is_dodging:
        return 0

    if player.is_blocking or player.is_parrying:
        return player.speed * player.block_move_multiplier

    if player.is_attacking:
        return player.speed * player.attack_movement_multiplier

    return player.speed


def jump(player):
    """Start a jump only if the player is standing on the ground."""
    if player.defeated or player.is_hurt:
        return

    if player.grounded:
        player.velocity_y = -player.jump_strength
        player.grounded = False


def start_dash(player):
    """Start a short dash if the cooldown has finished."""
    if player.defeated or player.is_hurt:
        return

    # Dashing during attacks makes combat hard to read, so attacks lock it out.
    if (
        player.is_attacking
        or player.is_blocking
        or player.is_parrying
        or player.is_dodging
        or player.is_in_action_recovery()
    ):
        return

    if not player.is_dashing and player.dash_cooldown_timer <= 0:
        player.is_dashing = True
        player.dash_timer = player.dash_duration
        player.dash_cooldown_timer = player.dash_cooldown
        add_dash_trail(player)


def start_dodge(player):
    """Start a short evade burst with temporary invulnerability."""
    if player.defeated or player.is_hurt or player.is_attacking or player.is_blocking or player.is_parrying:
        return None

    if player.is_dodging or player.dodge_cooldown_timer > 0 or player.is_in_action_recovery():
        return None

    player.is_dodging = True
    player.is_dashing = False
    player.dodge_direction = player.facing
    player.dodge_timer = player.dodge_duration
    player.dodge_cooldown_timer = player.dodge_cooldown
    player.dodge_invulnerability_timer = PLAYER_DODGE_INVULNERABILITY_DURATION
    add_dash_trail(player)

    return {
        "hitstop": 0,
        "shake_duration": PLAYER_DODGE_SHAKE_DURATION,
        "shake_strength": PLAYER_DODGE_SHAKE_STRENGTH,
    }


def update_dash_cooldown(player, dt):
    """Count down until the player is allowed to dash again."""
    if player.dash_cooldown_timer > 0:
        player.dash_cooldown_timer = max(0, player.dash_cooldown_timer - dt)


def update_dodge_timers(player, dt):
    """Count dodge duration and cooldown with delta time."""
    ended_dodge_this_frame = False

    if player.is_dodging:
        player.dodge_timer -= dt

        if player.dodge_timer <= 0:
            player.is_dodging = False
            player.dodge_timer = 0
            player.dodge_recovery_timer = PLAYER_DODGE_RECOVERY_DURATION
            player.begin_dodge_recovery_feedback()
            ended_dodge_this_frame = True

    if player.dodge_cooldown_timer > 0:
        player.dodge_cooldown_timer = max(0, player.dodge_cooldown_timer - dt)

    if player.dodge_recovery_timer > 0 and not ended_dodge_this_frame:
        player.dodge_recovery_timer = max(0, player.dodge_recovery_timer - dt)


def start_landing_recovery(player, fall_speed):
    """Add a tiny grounded pause after landing, stronger on fast falls."""
    if fall_speed >= PLAYER_HARD_LANDING_SPEED:
        player.landing_recovery_timer = PLAYER_HARD_LANDING_RECOVERY_DURATION
    else:
        player.landing_recovery_timer = PLAYER_LANDING_RECOVERY_DURATION
    player.begin_landing_feedback(fall_speed)


def apply_physics(player, dt):
    """Apply gravity and stop the player exactly on the ground."""
    was_grounded = player.grounded
    landing_speed = player.velocity_y
    player.y, player.velocity_y = apply_gravity(player.y, player.velocity_y, player.gravity, dt)
    player.y, player.velocity_y, player.grounded = resolve_ground_collision(
        player.y,
        player.height,
        player.velocity_y,
        GROUND_Y,
    )

    if not was_grounded and player.grounded:
        start_landing_recovery(player, landing_speed)

    player.rect.y = round(player.y)


def add_dash_trail(player):
    """Save a copy of the current rectangle for the dash afterimage effect."""
    player.dash_trail.append(create_afterimage(player.rect, player.trail_lifetime))


def update_dash_trail(player, dt):
    """Fade old dash afterimages over time."""
    player.dash_trail = update_timed_effects(player.dash_trail, dt)
