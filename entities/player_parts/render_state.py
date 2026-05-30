"""Animation-ready visual state mapping for the player."""


def get_player_visual_state(player):
    """Return a sprite-friendly visual state without changing gameplay logic."""
    if player.defeated:
        return "defeated"
    if player.is_hurt:
        return "hurt"
    if player.is_counter_attacking:
        return "counter"
    if player.is_attacking:
        return f"attack_{max(1, player.combo_step)}"
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
    if abs(getattr(player, "last_move_direction", 0)) > 0:
        return "run"
    return "idle"
