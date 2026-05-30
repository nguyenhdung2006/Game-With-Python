"""Player reaction, recovery, and risk-readability helpers."""

from settings import (
    PLAYER_ATTACK_HIT_PAYOFF_DURATION,
    PLAYER_COUNTER_PAYOFF_DURATION,
    PLAYER_DODGE_SETTLE_DURATION,
    PLAYER_DODGE_UNSAFE_DURATION,
    PLAYER_GUARD_RECOIL_PIXELS,
    PLAYER_GUARD_STRESS_COLOR,
    PLAYER_GUARD_STRESS_DURATION,
    PLAYER_HARD_LANDING_FEEDBACK_DURATION,
    PLAYER_HARD_LANDING_SPEED,
    PLAYER_LANDING_COMPRESS_PIXELS,
    PLAYER_LANDING_FEEDBACK_DURATION,
    PLAYER_PARRY_PAYOFF_DURATION,
    PLAYER_PAYOFF_COLOR,
    PLAYER_RECOVERY_FLASH_DURATION,
    PLAYER_RECOVERY_TINT_COLOR,
    PLAYER_STATE_SETTLE_DURATION,
    PLAYER_UNSAFE_OUTLINE_COLOR,
    PLAYER_WHIFF_FEEDBACK_DURATION,
    PLAYER_WHIFF_FINISHER_RECOVERY_MIN,
    PLAYER_WHIFF_RECOIL_DURATION,
    PLAYER_WHIFF_RECOIL_PIXELS,
)


def initialize_reaction_state(player):
    """Store player-side feedback tuning and runtime timers."""
    player.recovery_tint_color = PLAYER_RECOVERY_TINT_COLOR
    player.unsafe_outline_color = PLAYER_UNSAFE_OUTLINE_COLOR
    player.guard_stress_color = PLAYER_GUARD_STRESS_COLOR
    player.payoff_color = PLAYER_PAYOFF_COLOR

    player.whiff_feedback_duration = PLAYER_WHIFF_FEEDBACK_DURATION
    player.whiff_recoil_duration = PLAYER_WHIFF_RECOIL_DURATION
    player.whiff_recoil_pixels = PLAYER_WHIFF_RECOIL_PIXELS
    player.whiff_finisher_recovery_min = PLAYER_WHIFF_FINISHER_RECOVERY_MIN
    player.recovery_flash_duration = PLAYER_RECOVERY_FLASH_DURATION
    player.landing_feedback_duration = PLAYER_LANDING_FEEDBACK_DURATION
    player.hard_landing_feedback_duration = PLAYER_HARD_LANDING_FEEDBACK_DURATION
    player.landing_compress_pixels = PLAYER_LANDING_COMPRESS_PIXELS
    player.dodge_unsafe_duration = PLAYER_DODGE_UNSAFE_DURATION
    player.dodge_settle_duration = PLAYER_DODGE_SETTLE_DURATION
    player.guard_stress_duration = PLAYER_GUARD_STRESS_DURATION
    player.guard_recoil_pixels = PLAYER_GUARD_RECOIL_PIXELS
    player.parry_payoff_duration = PLAYER_PARRY_PAYOFF_DURATION
    player.counter_payoff_duration = PLAYER_COUNTER_PAYOFF_DURATION
    player.attack_hit_payoff_duration = PLAYER_ATTACK_HIT_PAYOFF_DURATION
    player.state_settle_duration = PLAYER_STATE_SETTLE_DURATION

    player.whiff_feedback_timer = 0
    player.unsafe_timer = 0
    player.recovery_flash_timer = 0
    player.reaction_recoil_timer = 0
    player.reaction_recoil_offset = 0
    player.landing_feedback_timer = 0
    player.guard_stress_timer = 0
    player.guard_recoil_timer = 0
    player.guard_recoil_offset = 0
    player.payoff_timer = 0
    player.attack_hit_payoff_timer = 0
    player.state_settle_timer = 0


def update_reaction_timers(player, dt):
    """Count down player readability timers without affecting combat rules."""
    _tick_timer(player, "whiff_feedback_timer", dt)
    _tick_timer(player, "unsafe_timer", dt)
    _tick_timer(player, "recovery_flash_timer", dt)
    _tick_timer(player, "landing_feedback_timer", dt)
    _tick_timer(player, "guard_stress_timer", dt)
    _tick_timer(player, "payoff_timer", dt)
    _tick_timer(player, "attack_hit_payoff_timer", dt)
    _tick_timer(player, "state_settle_timer", dt)

    if player.reaction_recoil_timer > 0:
        player.reaction_recoil_timer = max(0, player.reaction_recoil_timer - dt)
        if player.reaction_recoil_timer == 0:
            player.reaction_recoil_offset = 0

    if player.guard_recoil_timer > 0:
        player.guard_recoil_timer = max(0, player.guard_recoil_timer - dt)
        if player.guard_recoil_timer == 0:
            player.guard_recoil_offset = 0


def begin_attack_recovery_feedback(player):
    """Mark attack recovery as readable, with extra emphasis for whiffs."""
    player.state_settle_timer = max(player.state_settle_timer, player.state_settle_duration)

    if player.has_hit_this_attack:
        return

    player.whiff_feedback_timer = max(player.whiff_feedback_timer, player.whiff_feedback_duration)
    player.unsafe_timer = max(player.unsafe_timer, player.whiff_feedback_duration)
    player.recovery_flash_timer = max(player.recovery_flash_timer, player.recovery_flash_duration)
    player.reaction_recoil_timer = max(player.reaction_recoil_timer, player.whiff_recoil_duration)
    player.reaction_recoil_offset = max(player.reaction_recoil_offset, player.whiff_recoil_pixels)

    if player.combo_step >= 3:
        player.attack_recovery_timer = max(player.attack_recovery_timer, player.whiff_finisher_recovery_min)


def begin_landing_feedback(player, fall_speed):
    """Give landings a subtle compression and unsafe flash."""
    if fall_speed >= PLAYER_HARD_LANDING_SPEED:
        feedback_duration = player.hard_landing_feedback_duration
    else:
        feedback_duration = player.landing_feedback_duration

    player.landing_feedback_timer = max(player.landing_feedback_timer, feedback_duration)
    player.unsafe_timer = max(player.unsafe_timer, feedback_duration)
    player.recovery_flash_timer = max(player.recovery_flash_timer, player.recovery_flash_duration * 0.8)
    player.state_settle_timer = max(player.state_settle_timer, player.state_settle_duration)


def begin_dodge_recovery_feedback(player):
    """Make dodge exits readable as a small punishable settle moment."""
    player.unsafe_timer = max(player.unsafe_timer, player.dodge_unsafe_duration)
    player.recovery_flash_timer = max(player.recovery_flash_timer, player.recovery_flash_duration * 0.75)
    player.state_settle_timer = max(player.state_settle_timer, player.dodge_settle_duration)


def begin_guard_stress_feedback(player, attacker_direction):
    """Pulse the guard and body after a blocked hit."""
    player.guard_stress_timer = max(player.guard_stress_timer, player.guard_stress_duration)
    player.guard_recoil_timer = max(player.guard_recoil_timer, player.guard_stress_duration)
    player.guard_recoil_offset = player.guard_recoil_pixels * attacker_direction
    player.recovery_flash_timer = max(player.recovery_flash_timer, player.recovery_flash_duration * 0.6)


def begin_parry_payoff_feedback(player):
    """Reward a clean parry with a brighter but short-lived player pulse."""
    player.payoff_timer = max(player.payoff_timer, player.parry_payoff_duration)
    player.attack_hit_payoff_timer = max(player.attack_hit_payoff_timer, player.attack_hit_payoff_duration)


def begin_counter_payoff_feedback(player):
    """Make the counterattack startup read like an earned punish."""
    player.payoff_timer = max(player.payoff_timer, player.counter_payoff_duration)
    player.attack_hit_payoff_timer = max(player.attack_hit_payoff_timer, player.attack_hit_payoff_duration)


def register_attack_payoff(player):
    """Add a small success pulse when the player's strike connects."""
    scale = 1.0
    if player.is_counter_attacking:
        scale = 1.6
    elif player.combo_step >= 3:
        scale = 1.35

    duration = player.attack_hit_payoff_duration * scale
    player.attack_hit_payoff_timer = max(player.attack_hit_payoff_timer, duration)
    player.payoff_timer = max(player.payoff_timer, duration * 0.8)


def get_player_reaction_offset(player):
    """Return a temporary draw-only recoil offset."""
    offset = 0

    if player.reaction_recoil_timer > 0:
        offset -= player.facing * player.reaction_recoil_offset

    if player.guard_recoil_timer > 0:
        offset += player.guard_recoil_offset

    return round(offset)


def _tick_timer(owner, attr_name, dt):
    value = getattr(owner, attr_name)
    if value > 0:
        setattr(owner, attr_name, max(0, value - dt))
