"""Player attack, combo, and counterattack helpers."""

from settings import COUNTER_ATTACK, LIGHT_ATTACK_COMBO, PLAYER_ATTACK_BUFFER_DURATION
from systems.combat import can_use_action, create_attack_hitbox, get_combo_attack_data, update_cooldown


def can_cancel_attack_to_block(player):
    """Allow guarding near the end of an attack instead of only after it ends."""
    return player.is_attacking and player.attack_timer <= player.attack_cancel_window


def is_in_action_recovery(player):
    """Recovery timers stop instant action spam between states."""
    return (
        player.attack_recovery_timer > 0
        or player.dodge_recovery_timer > 0
        or player.landing_recovery_timer > 0
    )


def start_light_attack(player):
    """Start or queue the next hit in the 3-hit light combo."""
    if player.defeated or player.is_hurt or player.is_parrying or player.is_dodging:
        return

    # Counterattack is a separate reward attack. It does not continue the
    # normal combo chain because it exists as the payoff for a correct parry.
    if player.can_counter and player.counter_window_timer > 0 and not player.is_attacking:
        begin_counter_attack(player)
        return

    if player.is_blocking:
        return

    if is_in_action_recovery(player):
        player.buffered_attack = True
        player.attack_buffer_timer = PLAYER_ATTACK_BUFFER_DURATION
        return

    if player.is_attacking:
        if player.is_counter_attacking:
            return
        if player.combo_step < len(LIGHT_ATTACK_COMBO) and player.combo_timer > 0:
            player.queued_next_attack = True
        return

    if not can_use_action(player.attack_cooldown_timer):
        return

    if player.combo_timer <= 0 or player.combo_step >= len(LIGHT_ATTACK_COMBO):
        next_combo_step = 1
    else:
        next_combo_step = player.combo_step + 1

    begin_combo_attack(player, next_combo_step)


def begin_combo_attack(player, combo_step):
    """Apply the timing, damage, and hitbox data for one combo hit."""
    attack_data = get_combo_attack_data(combo_step)

    player.combo_step = combo_step
    player.combo_timer = player.combo_reset_time

    _apply_attack_data(player, attack_data)
    player.is_counter_attacking = False
    player.is_attacking = True
    player.attack_timer = player.attack_duration
    player.attack_cooldown_timer = player.attack_cooldown
    player.has_hit_this_attack = False


def begin_counter_attack(player):
    """Start the heavy punish attack granted by a successful parry.

    The counter window is short on purpose. That turns parry into a
    meaningful reward state instead of just free safety.
    """
    attack_data = COUNTER_ATTACK
    player.can_counter = False
    player.counter_window_timer = 0
    player.is_blocking = False
    player.combo_step = 0
    player.combo_timer = 0
    player.queued_next_attack = False
    player.buffered_attack = False
    player.attack_buffer_timer = 0

    _apply_attack_data(player, attack_data)
    player.is_counter_attacking = True
    player.is_attacking = True
    player.attack_timer = player.attack_duration
    player.attack_cooldown_timer = player.attack_cooldown
    player.has_hit_this_attack = False


def _apply_attack_data(player, attack_data):
    """Copy a dictionary of attack values onto the player state."""
    player.attack_damage = attack_data["damage"]
    player.attack_range = attack_data["range"]
    player.attack_height = attack_data["height"]
    player.attack_knockback = attack_data["knockback"]
    player.attack_movement_multiplier = attack_data["movement_multiplier"]
    player.attack_color = attack_data["color"]
    player.attack_hitstop = attack_data["hitstop"]
    player.attack_shake_duration = attack_data["shake_duration"]
    player.attack_shake_strength = attack_data["shake_strength"]
    player.attack_duration = attack_data["duration"]
    player.attack_cooldown = attack_data["cooldown"]
    player.attack_recovery = attack_data["recovery"]
    player.attack_cancel_window = attack_data["cancel_window"]


def update_attack_timers(player, dt):
    """Update attack duration, cooldown, and combo reset using delta time."""
    ended_attack_this_frame = False

    if player.combo_timer > 0:
        player.combo_timer = max(0, player.combo_timer - dt)

        if player.combo_timer == 0 and not player.is_attacking:
            reset_combo(player)

    if player.is_attacking:
        player.attack_timer -= dt

        if player.attack_timer <= 0:
            player.is_attacking = False
            player.attack_timer = 0
            player.attack_recovery_timer = player.attack_recovery
            if player.is_counter_attacking:
                player.is_counter_attacking = False
            ended_attack_this_frame = True

    if player.combo_timer == 0 and not player.is_attacking:
        reset_combo(player)

    player.attack_cooldown_timer = update_cooldown(player.attack_cooldown_timer, dt)
    if player.attack_recovery_timer > 0 and not ended_attack_this_frame:
        player.attack_recovery_timer = max(0, player.attack_recovery_timer - dt)

    if (
        player.queued_next_attack
        and not player.is_attacking
        and not player.is_counter_attacking
        and player.combo_timer > 0
        and can_use_action(player.attack_cooldown_timer)
        and player.attack_recovery_timer <= 0
    ):
        player.queued_next_attack = False
        start_light_attack(player)

    if (
        player.buffered_attack
        and not player.is_attacking
        and not is_in_action_recovery(player)
        and can_use_action(player.attack_cooldown_timer)
    ):
        player.buffered_attack = False
        start_light_attack(player)

    if player.buffered_attack and player.attack_buffer_timer == 0 and not player.is_attacking:
        player.buffered_attack = False


def reset_combo(player):
    """Return the combo chain to hit 1 after the timing window expires."""
    player.combo_step = 0
    player.combo_timer = 0
    player.queued_next_attack = False


def get_attack_hitbox(player):
    """Return the active sword hitbox, or None when not attacking."""
    if not player.is_attacking:
        return None

    return create_attack_hitbox(player)


def get_attack_impact(player):
    """Return the feel values for the currently active player attack."""
    return {
        "hitstop": player.attack_hitstop,
        "shake_duration": player.attack_shake_duration,
        "shake_strength": player.attack_shake_strength,
    }
