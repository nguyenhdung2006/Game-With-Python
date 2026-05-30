"""Player hurt, block, and parry helpers."""

import pygame

from settings import (
    PLAYER_BLOCK_HITSTOP,
    PLAYER_BLOCK_SHAKE_DURATION,
    PLAYER_BLOCK_SHAKE_STRENGTH,
    PLAYER_DODGE_INVULNERABILITY_DURATION,
    PLAYER_HURT_DURATION,
    PLAYER_HURT_FLASH_DURATION,
    PLAYER_INVULNERABILITY_DURATION,
    PLAYER_PARRY_COOLDOWN,
    PLAYER_PARRY_HITSTOP,
    PLAYER_PARRY_SHAKE_DURATION,
    PLAYER_PARRY_SHAKE_STRENGTH,
    PLAYER_PARRY_SUCCESS_DURATION,
    PLAYER_PARRY_WINDOW_DURATION,
    PLAYER_COUNTER_WINDOW_DURATION,
)


def take_damage(player, amount):
    """Receive enemy attack damage and start hurt/i-frame feedback."""
    if not can_take_damage(player):
        return False

    player.health = max(0, player.health - amount)
    player.hurt_timer = PLAYER_HURT_DURATION
    player.hurt_flash_timer = PLAYER_HURT_FLASH_DURATION
    player.invulnerability_timer = PLAYER_INVULNERABILITY_DURATION
    player.is_hurt = True
    player.is_attacking = False
    player.is_counter_attacking = False
    player.is_dashing = False
    player.can_counter = False
    player.counter_window_timer = 0

    if player.health == 0:
        player.defeated = True

    return True


def can_take_damage(player):
    """Return True only when i-frames are not protecting the player."""
    return (
        not player.defeated
        and player.invulnerability_timer <= 0
        and player.dodge_invulnerability_timer <= 0
    )


def update_hurt_timers(player, dt):
    """Count down hurt, flash, invulnerability, block, parry, and counter timers."""
    if player.hurt_timer > 0:
        player.hurt_timer = max(0, player.hurt_timer - dt)
        if player.hurt_timer == 0:
            player.is_hurt = False

    if player.hurt_flash_timer > 0:
        player.hurt_flash_timer = max(0, player.hurt_flash_timer - dt)

    if player.invulnerability_timer > 0:
        player.invulnerability_timer = max(0, player.invulnerability_timer - dt)

    if player.dodge_invulnerability_timer > 0:
        player.dodge_invulnerability_timer = max(0, player.dodge_invulnerability_timer - dt)

    if player.parry_window_timer > 0:
        player.parry_window_timer = max(0, player.parry_window_timer - dt)
        if player.parry_window_timer == 0:
            player.is_parrying = False

    if player.parry_cooldown_timer > 0:
        player.parry_cooldown_timer = max(0, player.parry_cooldown_timer - dt)

    if player.successful_parry_timer > 0:
        player.successful_parry_timer = max(0, player.successful_parry_timer - dt)

    if player.counter_window_timer > 0:
        player.counter_window_timer = max(0, player.counter_window_timer - dt)
        if player.counter_window_timer == 0:
            player.can_counter = False

    if player.block_flash_timer > 0:
        player.block_flash_timer = max(0, player.block_flash_timer - dt)

    if player.attack_buffer_timer > 0:
        player.attack_buffer_timer = max(0, player.attack_buffer_timer - dt)

    if player.landing_recovery_timer > 0:
        player.landing_recovery_timer = max(0, player.landing_recovery_timer - dt)


def update_block_state(player, keys):
    """Use one guard key for both parry timing and normal block holding."""
    can_block = (
        not player.defeated
        and not player.is_hurt
        and not player.is_dashing
        and not player.is_dodging
        and (
            not player.is_attacking
            or player.can_cancel_attack_to_block()
            or player.attack_recovery_timer > 0
        )
    )

    if keys[pygame.K_k] and can_block:
        if not player.is_blocking and not player.is_parrying:
            player.block_direction = player.facing
        player.is_blocking = player.parry_window_timer <= 0
        player.facing = player.block_direction
    else:
        player.is_blocking = False
        player.is_parrying = False
        player.parry_window_timer = 0


def can_block_attack_from(player, attacker_direction):
    """Block only works when the player is guarding toward the attacker."""
    return player.is_blocking and player.block_direction == -attacker_direction


def can_parry_attack_from(player, attacker_direction):
    """Parry uses the same front-facing rule as block, but only briefly."""
    return player.is_parrying and player.block_direction == -attacker_direction


def start_guard(player):
    """Open a short parry window on the first K press before normal block.

    Parry adds depth because the player trades safety for reward. The guard
    button still falls back to block after the short timing window ends.
    """
    can_guard = (
        not player.defeated
        and not player.is_hurt
        and not player.is_dashing
        and not player.is_dodging
        and not player.is_blocking
        and not player.is_parrying
        and (
            not player.is_attacking
            or player.can_cancel_attack_to_block()
            or player.attack_recovery_timer > 0
        )
    )

    if not can_guard:
        return

    player.block_direction = player.facing

    if player.parry_cooldown_timer <= 0:
        player.is_parrying = True
        player.parry_window_timer = PLAYER_PARRY_WINDOW_DURATION
        player.parry_cooldown_timer = PLAYER_PARRY_COOLDOWN


def parry_success(player, attacker_direction):
    """Resolve a successful parry without entering the normal hurt state."""
    player.is_parrying = False
    player.parry_window_timer = 0
    player.is_blocking = False
    player.successful_parry_timer = PLAYER_PARRY_SUCCESS_DURATION
    player.counter_window_timer = PLAYER_COUNTER_WINDOW_DURATION
    player.can_counter = True
    player.block_flash_timer = 0
    player.knockback_velocity_x = attacker_direction * (player.block_pushback * 0.45)
    player.begin_parry_payoff_feedback()

    return {
        "hitstop": PLAYER_PARRY_HITSTOP,
        "shake_duration": PLAYER_PARRY_SHAKE_DURATION,
        "shake_strength": PLAYER_PARRY_SHAKE_STRENGTH,
    }


def block_hit(player, amount, attacker_direction):
    """Absorb part of an enemy hit without entering full hurt stun."""
    if player.defeated:
        return None

    blocked_damage = max(1, round(amount * player.block_damage_reduction))
    player.health = max(0, player.health - blocked_damage)
    player.block_flash_timer = player.block_flash_duration
    player.knockback_velocity_x = attacker_direction * player.block_pushback
    player.begin_guard_stress_feedback(attacker_direction)

    if player.health == 0:
        player.defeated = True
        player.is_blocking = False

    return {
        "hitstop": PLAYER_BLOCK_HITSTOP,
        "shake_duration": PLAYER_BLOCK_SHAKE_DURATION,
        "shake_strength": PLAYER_BLOCK_SHAKE_STRENGTH,
    }
