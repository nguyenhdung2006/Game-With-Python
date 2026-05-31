"""Mechanical room reward model and safe reward effects."""

from dataclasses import dataclass
from typing import Callable

from config.reward_config import (
    ATTACK_DAMAGE_UP_MULTIPLIER,
    DASH_COOLDOWN_DOWN_MULTIPLIER,
    MAX_DAMAGE_MULTIPLIER,
    MAX_HP_UP_BONUS,
    MIN_DASH_COOLDOWN,
    MIN_DASH_COOLDOWN_MULTIPLIER,
)


@dataclass(frozen=True)
class Reward:
    """One purely mechanical reward option."""

    reward_id: str
    display_name: str
    description: str
    apply: Callable


def create_reward_pool():
    """Return the current conservative mechanical reward pool."""
    return [
        Reward(
            "max_hp_up",
            "Max HP Up",
            f"+{MAX_HP_UP_BONUS} max HP. Heal {MAX_HP_UP_BONUS} HP now.",
            apply_max_hp_up,
        ),
        Reward(
            "attack_damage_up",
            "Attack Damage Up",
            f"+{round((ATTACK_DAMAGE_UP_MULTIPLIER - 1) * 100)}% player attack damage.",
            apply_attack_damage_up,
        ),
        Reward(
            "dash_cooldown_down",
            "Dash Cooldown Down",
            f"-{round((1 - DASH_COOLDOWN_DOWN_MULTIPLIER) * 100)}% dash cooldown.",
            apply_dash_cooldown_down,
        ),
    ]


def apply_max_hp_up(player):
    """Increase max HP slightly and heal the same amount."""
    bonus = MAX_HP_UP_BONUS
    player.max_health_bonus += bonus
    player.max_health += bonus
    player.health = min(player.max_health, player.health + bonus)


def apply_attack_damage_up(player):
    """Increase outgoing player attack damage with a conservative cap."""
    player.damage_multiplier = min(
        MAX_DAMAGE_MULTIPLIER,
        player.damage_multiplier * ATTACK_DAMAGE_UP_MULTIPLIER,
    )


def apply_dash_cooldown_down(player):
    """Reduce dash cooldown with a minimum clamp."""
    player.dash_cooldown_multiplier = max(
        MIN_DASH_COOLDOWN_MULTIPLIER,
        player.dash_cooldown_multiplier * DASH_COOLDOWN_DOWN_MULTIPLIER,
    )
    player.dash_cooldown = max(
        MIN_DASH_COOLDOWN,
        player.base_dash_cooldown * player.dash_cooldown_multiplier,
    )
