"""Print a lightweight balance snapshot and conservative diagnostics."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.boss_config import BOSS_SKILL_CONFIG, ELITE_ENEMY_CONFIG, SOLO_BOSS_COMBO_CONFIG
from config.enemy_config import (
    BASIC_ENEMY_CONFIG,
    FAST_ENEMY_CONFIG,
    ORC_LEVEL_2_ENEMY_CONFIG,
    ORC_LEVEL_3_ENEMY_CONFIG,
    SLIME_ENEMY_CONFIG,
)
from config.player_config import (
    KICK_ATTACK_COMBO,
    LIGHT_ATTACK_COMBO,
    PLAYER_MAX_HEALTH,
    SUPER_SAIYAN_DAMAGE_MULTIPLIER,
    SUPER_SAIYAN_DURATION,
    SUPER_SAIYAN_MAX_ENERGY,
)
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
from config.skill_config import ENERGY_DISC_CONFIG, KAMEHAMEHA_CONFIG, KI_BLAST_CONFIG


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
    if SOLO_BOSS_COMBO_CONFIG["final_skill"]["energy_cost"] > SOLO_BOSS_COMBO_CONFIG["max_energy"]:
        warnings.append("Solo boss final skill costs more energy than the boss can store")
    if SOLO_BOSS_COMBO_CONFIG["final_lockout"] < 8.0:
        warnings.append("Solo boss final skill lockout may allow repeated high-threat combos")
    if SOLO_BOSS_COMBO_CONFIG["final_skill"]["recovery_duration"] < 1.0:
        warnings.append("Solo boss final skill recovery may be too short to punish")
    if SOLO_BOSS_COMBO_CONFIG["skill_lock_duration"] > 3.0:
        warnings.append("Solo player skill-lock duration may feel oppressive")
    if SUPER_SAIYAN_DAMAGE_MULTIPLIER > 2.5:
        warnings.append(f"Super Saiyan damage burst may be excessive: x{SUPER_SAIYAN_DAMAGE_MULTIPLIER:.2f}")
    if SUPER_SAIYAN_DURATION > 12:
        warnings.append(f"Super Saiyan duration may dominate combat pacing: {SUPER_SAIYAN_DURATION:.2f}s")

    for label, skill in (
        ("Ki Blast", KI_BLAST_CONFIG),
        ("Kamehameha", KAMEHAMEHA_CONFIG),
        ("Energy Disc", ENERGY_DISC_CONFIG),
    ):
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
    print(f"Punch combo damage: {[hit['damage'] for hit in LIGHT_ATTACK_COMBO]}")
    print(f"Kick combo damage: {[hit['damage'] for hit in KICK_ATTACK_COMBO]}")
    print(
        f"Super Saiyan: {SUPER_SAIYAN_MAX_ENERGY} gauge, "
        f"x{SUPER_SAIYAN_DAMAGE_MULTIPLIER:.2f} outgoing damage, {SUPER_SAIYAN_DURATION:.2f}s burst"
    )

    print_section("Enemies")
    for enemy in (
        BASIC_ENEMY_CONFIG,
        FAST_ENEMY_CONFIG,
        SLIME_ENEMY_CONFIG,
        ORC_LEVEL_2_ENEMY_CONFIG,
        ORC_LEVEL_3_ENEMY_CONFIG,
    ):
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
    print(f"Energy Disc: damage {ENERGY_DISC_CONFIG['damage']}, cooldown {ENERGY_DISC_CONFIG['cooldown']:.2f}s")

    print_section("Solo Boss Combo Skills")
    base_damage = SOLO_BOSS_COMBO_CONFIG["base_hit_damage"]
    for skill_id in ("skill_1", "skill_2", "final_skill"):
        skill = SOLO_BOSS_COMBO_CONFIG[skill_id]
        damage = [base_damage[index % 3] * skill["damage_multiplier"] for index, _ in enumerate(skill["frames"])]
        print(
            f"{skill_id}: frames {skill['frames']}, damage {damage}, energy cost {skill['energy_cost']}, "
            f"telegraph {skill['telegraph_duration']:.2f}s, recovery {skill['recovery_duration']:.2f}s"
        )
    print(
        f"Anti-spam: major spacing {SOLO_BOSS_COMBO_CONFIG['major_skill_spacing']:.2f}s, "
        f"final lockout {SOLO_BOSS_COMBO_CONFIG['final_lockout']:.2f}s, "
        f"final prior skills {SOLO_BOSS_COMBO_CONFIG['final_min_prior_skills']}"
    )
    print(
        f"Player control effects: stun {SOLO_BOSS_COMBO_CONFIG['stun_duration']:.2f}s, "
        f"skill lock {SOLO_BOSS_COMBO_CONFIG['skill_lock_duration']:.2f}s"
    )

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
