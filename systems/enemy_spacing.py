"""Lightweight multi-enemy spacing and flanking helpers."""

from settings import (
    ENEMY_FLANK_FAR_OFFSET,
    ENEMY_FLANK_NEAR_OFFSET,
    ENEMY_SPACING_MAX_STEP,
    ENEMY_SPACING_MIN_DISTANCE,
    ENEMY_SPACING_PULL_STRENGTH,
    ENEMY_SPACING_SEPARATION_FORCE,
    ENEMY_STATE_ATTACK,
    ENEMY_STATE_HURT,
    ENEMY_STATE_STAGGER,
    ENEMY_STATE_TELEGRAPH,
    WIDTH,
)


LOCKED_STATES = {
    ENEMY_STATE_ATTACK,
    ENEMY_STATE_TELEGRAPH,
    ENEMY_STATE_HURT,
    ENEMY_STATE_STAGGER,
}


def apply_enemy_spacing(enemies, player, leader_enemy, dt, wave_profile=None):
    """Spread enemies around the player using the current wave spacing profile."""
    alive_enemies = [enemy for enemy in enemies if not enemy.defeated]
    if len(alive_enemies) <= 1:
        return

    target_positions = build_flank_targets(alive_enemies, player, leader_enemy, wave_profile)

    for enemy in alive_enemies:
        if enemy is leader_enemy or enemy.state in LOCKED_STATES:
            continue

        target_x = target_positions.get(enemy)
        if target_x is None:
            continue

        move_enemy_toward_target(enemy, target_x, dt)

    apply_local_separation(alive_enemies, dt, wave_profile)


def build_flank_targets(enemies, player, leader_enemy, wave_profile=None):
    """Assign simple left/right spacing slots around the player."""
    non_leaders = [enemy for enemy in enemies if enemy is not leader_enemy]
    if not non_leaders:
        return {}

    player_x = player.rect.centerx
    near_offset = (
        wave_profile["flank_near_offset"]
        if wave_profile is not None
        else ENEMY_FLANK_NEAR_OFFSET
    )
    far_offset = (
        wave_profile["flank_far_offset"]
        if wave_profile is not None
        else ENEMY_FLANK_FAR_OFFSET
    )
    slot_offsets = [
        -near_offset,
        near_offset,
        -far_offset,
        far_offset,
    ]

    available_slots = [player_x + offset for offset in slot_offsets[: len(non_leaders)]]
    targets = {}

    # Greedy matching minimizes unnecessary crossing while still distributing
    # enemies to both sides of the player.
    for enemy in sorted(non_leaders, key=lambda item: item.rect.centerx):
        best_slot = min(available_slots, key=lambda slot_x: abs(slot_x - enemy.rect.centerx))
        targets[enemy] = clamp_target_x(best_slot, enemy.width)
        available_slots.remove(best_slot)

    return targets


def move_enemy_toward_target(enemy, target_center_x, dt):
    """Nudge a non-leading enemy toward its assigned flank slot."""
    delta = target_center_x - enemy.rect.centerx
    if abs(delta) < 10:
        return

    step = max(
        -ENEMY_SPACING_MAX_STEP * dt,
        min(ENEMY_SPACING_MAX_STEP * dt, delta * ENEMY_SPACING_PULL_STRENGTH * dt),
    )
    enemy.x += step
    enemy.x = max(0, min(WIDTH - enemy.width, enemy.x))
    enemy.rect.x = round(enemy.x)


def apply_local_separation(enemies, dt, wave_profile=None):
    """Push nearby enemies apart horizontally so they do not blob together."""
    spacing_min_distance = (
        wave_profile["spacing_min_distance"]
        if wave_profile is not None
        else ENEMY_SPACING_MIN_DISTANCE
    )
    for index, left_enemy in enumerate(enemies):
        for right_enemy in enemies[index + 1 :]:
            if left_enemy.state in LOCKED_STATES and right_enemy.state in LOCKED_STATES:
                continue

            distance = right_enemy.rect.centerx - left_enemy.rect.centerx
            if distance == 0:
                distance = 1

            if abs(distance) >= spacing_min_distance:
                continue

            overlap = spacing_min_distance - abs(distance)
            push = min(
                ENEMY_SPACING_MAX_STEP * dt * 0.7,
                overlap * ENEMY_SPACING_SEPARATION_FORCE * dt,
            )
            direction = 1 if distance > 0 else -1

            if left_enemy.state not in LOCKED_STATES:
                left_enemy.x -= direction * (push * 0.5)
                left_enemy.x = max(0, min(WIDTH - left_enemy.width, left_enemy.x))
                left_enemy.rect.x = round(left_enemy.x)

            if right_enemy.state not in LOCKED_STATES:
                right_enemy.x += direction * (push * 0.5)
                right_enemy.x = max(0, min(WIDTH - right_enemy.width, right_enemy.x))
                right_enemy.rect.x = round(right_enemy.x)


def clamp_target_x(target_center_x, enemy_width):
    """Keep desired spacing targets fully inside the screen."""
    half_width = enemy_width // 2
    return max(half_width, min(WIDTH - half_width, target_center_x))
