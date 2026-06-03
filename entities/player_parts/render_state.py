"""Animation-ready visual state mapping for the player."""


def get_player_visual_state(player):
    """Return a sprite-friendly visual state without changing gameplay logic."""
    if player.defeated:
        return "defeated"
    if player.is_hurt:
        return f"hurt_{max(1, getattr(player, 'hurt_chain_step', 1))}"
    if getattr(player, "is_transforming", lambda: False)():
        return "super_saiyan_transform"
    if getattr(player, "skill_visual_timer", 0) > 0:
        return getattr(player, "skill_visual_state", None) or "idle"
    if player.is_counter_attacking:
        return "counter"
    if player.is_attacking:
        if getattr(player, "is_super_saiyan", False):
            return f"super_saiyan_{getattr(player, 'attack_style', 'punch')}_{max(1, player.combo_step)}"
        return f"{getattr(player, 'attack_style', 'punch')}_{max(1, player.combo_step)}"
    if getattr(player, "melee_recovery_visual_timer", 0) > 0:
        return getattr(player, "melee_recovery_visual_state", None) or "idle"
    if player.is_dodging:
        return "dodge"
    if player.is_parrying or player.successful_parry_timer > 0:
        return "parry"
    if player.is_blocking:
        return "block"
    if player.is_dashing:
        return "dash"
    if not player.grounded:
        return "jump" if player.velocity_y < 0 else "fall"
    if getattr(player, "hurt_visual_timer", 0) > 0:
        return f"hurt_{max(1, getattr(player, 'hurt_chain_step', 1))}"
    if abs(getattr(player, "last_move_direction", 0)) > 0:
        return "run"
    if getattr(player, "is_super_saiyan", False):
        return "super_saiyan_idle"
    return "idle"


def update_player_visual_timers(player, dt):
    """Tick presentation-only skill and melee recovery states."""
    if getattr(player, "skill_visual_timer", 0) > 0:
        player.skill_visual_timer = max(0.0, player.skill_visual_timer - dt)
        if player.skill_visual_timer == 0:
            player.skill_visual_state = None

    if getattr(player, "melee_recovery_visual_timer", 0) > 0:
        player.melee_recovery_visual_timer = max(0.0, player.melee_recovery_visual_timer - dt)
        if player.melee_recovery_visual_timer == 0:
            player.melee_recovery_visual_state = None
