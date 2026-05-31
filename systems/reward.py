"""Mechanical room reward model and safe reward effects."""

from dataclasses import dataclass
from typing import Callable

from config.reward_config import (
    MAX_COMBO_FINISHER_DAMAGE_MULTIPLIER,
    MAX_DAMAGE_MULTIPLIER,
    MAX_DASH_SPEED_MULTIPLIER,
    MAX_MOVE_SPEED_MULTIPLIER,
    MAX_SKILL_DAMAGE_MULTIPLIER,
    MIN_DAMAGE_TAKEN_MULTIPLIER,
    MIN_DASH_COOLDOWN,
    MIN_DASH_COOLDOWN_MULTIPLIER,
    MIN_SKILL_COOLDOWN_MULTIPLIER,
    REWARD_DEFINITIONS,
)


@dataclass(frozen=True)
class Reward:
    """One purely mechanical reward option."""

    reward_id: str
    display_name: str
    description: str
    category: str
    value: float
    max_stacks: int | None
    apply: Callable


def create_reward_pool():
    """Build the current mechanical reward pool from config definitions."""
    return [
        Reward(
            reward_id=definition["id"],
            display_name=definition["display_name"],
            description=definition["description"],
            category=definition["category"],
            value=definition["value"],
            max_stacks=definition["max_stacks"],
            apply=REWARD_EFFECTS[definition["effect_id"]],
        )
        for definition in REWARD_DEFINITIONS
    ]


def apply_max_hp_up(player, value):
    """Increase max HP slightly and heal the same amount."""
    player.max_health_bonus += value
    player.max_health += value
    heal_player(player, value)


def apply_attack_damage_up(player, value):
    """Increase outgoing player attack damage with a conservative cap."""
    player.damage_multiplier = min(MAX_DAMAGE_MULTIPLIER, player.damage_multiplier * value)


def apply_skill_damage_up(player, value):
    """Increase skill damage without changing melee damage."""
    player.skill_damage_multiplier = min(
        MAX_SKILL_DAMAGE_MULTIPLIER,
        player.skill_damage_multiplier * value,
    )


def apply_combo_finisher_damage_up(player, value):
    """Increase the third normal combo hit without changing other attacks."""
    player.combo_finisher_damage_multiplier = min(
        MAX_COMBO_FINISHER_DAMAGE_MULTIPLIER,
        player.combo_finisher_damage_multiplier * value,
    )


def apply_damage_taken_down(player, value):
    """Reduce incoming damage with a conservative minimum clamp."""
    player.damage_taken_multiplier = max(
        MIN_DAMAGE_TAKEN_MULTIPLIER,
        player.damage_taken_multiplier * value,
    )


def apply_dash_cooldown_down(player, value):
    """Reduce dash cooldown with a minimum clamp."""
    player.dash_cooldown_multiplier = max(
        MIN_DASH_COOLDOWN_MULTIPLIER,
        player.dash_cooldown_multiplier * value,
    )
    player.dash_cooldown = max(
        MIN_DASH_COOLDOWN,
        player.base_dash_cooldown * player.dash_cooldown_multiplier,
    )


def apply_dash_distance_up(player, value):
    """Increase dash speed slightly while preserving dash timing."""
    player.dash_speed_multiplier = min(
        MAX_DASH_SPEED_MULTIPLIER,
        player.dash_speed_multiplier * value,
    )
    player.dash_speed = player.base_dash_speed * player.dash_speed_multiplier


def apply_move_speed_up(player, value):
    """Increase normal movement speed with a conservative cap."""
    player.move_speed_multiplier = min(
        MAX_MOVE_SPEED_MULTIPLIER,
        player.move_speed_multiplier * value,
    )
    player.speed = player.base_move_speed * player.move_speed_multiplier


def apply_skill_cooldown_down(player, value):
    """Reduce future player skill cooldowns with a minimum clamp."""
    player.skill_cooldown_multiplier = max(
        MIN_SKILL_COOLDOWN_MULTIPLIER,
        player.skill_cooldown_multiplier * value,
    )


def apply_heal_after_room_clear(player, value):
    """Increase the automatic mechanical heal after future room clears."""
    player.room_clear_heal += value


def apply_small_heal_now(player, value):
    """Heal the player immediately without changing max HP."""
    heal_player(player, value)


def heal_player(player, amount):
    """Restore health without exceeding the current max-health value."""
    player.health = min(player.max_health, player.health + amount)


REWARD_EFFECTS = {
    "attack_damage_up": apply_attack_damage_up,
    "skill_damage_up": apply_skill_damage_up,
    "combo_finisher_damage_up": apply_combo_finisher_damage_up,
    "max_hp_up": apply_max_hp_up,
    "damage_taken_down": apply_damage_taken_down,
    "dash_cooldown_down": apply_dash_cooldown_down,
    "dash_distance_up": apply_dash_distance_up,
    "move_speed_up": apply_move_speed_up,
    "skill_cooldown_down": apply_skill_cooldown_down,
    "heal_after_room_clear": apply_heal_after_room_clear,
    "small_heal_now": apply_small_heal_now,
}
