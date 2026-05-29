"""Base enemy AI, combat-state, and damage helpers."""

from entities.enemy_parts.reaction import (
    begin_post_attack_recovery,
    begin_stagger_reaction,
    register_player_hit,
    update_reaction_timers,
)
from settings import (
    ENEMY_STATE_ATTACK,
    ENEMY_STATE_CHASE,
    ENEMY_STATE_DEFEATED,
    ENEMY_STATE_HURT,
    ENEMY_STATE_IDLE,
    ENEMY_STATE_STAGGER,
    ENEMY_STATE_TELEGRAPH,
    WIDTH,
)
from systems.physics import clamp_x_to_screen, move_toward_zero


def update(enemy, player, dt, allow_attack=True):
    """Run the shared melee enemy state machine.

    allow_attack lets encounter logic throttle how many enemies try to
    start attacks at once. That keeps multi-enemy fights readable.
    """
    update_timers(enemy, dt)

    if update_entrance(enemy, dt):
        return

    if enemy.defeated:
        enemy.state = ENEMY_STATE_DEFEATED
        enemy.knockback_velocity_x = 0
        return

    if enemy.hurt_reaction_timer > 0:
        enemy.state = ENEMY_STATE_HURT
        update_knockback(enemy, dt)
        return

    if enemy.stagger_timer > 0:
        # Stagger is short, readable vulnerability. Archetypes can tune the
        # duration to feel more or less punishable.
        enemy.state = ENEMY_STATE_STAGGER
        update_knockback(enemy, dt)
        return

    face_player(enemy, player)

    if enemy.retreat_timer > 0:
        update_retreat(enemy, dt)
    elif enemy.recovery_timer > 0:
        update_recovery(enemy, dt)
    elif enemy.state == ENEMY_STATE_TELEGRAPH:
        update_telegraph(enemy, dt)
    elif enemy.state == ENEMY_STATE_ATTACK:
        update_attack(enemy, dt)
    else:
        update_idle_or_chase(enemy, player, dt, allow_attack)

    update_knockback(enemy, dt)


def update_timers(enemy, dt):
    """Count down the shared state timers."""
    if enemy.attack_cooldown_timer > 0:
        enemy.attack_cooldown_timer = max(0, enemy.attack_cooldown_timer - dt)

    if enemy.hurt_flash_timer > 0:
        enemy.hurt_flash_timer = max(0, enemy.hurt_flash_timer - dt)

    if enemy.retreat_timer > 0:
        enemy.retreat_timer = max(0, enemy.retreat_timer - dt)

    if enemy.recovery_timer > 0:
        enemy.recovery_timer = max(0, enemy.recovery_timer - dt)

    if enemy.stagger_timer > 0:
        was_active = enemy.stagger_timer > 0
        enemy.stagger_timer = max(0, enemy.stagger_timer - dt)
        if was_active and enemy.stagger_timer == 0:
            enemy.recovery_timer = max(enemy.recovery_timer, enemy.post_stagger_recovery_duration)
            enemy.recovery_flash_timer = max(enemy.recovery_flash_timer, enemy.recovery_flash_duration * 0.75)

    if enemy.pressure_indicator_timer > 0:
        enemy.pressure_indicator_timer = max(0, enemy.pressure_indicator_timer - dt)

    if enemy.aggression_focus_timer > 0:
        enemy.aggression_focus_timer = max(0, enemy.aggression_focus_timer - dt)

    update_reaction_timers(enemy, dt)


def update_entrance(enemy, dt):
    """Handle a lightweight staged entrance before full aggression starts."""
    if enemy.entrance_delay_timer > 0:
        enemy.entrance_delay_timer = max(0, enemy.entrance_delay_timer - dt)
        update_spawn_slide(enemy, dt)
        return True

    if enemy.entrance_pause_timer > 0:
        enemy.entrance_pause_timer = max(0, enemy.entrance_pause_timer - dt)
        update_spawn_slide(enemy, dt)
        return True

    if enemy.rect.x != round(enemy.spawn_target_x):
        update_spawn_slide(enemy, dt)

    return False


def update_spawn_slide(enemy, dt):
    """Slide the enemy toward its staged spawn position."""
    delta = enemy.spawn_target_x - enemy.x
    if abs(delta) < 2:
        enemy.x = float(enemy.spawn_target_x)
        enemy.rect.x = round(enemy.x)
        return

    step = enemy.entrance_move_speed * dt
    if delta > 0:
        enemy.x = min(enemy.spawn_target_x, enemy.x + step)
    else:
        enemy.x = max(enemy.spawn_target_x, enemy.x - step)
    enemy.rect.x = round(enemy.x)


def update_knockback(enemy, dt):
    """Move the enemy while knockback is still active."""
    if enemy.knockback_velocity_x == 0:
        return

    enemy.x += enemy.knockback_velocity_x * dt
    enemy.x = clamp_x_to_screen(enemy.x, enemy.width, WIDTH)
    enemy.knockback_velocity_x = move_toward_zero(
        enemy.knockback_velocity_x,
        enemy.knockback_friction * dt,
    )
    enemy.rect.x = round(enemy.x)


def face_player(enemy, player):
    """Turn toward the player before chasing or attacking."""
    if player.rect.centerx >= enemy.rect.centerx:
        enemy.facing = 1
    else:
        enemy.facing = -1


def update_idle_or_chase(enemy, player, dt, allow_attack=True):
    """Chase while far away, or telegraph when close enough to attack."""
    distance_to_player = abs(player.rect.centerx - enemy.rect.centerx)

    if distance_to_player > enemy.attack_start_distance:
        enemy.state = ENEMY_STATE_CHASE
        enemy.x += enemy.facing * enemy.chase_speed * dt
        enemy.x = clamp_x_to_screen(enemy.x, enemy.width, WIDTH)
        enemy.rect.x = round(enemy.x)
        return

    enemy.state = ENEMY_STATE_IDLE

    if enemy.attack_cooldown_timer <= 0 and allow_attack:
        start_telegraph(enemy)


def update_retreat(enemy, dt):
    """Step away after attacking so enemies do not just face-hug forever."""
    enemy.state = ENEMY_STATE_IDLE
    enemy.x -= enemy.facing * enemy.retreat_speed * dt
    enemy.x = clamp_x_to_screen(enemy.x, enemy.width, WIDTH)
    enemy.rect.x = round(enemy.x)


def update_recovery(enemy, dt):
    """Pause briefly after an attack before restarting pressure."""
    enemy.state = ENEMY_STATE_IDLE


def start_telegraph(enemy):
    """Begin the readable warning before the enemy strike."""
    enemy.state = ENEMY_STATE_TELEGRAPH
    enemy.telegraph_timer = enemy.telegraph_duration


def update_telegraph(enemy, dt):
    """Wait through the telegraph, then start the attack."""
    enemy.telegraph_timer -= dt

    if enemy.telegraph_timer <= 0:
        start_attack(enemy)


def start_attack(enemy):
    """Open the active attack window."""
    enemy.state = ENEMY_STATE_ATTACK
    enemy.attack_timer = enemy.attack_duration
    enemy.attack_cooldown_timer = enemy.attack_cooldown
    enemy.has_hit_this_attack = False


def update_attack(enemy, dt):
    """Close the active attack window and move to retreat."""
    enemy.attack_timer -= dt

    if enemy.attack_timer <= 0:
        start_retreat(enemy)


def start_retreat(enemy):
    """Create spacing after an attack instead of constant contact."""
    enemy.state = ENEMY_STATE_IDLE
    enemy.attack_timer = 0
    enemy.retreat_timer = enemy.retreat_duration
    enemy.recovery_timer = enemy.recovery_duration
    begin_post_attack_recovery(enemy)


def start_stagger(enemy, duration=None):
    """Interrupt the current action and leave the enemy briefly vulnerable."""
    if enemy.defeated:
        return

    if duration is None:
        duration = enemy.stagger_duration

    enemy.state = ENEMY_STATE_STAGGER
    enemy.telegraph_timer = 0
    enemy.attack_timer = 0
    enemy.retreat_timer = 0
    enemy.recovery_timer = 0
    enemy.has_hit_this_attack = True
    enemy.stagger_timer = duration
    begin_stagger_reaction(enemy)


def is_attack_active(enemy):
    """Return True while the enemy attack hitbox should be dangerous."""
    return enemy.state == ENEMY_STATE_ATTACK and enemy.attack_timer > 0


def take_damage(enemy, amount, knockback_x=0):
    """Receive damage while keeping health above zero."""
    if enemy.defeated:
        return

    enemy.health = max(0, enemy.health - amount)
    enemy.hurt_flash_timer = enemy.hurt_flash_duration
    enemy.knockback_velocity_x = knockback_x
    enemy.state = ENEMY_STATE_HURT
    enemy.telegraph_timer = 0
    enemy.attack_timer = 0
    enemy.retreat_timer = 0
    enemy.recovery_timer = 0
    enemy.stagger_timer = 0
    enemy.has_hit_this_attack = False

    if enemy.health == 0:
        enemy.defeated = True
        enemy.state = ENEMY_STATE_DEFEATED

    return True


def register_attack_reaction(enemy, player):
    """Expose player-hit reaction registration through the enemy parts layer."""
    register_player_hit(enemy, player)
