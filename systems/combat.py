"""Combat helpers.

This module keeps hitbox, damage, knockback, and cooldown rules reusable so
main.py does not fill up with combat details as the game grows.
"""

import pygame

from settings import ATTACK_COOLDOWN, ATTACK_HEIGHT, ATTACK_KNOCKBACK_SPEED, ATTACK_RANGE


def create_attack_hitbox(player):
    """Create a sword hitbox in front of the player.

    The hitbox is a pygame.Rect that only matters during an active attack.
    It sits on the side the player is facing and lines up around the torso.
    """
    if player.facing == 1:
        x = player.rect.right
    else:
        x = player.rect.left - ATTACK_RANGE

    y = player.rect.centery - ATTACK_HEIGHT // 2
    return pygame.Rect(x, y, ATTACK_RANGE, ATTACK_HEIGHT)


def apply_damage(target, amount):
    """Reduce target health through its own damage method."""
    if hasattr(target, "take_damage"):
        target.take_damage(amount)


def apply_knockback(target, direction):
    """Push a target away from the attacker."""
    if hasattr(target, "knockback_velocity_x"):
        target.knockback_velocity_x = direction * ATTACK_KNOCKBACK_SPEED


def process_player_attack(player, enemy):
    """Apply one light-attack hit if the player's active hitbox touches enemy."""
    if enemy.defeated:
        return

    attack_hitbox = player.get_attack_hitbox()

    if attack_hitbox is None or player.has_hit_this_attack:
        return

    if attack_hitbox.colliderect(enemy.rect):
        apply_damage(enemy, player.attack_damage)
        apply_knockback(enemy, player.facing)
        player.has_hit_this_attack = True


def can_use_action(cooldown_timer):
    """Return True when an action cooldown has finished."""
    return cooldown_timer <= 0


def start_cooldown():
    """Return the default attack cooldown duration."""
    return ATTACK_COOLDOWN


def update_cooldown(cooldown_timer, dt):
    """Count an action cooldown down toward zero."""
    return max(0, cooldown_timer - dt)
