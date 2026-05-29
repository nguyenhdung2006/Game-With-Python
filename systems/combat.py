"""Combat helpers.

This module keeps hitbox, damage, knockback, and cooldown rules reusable so
main.py does not fill up with combat details as the game grows.
"""

import pygame

from settings import (
    ENEMY_ATTACK_DAMAGE,
    ENEMY_ATTACK_HEIGHT,
    ENEMY_ATTACK_HITSTOP,
    ENEMY_ATTACK_KNOCKBACK,
    ENEMY_ATTACK_RANGE,
    ENEMY_ATTACK_SHAKE_DURATION,
    ENEMY_ATTACK_SHAKE_STRENGTH,
    LIGHT_ATTACK_COMBO,
)


def create_attack_hitbox(player):
    """Create a sword hitbox in front of the player.

    The hitbox is a pygame.Rect that only matters during an active attack.
    It sits on the side the player is facing and lines up around the torso.
    """
    if player.facing == 1:
        x = player.rect.right
    else:
        x = player.rect.left - player.attack_range

    y = player.rect.centery - player.attack_height // 2
    return pygame.Rect(x, y, player.attack_range, player.attack_height)


def create_enemy_attack_hitbox(enemy):
    """Create the enemy melee hitbox in front of its facing direction."""
    if enemy.facing == 1:
        x = enemy.rect.right
    else:
        x = enemy.rect.left - ENEMY_ATTACK_RANGE

    y = enemy.rect.centery - ENEMY_ATTACK_HEIGHT // 2
    return pygame.Rect(x, y, ENEMY_ATTACK_RANGE, ENEMY_ATTACK_HEIGHT)


def get_combo_attack_data(combo_step):
    """Return damage, size, duration, and knockback values for one combo hit."""
    return LIGHT_ATTACK_COMBO[combo_step - 1]


def apply_damage(target, amount):
    """Reduce target health through its own damage method."""
    if hasattr(target, "take_damage"):
        target.take_damage(amount)


def apply_knockback(target, direction, strength):
    """Push a target away from the attacker."""
    if hasattr(target, "knockback_velocity_x"):
        target.knockback_velocity_x = direction * strength


def process_player_attack(player, enemy):
    """Apply one light-attack hit if the player's active hitbox touches enemy."""
    if enemy.defeated:
        return

    attack_hitbox = player.get_attack_hitbox()

    if attack_hitbox is None or player.has_hit_this_attack:
        return

    if attack_hitbox.colliderect(enemy.rect):
        apply_damage(enemy, player.attack_damage)
        apply_knockback(enemy, player.facing, player.attack_knockback)
        player.has_hit_this_attack = True
        return get_combo_attack_data(player.combo_step)

    return None


def process_enemy_attack(enemy, player):
    """Apply one enemy attack hit if its active hitbox touches the player."""
    if not enemy.is_attack_active() or enemy.has_hit_this_attack:
        return None

    attack_hitbox = create_enemy_attack_hitbox(enemy)

    if attack_hitbox.colliderect(player.rect):
        apply_damage(player, ENEMY_ATTACK_DAMAGE)
        apply_knockback(player, enemy.facing, ENEMY_ATTACK_KNOCKBACK)
        enemy.has_hit_this_attack = True
        return {
            "hitstop": ENEMY_ATTACK_HITSTOP,
            "shake_duration": ENEMY_ATTACK_SHAKE_DURATION,
            "shake_strength": ENEMY_ATTACK_SHAKE_STRENGTH,
        }

    return None


def can_use_action(cooldown_timer):
    """Return True when an action cooldown has finished."""
    return cooldown_timer <= 0


def start_cooldown():
    """Return the default attack cooldown duration."""
    return LIGHT_ATTACK_COMBO[0]["cooldown"]


def update_cooldown(cooldown_timer, dt):
    """Count an action cooldown down toward zero."""
    return max(0, cooldown_timer - dt)
