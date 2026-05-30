"""Player entity.

The Player class stays the public entry point for gameplay code, while the
large behavior groups now live in focused helper modules under
`entities/player_parts/`.
"""

from entities.player_parts.combat import (
    begin_combo_attack as _begin_combo_attack,
    begin_counter_attack as _begin_counter_attack,
    can_cancel_attack_to_block as _can_cancel_attack_to_block,
    get_attack_hitbox as _get_attack_hitbox,
    get_attack_impact as _get_attack_impact,
    is_in_action_recovery as _is_in_action_recovery,
    reset_combo as _reset_combo,
    start_light_attack as _start_light_attack,
    update_attack_timers as _update_attack_timers,
)
from entities.player_parts.defense import (
    block_hit as _block_hit,
    can_block_attack_from as _can_block_attack_from,
    can_parry_attack_from as _can_parry_attack_from,
    can_take_damage as _can_take_damage,
    parry_success as _parry_success,
    start_guard as _start_guard,
    take_damage as _take_damage,
    update_block_state as _update_block_state,
    update_hurt_timers as _update_hurt_timers,
)
from entities.player_parts.movement import (
    add_dash_trail as _add_dash_trail,
    apply_physics as _apply_physics,
    get_current_move_speed as _get_current_move_speed,
    handle_input as _handle_input,
    jump as _jump,
    start_dash as _start_dash,
    start_dodge as _start_dodge,
    start_landing_recovery as _start_landing_recovery,
    update_dash_cooldown as _update_dash_cooldown,
    update_dash_trail as _update_dash_trail,
    update_dodge_timers as _update_dodge_timers,
    update_knockback as _update_knockback,
)
from entities.player_parts.reaction import (
    begin_attack_recovery_feedback as _begin_attack_recovery_feedback,
    begin_counter_payoff_feedback as _begin_counter_payoff_feedback,
    begin_dodge_recovery_feedback as _begin_dodge_recovery_feedback,
    begin_guard_stress_feedback as _begin_guard_stress_feedback,
    begin_landing_feedback as _begin_landing_feedback,
    begin_parry_payoff_feedback as _begin_parry_payoff_feedback,
    get_player_reaction_offset as _get_player_reaction_offset,
    register_attack_payoff as _register_attack_payoff,
    update_reaction_timers as _update_reaction_timers,
)
from entities.player_parts.render import draw as _draw
from entities.player_parts.setup import initialize_player_state


class Player:
    """Main player object used by the rest of the game."""

    def __init__(self, x, y):
        initialize_player_state(self, x, y)

    def update(self, keys, dt):
        """Run the per-frame player flow in one readable place."""
        self.update_hurt_timers(dt)
        self.update_reaction_timers(dt)

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

    # Combat behavior
    can_cancel_attack_to_block = _can_cancel_attack_to_block
    is_in_action_recovery = _is_in_action_recovery
    start_light_attack = _start_light_attack
    begin_combo_attack = _begin_combo_attack
    begin_counter_attack = _begin_counter_attack
    update_attack_timers = _update_attack_timers
    reset_combo = _reset_combo
    get_attack_hitbox = _get_attack_hitbox
    get_attack_impact = _get_attack_impact
    register_attack_payoff = _register_attack_payoff

    # Defense behavior
    take_damage = _take_damage
    can_take_damage = _can_take_damage
    update_hurt_timers = _update_hurt_timers
    update_block_state = _update_block_state
    can_block_attack_from = _can_block_attack_from
    can_parry_attack_from = _can_parry_attack_from
    start_guard = _start_guard
    parry_success = _parry_success
    block_hit = _block_hit

    # Player reaction and readability behavior
    begin_attack_recovery_feedback = _begin_attack_recovery_feedback
    begin_counter_payoff_feedback = _begin_counter_payoff_feedback
    begin_dodge_recovery_feedback = _begin_dodge_recovery_feedback
    begin_guard_stress_feedback = _begin_guard_stress_feedback
    begin_landing_feedback = _begin_landing_feedback
    begin_parry_payoff_feedback = _begin_parry_payoff_feedback
    update_reaction_timers = _update_reaction_timers
    get_reaction_offset = _get_player_reaction_offset

    # Movement and physics behavior
    update_knockback = _update_knockback
    handle_input = _handle_input
    get_current_move_speed = _get_current_move_speed
    jump = _jump
    start_dash = _start_dash
    start_dodge = _start_dodge
    update_dash_cooldown = _update_dash_cooldown
    update_dodge_timers = _update_dodge_timers
    start_landing_recovery = _start_landing_recovery
    apply_physics = _apply_physics
    add_dash_trail = _add_dash_trail
    update_dash_trail = _update_dash_trail

    # Rendering behavior
    draw = _draw
