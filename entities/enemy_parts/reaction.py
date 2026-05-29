"""Enemy reaction and punish-window feedback helpers."""


def initialize_reaction_state(enemy, config):
    """Store reaction-tuning values and runtime timers on the enemy."""
    enemy.hurt_reaction_duration = config["hurt_reaction_duration"]
    enemy.hurt_reaction_heavy_bonus = config["hurt_reaction_heavy_bonus"]
    enemy.punish_window_duration = config["punish_window_duration"]
    enemy.recovery_flash_duration = config["recovery_flash_duration"]
    enemy.stagger_emphasis_duration = config["stagger_emphasis_duration"]
    enemy.post_stagger_recovery_duration = config["post_stagger_recovery_duration"]
    enemy.reaction_recoil_pixels = config["reaction_recoil_pixels"]
    enemy.recovery_tint_color = config["recovery_tint_color"]
    enemy.punish_outline_color = config["punish_outline_color"]
    enemy.stagger_emphasis_color = config["stagger_emphasis_color"]

    enemy.hurt_reaction_timer = 0
    enemy.punish_window_timer = 0
    enemy.recovery_flash_timer = 0
    enemy.stagger_emphasis_timer = 0
    enemy.reaction_recoil_timer = 0
    enemy.reaction_recoil_offset = 0


def update_reaction_timers(enemy, dt):
    """Count down readability and reaction timers."""
    if enemy.hurt_reaction_timer > 0:
        was_active = enemy.hurt_reaction_timer > 0
        enemy.hurt_reaction_timer = max(0, enemy.hurt_reaction_timer - dt)
        if was_active and enemy.hurt_reaction_timer == 0:
            enemy.recovery_flash_timer = max(enemy.recovery_flash_timer, 0.05)

    if enemy.punish_window_timer > 0:
        enemy.punish_window_timer = max(0, enemy.punish_window_timer - dt)

    if enemy.recovery_flash_timer > 0:
        enemy.recovery_flash_timer = max(0, enemy.recovery_flash_timer - dt)

    if enemy.stagger_emphasis_timer > 0:
        enemy.stagger_emphasis_timer = max(0, enemy.stagger_emphasis_timer - dt)

    if enemy.reaction_recoil_timer > 0:
        enemy.reaction_recoil_timer = max(0, enemy.reaction_recoil_timer - dt)
        if enemy.reaction_recoil_timer == 0:
            enemy.reaction_recoil_offset = 0


def register_player_hit(enemy, player):
    """Scale hit reaction clarity based on the kind of player attack landed."""
    reaction_scale = get_player_reaction_scale(player)
    enemy.hurt_reaction_timer = max(
        enemy.hurt_reaction_timer,
        enemy.hurt_reaction_duration + enemy.hurt_reaction_heavy_bonus * (reaction_scale - 1.0),
    )
    enemy.hurt_flash_timer = max(enemy.hurt_flash_timer, enemy.hurt_flash_duration * min(1.5, reaction_scale))
    enemy.reaction_recoil_timer = max(enemy.reaction_recoil_timer, 0.10 + (0.03 * (reaction_scale - 1.0)))
    enemy.reaction_recoil_offset = max(
        enemy.reaction_recoil_offset,
        int(enemy.reaction_recoil_pixels * reaction_scale),
    )

    if getattr(player, "is_counter_attacking", False) or getattr(player, "combo_step", 0) >= 3:
        enemy.stagger_emphasis_timer = max(enemy.stagger_emphasis_timer, enemy.stagger_emphasis_duration)


def begin_post_attack_recovery(enemy):
    """Mark the enemy as punishable after it fully commits to an attack."""
    enemy.punish_window_timer = max(enemy.punish_window_timer, enemy.punish_window_duration)
    enemy.recovery_flash_timer = max(enemy.recovery_flash_timer, enemy.recovery_flash_duration)
    enemy.reaction_recoil_timer = max(enemy.reaction_recoil_timer, 0.10)
    enemy.reaction_recoil_offset = max(enemy.reaction_recoil_offset, max(3, enemy.reaction_recoil_pixels // 2))


def begin_stagger_reaction(enemy):
    """Make staggered vulnerability read more clearly."""
    enemy.punish_window_timer = max(enemy.punish_window_timer, enemy.punish_window_duration + 0.05)
    enemy.recovery_flash_timer = max(enemy.recovery_flash_timer, enemy.recovery_flash_duration)
    enemy.stagger_emphasis_timer = max(enemy.stagger_emphasis_timer, enemy.stagger_emphasis_duration)
    enemy.reaction_recoil_timer = max(enemy.reaction_recoil_timer, 0.14)
    enemy.reaction_recoil_offset = max(enemy.reaction_recoil_offset, enemy.reaction_recoil_pixels)


def get_player_reaction_scale(player):
    """Return a light/heavy reaction scale from the player's current attack."""
    if getattr(player, "is_counter_attacking", False):
        return 1.85

    combo_step = getattr(player, "combo_step", 0)
    if combo_step >= 3:
        return 1.45
    if combo_step == 2:
        return 1.18
    return 1.0
