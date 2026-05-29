"""Shared enemy behavior.

BaseEnemy stays as the public reusable superclass, while the heavy behavior
groups now live in focused helper modules under `entities/enemy_parts/`.
"""

from entities.enemy_parts.behavior import (
    face_player as _face_player,
    is_attack_active as _is_attack_active,
    register_attack_reaction as _register_attack_reaction,
    start_attack as _start_attack,
    start_retreat as _start_retreat,
    start_stagger as _start_stagger,
    start_telegraph as _start_telegraph,
    take_damage as _take_damage,
    update as _update,
    update_attack as _update_attack,
    update_idle_or_chase as _update_idle_or_chase,
    update_knockback as _update_knockback,
    update_recovery as _update_recovery,
    update_retreat as _update_retreat,
    update_telegraph as _update_telegraph,
    update_timers as _update_timers,
)
from entities.enemy_parts.render import draw as _draw
from entities.enemy_parts.setup import initialize_enemy_state


class BaseEnemy:
    """Reusable enemy base class for melee archetypes."""

    def __init__(self, x, y, config):
        initialize_enemy_state(self, x, y, config)

    # Shared behavior
    update = _update
    update_timers = _update_timers
    update_knockback = _update_knockback
    face_player = _face_player
    update_idle_or_chase = _update_idle_or_chase
    update_retreat = _update_retreat
    update_recovery = _update_recovery
    start_telegraph = _start_telegraph
    update_telegraph = _update_telegraph
    start_attack = _start_attack
    update_attack = _update_attack
    start_retreat = _start_retreat
    start_stagger = _start_stagger
    is_attack_active = _is_attack_active
    take_damage = _take_damage
    register_attack_reaction = _register_attack_reaction

    # Drawing
    draw = _draw
