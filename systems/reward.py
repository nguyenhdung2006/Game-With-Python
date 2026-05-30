"""Mechanical room reward model and safe reward effects."""

from dataclasses import dataclass
from typing import Callable


MAX_DAMAGE_MULTIPLIER = 1.6
MIN_DASH_COOLDOWN_MULTIPLIER = 0.55
MIN_DASH_COOLDOWN = 0.25


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
            "+10 max HP. Heal 10 HP now.",
            apply_max_hp_up,
        ),
        Reward(
            "attack_damage_up",
            "Attack Damage Up",
            "+10% player attack damage.",
            apply_attack_damage_up,
        ),
        Reward(
            "dash_cooldown_down",
            "Dash Cooldown Down",
            "-10% dash cooldown.",
            apply_dash_cooldown_down,
        ),
    ]


def apply_max_hp_up(player):
    """Increase max HP slightly and heal the same amount."""
    bonus = 10
    player.max_health_bonus += bonus
    player.max_health += bonus
    player.health = min(player.max_health, player.health + bonus)


def apply_attack_damage_up(player):
    """Increase outgoing player attack damage with a conservative cap."""
    player.damage_multiplier = min(MAX_DAMAGE_MULTIPLIER, player.damage_multiplier * 1.10)


def apply_dash_cooldown_down(player):
    """Reduce dash cooldown with a minimum clamp."""
    player.dash_cooldown_multiplier = max(
        MIN_DASH_COOLDOWN_MULTIPLIER,
        player.dash_cooldown_multiplier * 0.90,
    )
    player.dash_cooldown = max(
        MIN_DASH_COOLDOWN,
        player.base_dash_cooldown * player.dash_cooldown_multiplier,
    )
