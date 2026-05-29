"""Future combat helpers.

Phase 4 can build on this file for attacks, hitboxes, damage, and cooldowns.
For now these helpers are intentionally small placeholders.
"""

import pygame

from settings import ATTACK_COOLDOWN, ATTACK_HEIGHT, ATTACK_RANGE


def create_attack_hitbox(attacker_rect, facing):
    """Create a simple future melee hitbox in front of an attacker."""
    if facing == 1:
        x = attacker_rect.right
    else:
        x = attacker_rect.left - ATTACK_RANGE

    y = attacker_rect.centery - ATTACK_HEIGHT // 2
    return pygame.Rect(x, y, ATTACK_RANGE, ATTACK_HEIGHT)


def apply_damage(target, amount, knockback_x=0):
    """Ask a target to take damage if it supports that behavior."""
    if hasattr(target, "take_damage"):
        target.take_damage(amount, knockback_x)


def can_use_action(cooldown_timer):
    """Return True when an action cooldown has finished."""
    return cooldown_timer <= 0


def start_cooldown():
    """Return the default attack cooldown duration."""
    return ATTACK_COOLDOWN


def update_cooldown(cooldown_timer, dt):
    """Count an action cooldown down toward zero."""
    return max(0, cooldown_timer - dt)
