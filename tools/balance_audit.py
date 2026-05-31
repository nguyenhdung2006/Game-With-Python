"""Print a lightweight balance snapshot and conservative diagnostics."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.boss_config import BOSS_SKILL_CONFIG, ELITE_ENEMY_CONFIG
from config.enemy_config import BASIC_ENEMY_CONFIG, FAST_ENEMY_CONFIG
from config.player_config import LIGHT_ATTACK_COMBO, PLAYER_MAX_HEALTH
from config.reward_config import (
    MAX_COMBO_FINISHER_DAMAGE_MULTIPLIER,
    MAX_DAMAGE_MULTIPLIER,
    MAX_DASH_SPEED_MULTIPLIER,
    MAX_MOVE_SPEED_MULTIPLIER,
    MAX_SKILL_DAMAGE_MULTIPLIER,
    MIN_DAMAGE_TAKEN_MULTIPLIER,
    MIN_DASH_COOLDOWN_MULTIPLIER,
    MIN_SKILL_COOLDOWN_MULTIPLIER,
    REWARD_DEFINITIONS,
)
from config.skill_config import KAMEHAMEHA_CONFIG, KI_BLAST_CONFIG


def print_section(title):
    """Print one readable report heading."""
    print(f"\n== {title} ==")


def collect_warnings():
    """Return diagnostics for values worth reviewing before final balance."""
    warnings = []
    if MAX_DAMAGE_MULTIPLIER > 2.0:
        warnings.append(f"Player damage multiplier cap is high: x{MAX_DAMAGE_MULTIPLIER:.2f}")
    if MIN_DASH_COOLDOWN_MULTIPLIER < 0.50:
        warnings.append(f"Dash cooldown multiplier minimum is aggressive: x{MIN_DASH_COOLDOWN_MULTIPLIER:.2f}")
    if MIN_SKILL_COOLDOWN_MULTIPLIER < 0.60:
        warnings.append(f"Skill cooldown multiplier minimum is aggressive: x{MIN_SKILL_COOLDOWN_MULTIPLIER:.2f}")
    if MIN_DAMAGE_TAKEN_MULTIPLIER < 0.60:
        warnings.append(f"Damage-taken multiplier minimum is aggressive: x{MIN_DAMAGE_TAKEN_MULTIPLIER:.2f}")
    if MAX_DASH_SPEED_MULTIPLIER > 1.50:
        warnings.append(f"Dash-distance cap may reduce arena readability: x{MAX_DASH_SPEED_MULTIPLIER:.2f}")
    if MAX_MOVE_SPEED_MULTIPLIER > 1.40:
        warnings.append(f"Move-speed cap may reduce arena readability: x{MAX_MOVE_SPEED_MULTIPLIER:.2f}")
    if BOSS_SKILL_CONFIG["skill_range"] > 320:
        warnings.append(f"Boss skill range may be difficult to avoid: {BOSS_SKILL_CONFIG['skill_range']}")
    if BOSS_SKILL_CONFIG["damage"] >= PLAYER_MAX_HEALTH * 0.40:
        warnings.append(f"Boss skill damage is high relative to player HP: {BOSS_SKILL_CONFIG['damage']}")

    for label, skill in (("Ki Blast", KI_BLAST_CONFIG), ("Kamehameha", KAMEHAMEHA_CONFIG)):
        if skill["damage"] >= ELITE_ENEMY_CONFIG["max_health"] * 0.35:
            warnings.append(f"{label} damage is high relative to elite HP: {skill['damage']}")
    for reward in REWARD_DEFINITIONS:
        if reward["max_stacks"] is None:
            warnings.append(f"Reward has no stack cap: {reward['display_name']}")
    return warnings


def run():
    """Print current tuning and conservative warning diagnostics."""
    print("Gameplay Balance Audit")
    print("Prototype snapshot only. Final balance and fantasy identity require later review.")

    print_section("Player")
    print(f"HP: {PLAYER_MAX_HEALTH}")
    print(f"Combo damage: {[hit['damage'] for hit in LIGHT_ATTACK_COMBO]}")

    print_section("Enemies")
    for enemy in (BASIC_ENEMY_CONFIG, FAST_ENEMY_CONFIG):
        print(f"{enemy['label']}: HP {enemy['max_health']}, damage {enemy['attack_damage']}, range {enemy['attack_range']}")

    print_section("Elite / Boss Placeholder")
    print(
        f"HP: {ELITE_ENEMY_CONFIG['max_health']}, melee damage: {ELITE_ENEMY_CONFIG['attack_damage']}, "
        f"skill damage: {BOSS_SKILL_CONFIG['damage']}, skill cooldown: {BOSS_SKILL_CONFIG['cooldown']:.2f}s, "
        f"skill range: {BOSS_SKILL_CONFIG['skill_range']}"
    )

    print_section("Player Skills")
    print(f"Ki Blast: damage {KI_BLAST_CONFIG['damage']}, cooldown {KI_BLAST_CONFIG['cooldown']:.2f}s")
    print(f"Kamehameha: damage {KAMEHAMEHA_CONFIG['damage']}, cooldown {KAMEHAMEHA_CONFIG['cooldown']:.2f}s")

    print_section("Reward Caps")
    print(f"Damage: x{MAX_DAMAGE_MULTIPLIER:.2f}")
    print(f"Skill damage: x{MAX_SKILL_DAMAGE_MULTIPLIER:.2f}")
    print(f"Combo finisher: x{MAX_COMBO_FINISHER_DAMAGE_MULTIPLIER:.2f}")
    print(f"Damage taken minimum: x{MIN_DAMAGE_TAKEN_MULTIPLIER:.2f}")
    print(f"Dash cooldown minimum: x{MIN_DASH_COOLDOWN_MULTIPLIER:.2f}")
    print(f"Skill cooldown minimum: x{MIN_SKILL_COOLDOWN_MULTIPLIER:.2f}")
    print(f"Dash distance: x{MAX_DASH_SPEED_MULTIPLIER:.2f}")
    print(f"Move speed: x{MAX_MOVE_SPEED_MULTIPLIER:.2f}")

    print_section("Reward Definitions")
    for reward in REWARD_DEFINITIONS:
        stack_label = "uncapped" if reward["max_stacks"] is None else str(reward["max_stacks"])
        print(f"{reward['category']:>8} | {reward['display_name']} | value {reward['value']} | stacks {stack_label}")

    warnings = collect_warnings()
    print_section("Warnings")
    if warnings:
        for warning in warnings:
            print(f"[WARN] {warning}")
    else:
        print("[OK] No extreme prototype values detected")
    print(f"\nAudit complete: {len(warnings)} warning(s)")


if __name__ == "__main__":
    run()
