"""Player attack, combo, and counterattack helpers."""

from settings import COUNTER_ATTACK, KICK_ATTACK_COMBO, LIGHT_ATTACK_COMBO, PLAYER_ATTACK_BUFFER_DURATION
from systems.audio_manager import play_audio_event
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
    """Start or queue the next punch in the five-hit R06 combo."""
    start_combo_attack(player, "punch", allow_counter=True)


def start_kick_attack(player):
    """Start or queue the next kick in the three-hit R07 combo."""
    start_combo_attack(player, "kick")


def start_combo_attack(player, attack_style, allow_counter=False):
    """Start one attack style while preserving seamless queued playback."""
    if (
        player.defeated
        or player.is_hurt
        or player.is_parrying
        or player.is_dodging
        or player.is_transforming()
    ):
        return

    # Counterattack is a separate reward attack. It does not continue the
    # normal combo chain because it exists as the payoff for a correct parry.
    if allow_counter and player.can_counter and player.counter_window_timer > 0 and not player.is_attacking:
        begin_counter_attack(player)
        return

    if player.is_blocking:
        return

    if is_in_action_recovery(player):
        player.buffered_attack = True
        player.buffered_attack_style = attack_style
        player.attack_buffer_timer = PLAYER_ATTACK_BUFFER_DURATION
        return

    attack_combo = get_attack_combo(attack_style)
    if player.is_attacking:
        if player.is_counter_attacking:
            return
        if (
            player.attack_style == attack_style
            and player.combo_step < len(attack_combo)
            and player.combo_timer > 0
        ):
            player.queued_next_attack = True
            player.queued_attack_style = attack_style
        return

    if not can_use_action(player.attack_cooldown_timer):
        return

    if (
        player.combo_style != attack_style
        or player.combo_timer <= 0
        or player.combo_step >= len(attack_combo)
    ):
        next_combo_step = 1
    else:
        next_combo_step = player.combo_step + 1

    begin_combo_attack(player, next_combo_step, attack_style)


def get_attack_combo(attack_style):
    """Return the configured mechanics for one melee style."""
    if attack_style == "kick":
        return KICK_ATTACK_COMBO
    return LIGHT_ATTACK_COMBO


def begin_combo_attack(player, combo_step, attack_style="punch"):
    """Apply the timing, damage, and hitbox data for one combo hit."""
    attack_data = get_combo_attack_data(combo_step, attack_style)

    player.attack_style = attack_style
    player.combo_style = attack_style
    player.combo_step = combo_step
    player.combo_timer = player.combo_reset_time
    player.melee_recovery_visual_state = None
    player.melee_recovery_visual_timer = 0

    _apply_attack_data(player, attack_data)
    player.is_counter_attacking = False
    player.is_attacking = True
    player.attack_timer = player.attack_duration
    player.attack_cooldown_timer = player.attack_cooldown
    player.has_hit_this_attack = False
    play_audio_event(player, "player_attack")


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
    player.queued_attack_style = None
    player.buffered_attack = False
    player.buffered_attack_style = None
    player.attack_buffer_timer = 0
    player.melee_recovery_visual_state = None
    player.melee_recovery_visual_timer = 0

    _apply_attack_data(player, attack_data)
    player.begin_counter_payoff_feedback()
    player.is_counter_attacking = True
    player.is_attacking = True
    player.attack_timer = player.attack_duration
    player.attack_cooldown_timer = player.attack_cooldown
    player.has_hit_this_attack = False
    play_audio_event(player, "player_attack")


def _apply_attack_data(player, attack_data):
    """Copy a dictionary of attack values onto the player state."""
    player.attack_damage = attack_data["damage"]
    player.attack_range = attack_data["range"]
    player.attack_height = attack_data["height"]
    player.attack_knockback = attack_data["knockback"]
    player.attack_launch_y = attack_data.get("launch_y", 0)
    player.attack_movement_multiplier = attack_data["movement_multiplier"]
    player.attack_color = attack_data["color"]
    player.attack_hitstop = attack_data["hitstop"]
    player.attack_shake_duration = attack_data["shake_duration"]
    player.attack_shake_strength = attack_data["shake_strength"]
    player.attack_duration = attack_data["duration"]
    player.attack_cooldown = attack_data["cooldown"]
    player.attack_recovery = attack_data["recovery"]
    player.attack_cancel_window = attack_data["cancel_window"]
    player.attack_recovery_visual_state = attack_data.get("recovery_visual_state")
    player.attack_recovery_visual_duration = attack_data.get("recovery_visual_duration", 0)


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
            attack_combo = get_attack_combo(player.attack_style)
            can_continue_combo = (
                not player.is_counter_attacking
                and player.queued_next_attack
                and player.queued_attack_style == player.attack_style
                and player.combo_step < len(attack_combo)
                and player.combo_timer > 0
            )
            if can_continue_combo:
                player.queued_next_attack = False
                player.queued_attack_style = None
                player.attack_cooldown_timer = 0
                player.attack_recovery_timer = 0
                begin_combo_attack(player, player.combo_step + 1, player.attack_style)
            else:
                player.is_attacking = False
                player.attack_timer = 0
                player.attack_recovery_timer = player.attack_recovery
                begin_melee_recovery_visual(player)
                player.begin_attack_recovery_feedback()
                if player.is_counter_attacking:
                    player.is_counter_attacking = False
                ended_attack_this_frame = True

    if player.combo_timer == 0 and not player.is_attacking:
        reset_combo(player)

    player.attack_cooldown_timer = update_cooldown(player.attack_cooldown_timer, dt)
    if player.attack_recovery_timer > 0 and not ended_attack_this_frame:
        player.attack_recovery_timer = max(0, player.attack_recovery_timer - dt)

    if (
        player.buffered_attack
        and not player.is_attacking
        and not is_in_action_recovery(player)
        and can_use_action(player.attack_cooldown_timer)
    ):
        attack_style = player.buffered_attack_style or "punch"
        player.buffered_attack = False
        player.buffered_attack_style = None
        start_combo_attack(player, attack_style, allow_counter=attack_style == "punch")

    if player.buffered_attack and player.attack_buffer_timer == 0 and not player.is_attacking:
        player.buffered_attack = False
        player.buffered_attack_style = None


def reset_combo(player):
    """Return the combo chain to hit 1 after the timing window expires."""
    player.combo_step = 0
    player.combo_timer = 0
    player.combo_style = None
    player.queued_next_attack = False
    player.queued_attack_style = None


def begin_melee_recovery_visual(player):
    """Play an approved stop-only recovery when the current hit defines one."""
    visual_state = getattr(player, "attack_recovery_visual_state", None)
    if visual_state is None:
        return
    player.melee_recovery_visual_state = visual_state
    player.melee_recovery_visual_timer = getattr(player, "attack_recovery_visual_duration", 0)


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
