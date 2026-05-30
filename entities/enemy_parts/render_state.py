"""Animation-ready visual state mapping for enemies."""

from settings import (
    ENEMY_STATE_ATTACK,
    ENEMY_STATE_CHASE,
    ENEMY_STATE_DEFEATED,
    ENEMY_STATE_HURT,
    ENEMY_STATE_STAGGER,
    ENEMY_STATE_TELEGRAPH,
)


def get_enemy_visual_state(enemy):
    """Return a sprite-friendly visual state without changing AI logic."""
    if enemy.defeated or enemy.state == ENEMY_STATE_DEFEATED:
        return "defeated"
    if enemy.state == ENEMY_STATE_HURT or enemy.hurt_reaction_timer > 0:
        return "hurt"
    if enemy.state == ENEMY_STATE_STAGGER:
        return "stagger"
    if enemy.state == ENEMY_STATE_TELEGRAPH:
        return "telegraph"
    if enemy.state == ENEMY_STATE_ATTACK:
        return "attack"
    if enemy.recovery_timer > 0 or enemy.retreat_timer > 0:
        return "recovery"
    if enemy.state == ENEMY_STATE_CHASE:
        return "chase"
    return "idle"
