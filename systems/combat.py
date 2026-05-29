"""Combat helpers.

This module keeps hitbox, damage, knockback, and cooldown rules reusable so
main.py does not fill up with combat details as the game grows.
"""

import pygame

from settings import (
    ENEMY_COUNTER_STAGGER_DURATION,
    LIGHT_ATTACK_COMBO,
)


def create_attack_hitbox(player):
    """Create a sword hitbox in front of the player.

    The hitbox is a pygame.Rect that only matters during an active attack.
    It sits on the side the player is facing and lines up around the torso.
    """
    if player.facing == 1:
        x = player.rect.right
    else:
        x = player.rect.left - player.attack_range

    y = player.rect.centery - player.attack_height // 2
    return pygame.Rect(x, y, player.attack_range, player.attack_height)


def create_enemy_attack_hitbox(enemy):
    """Create the enemy melee hitbox in front of its facing direction."""
    if enemy.facing == 1:
        x = enemy.rect.right
    else:
        x = enemy.rect.left - enemy.attack_range

    y = enemy.rect.centery - enemy.attack_height // 2
    return pygame.Rect(x, y, enemy.attack_range, enemy.attack_height)


def get_combo_attack_data(combo_step):
    """Return damage, size, duration, and knockback values for one combo hit."""
    return LIGHT_ATTACK_COMBO[combo_step - 1]


def apply_damage(target, amount):
    """Reduce target health through its own damage method."""
    if hasattr(target, "take_damage"):
        return target.take_damage(amount)

    return False


def apply_knockback(target, direction, strength):
    """Push a target away from the attacker."""
    if hasattr(target, "knockback_velocity_x"):
        target.knockback_velocity_x = direction * strength


def process_player_attack(player, enemy):
    """Apply one light-attack hit if the player's active hitbox touches enemy."""
    if enemy.defeated:
        return

    attack_hitbox = player.get_attack_hitbox()

    if attack_hitbox is None or player.has_hit_this_attack:
        return

    if attack_hitbox.colliderect(enemy.rect):
        damage_applied = apply_damage(enemy, player.attack_damage)
        if damage_applied and hasattr(enemy, "register_attack_reaction"):
            enemy.register_attack_reaction(player)
        apply_knockback(enemy, player.facing, player.attack_knockback)
        if getattr(player, "is_counter_attacking", False):
            enemy.start_stagger(ENEMY_COUNTER_STAGGER_DURATION)
        player.has_hit_this_attack = True
        return player.get_attack_impact()

    return None


def process_player_attacks(player, enemies):
    """Apply the player's current attack to the first enemy it connects with."""
    for enemy in enemies:
        hit_result = process_player_attack(player, enemy)
        if hit_result:
            return hit_result

    return None


def process_enemy_attack(enemy, player):
    """Apply one enemy attack hit if its active hitbox touches the player."""
    if not enemy.is_attack_active() or enemy.has_hit_this_attack:
        return None

    attack_hitbox = create_enemy_attack_hitbox(enemy)

    if attack_hitbox.colliderect(player.rect):
        # Parry is the risky timing-based defense. It only works during the
        # small window opened by the first K press, but the reward is full
        # negation plus enemy stagger instead of only reduced damage.
        if hasattr(player, "can_parry_attack_from") and player.can_parry_attack_from(enemy.facing):
            enemy.has_hit_this_attack = True
            enemy.start_stagger()
            apply_knockback(enemy, player.facing, enemy.attack_knockback * 0.8)
            return player.parry_success(enemy.facing)

        # Blocking only helps against attacks from the front. It reduces damage,
        # but unlike a future parry system it does not create a counter window.
        if hasattr(player, "can_block_attack_from") and player.can_block_attack_from(enemy.facing):
            enemy.has_hit_this_attack = True
            return player.block_hit(enemy.attack_damage, enemy.facing)

        if not apply_damage(player, enemy.attack_damage):
            return None

        apply_knockback(player, enemy.facing, enemy.attack_knockback)
        enemy.has_hit_this_attack = True
        return {
            "hitstop": enemy.attack_hitstop,
            "shake_duration": enemy.attack_shake_duration,
            "shake_strength": enemy.attack_shake_strength,
        }

    return None


def process_enemy_attacks(enemies, player):
    """Collect impact results from every active enemy attack this frame."""
    hit_results = []

    for enemy in enemies:
        hit_result = process_enemy_attack(enemy, player)
        if hit_result:
            hit_results.append(hit_result)

    return hit_results


def can_use_action(cooldown_timer):
    """Return True when an action cooldown has finished."""
    return cooldown_timer <= 0


def start_cooldown():
    """Return the default attack cooldown duration."""
    return LIGHT_ATTACK_COMBO[0]["cooldown"]


def update_cooldown(cooldown_timer, dt):
    """Count an action cooldown down toward zero."""
    return max(0, cooldown_timer - dt)
