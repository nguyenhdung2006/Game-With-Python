"""Lightweight standalone regression checks for gameplay foundations."""

from pathlib import Path
import os
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from config.boss_config import BOSS_SKILL_CONFIG, ELITE_ENEMY_CONFIG
from config.dungeon_layout_config import (
    DUNGEON_CLEAR_LAYOUT,
    DUNGEON_ROOM_LAYOUTS,
    LAYOUT_CLEAR,
    LAYOUT_ELITE_BOSS,
    LAYOUT_ENCOUNTER,
    LAYOUT_START,
)
from config.enemy_config import BASIC_ENEMY_CONFIG, FAST_ENEMY_CONFIG
from config.player_config import DASH_COOLDOWN, DASH_SPEED, PLAYER_MAX_HEALTH, PLAYER_SPEED
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
from config.skill_config import KAMEHAMEHA_CONFIG, KI_BLAST_CONFIG
from entities.basic_enemy import BasicEnemy
from entities.elite_enemy import EliteEnemy
from entities.player import Player
from managers.dungeon_layout import DungeonLayoutManager
from managers.room_state import ROOM_ACTIVE, ROOM_CLEARED, ROOM_REWARD
from modes.dungeon_mode import DungeonMode
from modes.solo_mode import SOLO_ACTIVE, SOLO_VICTORY, SoloMode
from settings import GROUND_Y, HEIGHT, PLAYER_HEIGHT, WIDTH
from systems.beam import Beam
from systems.boss_skill_controller import (
    BOSS_SKILL_ACTIVE,
    BOSS_SKILL_READY,
    BOSS_SKILL_RECOVERY,
    BOSS_SKILL_TELEGRAPH,
)
from systems.projectile import Projectile
from systems.projectile_manager import ProjectileManager
from systems.reward import REWARD_EFFECTS, create_reward_pool
from systems.reward_manager import RewardManager
from systems.skill_manager import SkillManager


def check(condition, message):
    """Raise a readable assertion when one smoke expectation fails."""
    if not condition:
        raise AssertionError(message)


def create_player(x=180):
    """Return a grounded player for mechanical checks."""
    return Player(x, GROUND_Y - PLAYER_HEIGHT)


def check_config_values():
    """Validate required config values and definition shapes."""
    check(PLAYER_MAX_HEALTH > 0, "Player max HP must be positive")
    check(PLAYER_SPEED > 0, "Player move speed must be positive")
    check(DASH_SPEED > PLAYER_SPEED, "Dash speed must exceed normal move speed")
    check(DASH_COOLDOWN > 0, "Dash cooldown must be positive")

    required_enemy_fields = {
        "max_health",
        "chase_speed",
        "attack_damage",
        "attack_range",
        "telegraph_duration",
        "attack_duration",
        "attack_cooldown",
        "recovery_duration",
    }
    for label, enemy_config in (
        ("basic enemy", BASIC_ENEMY_CONFIG),
        ("fast enemy", FAST_ENEMY_CONFIG),
        ("elite enemy", ELITE_ENEMY_CONFIG),
    ):
        check(required_enemy_fields <= enemy_config.keys(), f"{label} config is incomplete")
        check(enemy_config["max_health"] > 0, f"{label} HP must be positive")
        check(enemy_config["chase_speed"] > 0, f"{label} chase speed must be positive")
        check(enemy_config["attack_damage"] > 0, f"{label} damage must be positive")
        check(enemy_config["attack_range"] > 0, f"{label} range must be positive")
        check(enemy_config["telegraph_duration"] > 0, f"{label} telegraph must be readable")
        check(enemy_config["attack_cooldown"] > 0, f"{label} cooldown must be positive")

    required_ki_blast_fields = {"damage", "cooldown", "speed", "lifetime", "width", "height"}
    check(required_ki_blast_fields <= KI_BLAST_CONFIG.keys(), "Ki Blast config is incomplete")
    for field in required_ki_blast_fields:
        check(KI_BLAST_CONFIG[field] > 0, f"Ki Blast {field} must be positive")

    required_kamehameha_fields = {"damage", "cooldown", "range", "height", "duration"}
    check(required_kamehameha_fields <= KAMEHAMEHA_CONFIG.keys(), "Kamehameha config is incomplete")
    for field in required_kamehameha_fields:
        check(KAMEHAMEHA_CONFIG[field] > 0, f"Kamehameha {field} must be positive")

    check(BOSS_SKILL_CONFIG["cooldown"] > 0, "Boss skill cooldown must be positive")
    check(BOSS_SKILL_CONFIG["telegraph_duration"] > 0, "Boss skill telegraph must be readable")
    check(BOSS_SKILL_CONFIG["active_duration"] > 0, "Boss skill active duration must be positive")
    check(BOSS_SKILL_CONFIG["recovery_duration"] > 0, "Boss skill recovery must be positive")
    check(BOSS_SKILL_CONFIG["skill_range"] > 0, "Boss skill range must be positive")
    check(BOSS_SKILL_CONFIG["damage"] > 0, "Boss skill damage must be positive")


def check_reward_definitions():
    """Validate reward data, unique ids, categories, stacks, and clamps."""
    required_fields = {
        "id",
        "display_name",
        "description",
        "category",
        "value",
        "max_stacks",
        "effect_id",
    }
    valid_categories = {"offense", "defense", "mobility", "resource", "utility"}
    reward_ids = set()
    for definition in REWARD_DEFINITIONS:
        check(required_fields <= definition.keys(), f"Reward definition is incomplete: {definition}")
        check(definition["id"] not in reward_ids, f"Duplicate reward id: {definition['id']}")
        check(definition["category"] in valid_categories, f"Invalid reward category: {definition['category']}")
        check(definition["value"] > 0, f"Reward value must be positive: {definition['id']}")
        check(definition["effect_id"] in REWARD_EFFECTS, f"Missing reward effect: {definition['effect_id']}")
        check(
            definition["max_stacks"] is None or definition["max_stacks"] > 0,
            f"Invalid max stacks: {definition['id']}",
        )
        reward_ids.add(definition["id"])

    check(
        {definition["category"] for definition in REWARD_DEFINITIONS} == valid_categories,
        "Reward definitions must represent every mechanical category",
    )
    check(len(create_reward_pool()) == len(REWARD_DEFINITIONS), "Reward pool does not match config definitions")
    check(0 < MIN_DASH_COOLDOWN_MULTIPLIER <= 1, "Dash cooldown minimum multiplier is unsafe")
    check(MIN_DASH_COOLDOWN > 0, "Dash cooldown minimum is unsafe")
    check(0 < MIN_DAMAGE_TAKEN_MULTIPLIER <= 1, "Damage taken minimum multiplier is unsafe")
    check(0 < MIN_SKILL_COOLDOWN_MULTIPLIER <= 1, "Skill cooldown minimum multiplier is unsafe")
    check(MAX_DAMAGE_MULTIPLIER >= 1, "Damage multiplier cap must preserve baseline")
    check(MAX_SKILL_DAMAGE_MULTIPLIER >= 1, "Skill damage cap must preserve baseline")
    check(MAX_COMBO_FINISHER_DAMAGE_MULTIPLIER >= 1, "Finisher cap must preserve baseline")
    check(MAX_DASH_SPEED_MULTIPLIER >= 1, "Dash speed cap must preserve baseline")
    check(MAX_MOVE_SPEED_MULTIPLIER >= 1, "Move speed cap must preserve baseline")


def check_layout_definitions():
    """Validate the fixed Dungeon layout catalog."""
    layouts = DungeonLayoutManager()
    check(layouts.total_room_layouts() == 3, "Dungeon must expose three combat layouts")
    layout_types = {layout.layout_type for layout in layouts.room_layouts}
    check({LAYOUT_START, LAYOUT_ENCOUNTER, LAYOUT_ELITE_BOSS} <= layout_types, "Combat layout types are incomplete")
    check(layouts.clear_layout.layout_type == LAYOUT_CLEAR, "Dungeon clear layout is missing")

    layout_ids = set()
    for data in (*DUNGEON_ROOM_LAYOUTS, DUNGEON_CLEAR_LAYOUT):
        check(data["layout_id"] not in layout_ids, f"Duplicate layout id: {data['layout_id']}")
        check(len(data["room_bounds"]) == 4, f"Invalid room bounds: {data['layout_id']}")
        check(len(data["arena_bounds"]) == 2, f"Invalid arena bounds: {data['layout_id']}")
        check(len(data["player_spawn"]) == 2, f"Invalid player spawn: {data['layout_id']}")
        _, _, room_width, room_height = data["room_bounds"]
        arena_left, arena_right = data["arena_bounds"]
        check(room_width > 0 and room_height > 0, f"Room bounds must be positive: {data['layout_id']}")
        check(arena_left < arena_right, f"Arena bounds are reversed: {data['layout_id']}")
        check(arena_left <= data["player_spawn"][0] <= arena_right, f"Player spawn is outside arena: {data['layout_id']}")
        if data["layout_type"] != LAYOUT_CLEAR:
            check(data["enemy_spawn_points_right"], f"Missing right enemy spawns: {data['layout_id']}")
            check(data["enemy_spawn_points_left"], f"Missing left enemy spawns: {data['layout_id']}")
            for spawn in (*data["enemy_spawn_points_right"], *data["enemy_spawn_points_left"]):
                check(len(spawn) == 2, f"Invalid enemy spawn: {data['layout_id']}")
                check(arena_left <= spawn[0] <= arena_right, f"Enemy spawn is outside arena: {data['layout_id']}")
        layout_ids.add(data["layout_id"])


def check_reward_runtime():
    """Exercise option generation, unique choices, effects, stacks, and clamps."""
    manager = RewardManager()
    options = manager.generate_options()
    check(len(options) == 3, "RewardManager must generate three choices")
    check(len({reward.reward_id for reward in options}) == 3, "Reward choices must be unique")

    for reward in create_reward_pool():
        player = create_player()
        player.health = 50
        reward.apply(player, reward.value)

    attack_reward = next(reward for reward in manager.reward_pool if reward.reward_id == "attack_damage_up")
    player = create_player()
    for _ in range(attack_reward.max_stacks):
        manager.current_options = [attack_reward]
        check(manager.apply_selected(player) is attack_reward, "Stackable reward failed before cap")
    manager.current_options = [attack_reward]
    check(manager.apply_selected(player) is None, "Reward applied after reaching max stacks")

    clamp_player = create_player()
    for reward in create_reward_pool():
        for _ in range(20):
            reward.apply(clamp_player, reward.value)
    check(clamp_player.damage_multiplier == MAX_DAMAGE_MULTIPLIER, "Damage cap failed")
    check(clamp_player.skill_damage_multiplier == MAX_SKILL_DAMAGE_MULTIPLIER, "Skill damage cap failed")
    check(
        clamp_player.combo_finisher_damage_multiplier == MAX_COMBO_FINISHER_DAMAGE_MULTIPLIER,
        "Finisher cap failed",
    )
    check(clamp_player.damage_taken_multiplier == MIN_DAMAGE_TAKEN_MULTIPLIER, "Damage reduction clamp failed")
    check(clamp_player.dash_cooldown_multiplier == MIN_DASH_COOLDOWN_MULTIPLIER, "Dash cooldown clamp failed")
    check(clamp_player.dash_speed_multiplier == MAX_DASH_SPEED_MULTIPLIER, "Dash distance cap failed")
    check(clamp_player.move_speed_multiplier == MAX_MOVE_SPEED_MULTIPLIER, "Move speed cap failed")
    check(clamp_player.skill_cooldown_multiplier == MIN_SKILL_COOLDOWN_MULTIPLIER, "Skill cooldown clamp failed")


def check_modes_and_reward_flow():
    """Initialize modes and exercise reward transition plus retry state reset."""
    solo = SoloMode()
    check(solo.is_active(), "Solo mode failed to initialize")
    solo.enemy.defeated = True
    solo.update_result_state()
    check(solo.result_state == SOLO_VICTORY, "Solo victory state failed")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    check(solo.result_state == SOLO_ACTIVE, "Solo rematch failed")

    dungeon = DungeonMode()
    check(dungeon.is_active_encounter_room(), "Dungeon mode failed to initialize")
    first_layout = dungeon.room_manager.current_layout()
    dungeon.complete_current_encounter_room()
    check(dungeon.room_manager.flow_state == ROOM_CLEARED, "Dungeon room clear state failed")
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(dungeon.room_manager.flow_state == ROOM_REWARD, "Dungeon reward state failed")
    check(len(dungeon.reward_manager.current_options) == 3, "Dungeon reward options failed")
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(dungeon.room_manager.flow_state == ROOM_ACTIVE, "Dungeon next-room transition failed")
    check(dungeon.room_manager.current_layout() is not first_layout, "Dungeon layout did not advance")

    dungeon.player.defeated = True
    dungeon.complete_dungeon_defeat()
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    check(dungeon.reward_manager.chosen_reward_count() == 0, "Dungeon retry kept stale rewards")
    check(dungeon.player.damage_multiplier == 1.0, "Dungeon retry kept stale player modifiers")
    check(dungeon.room_manager.current_room_index == 0, "Dungeon retry kept stale room progress")
    check(dungeon.is_active_encounter_room(), "Dungeon retry did not restart combat")


def check_boss_skill_transitions():
    """Force the neutral boss skill through telegraph, active, and recovery."""
    player = create_player(420)
    boss = EliteEnemy(520)
    boss.facing = -1
    controller = boss.skill_controller
    controller.cooldown_timer = 0
    controller.decision_delay_timer = 0

    check(controller.update(boss, player, 0.016), "Boss skill did not start")
    check(controller.state == BOSS_SKILL_TELEGRAPH, "Boss skill telegraph state failed")
    controller.update(boss, player, controller.telegraph_duration)
    check(controller.state == BOSS_SKILL_ACTIVE, "Boss skill active state failed")
    start_health = player.health
    controller.update(boss, player, 0.016)
    check(player.health < start_health, "Boss skill did not damage player")
    controller.update(boss, player, controller.active_duration)
    check(controller.state == BOSS_SKILL_RECOVERY, "Boss skill recovery state failed")
    controller.update(boss, player, controller.recovery_duration)
    check(controller.state == BOSS_SKILL_READY, "Boss skill did not return to ready")


def check_projectile_and_beam():
    """Update and draw neutral projectile primitives safely."""
    surface = pygame.Surface((WIDTH, HEIGHT))
    projectile = Projectile(100, 100, 1, speed=200, damage=5, lifetime=0.10)
    projectile.update(0.05)
    projectile.draw(surface)
    check(projectile.active, "Projectile expired too early")
    projectile.update(0.05)
    check(not projectile.active, "Projectile did not expire")

    beam = Beam(100, 180, 1, beam_range=220, height=24, damage=8, duration=0.10)
    beam.draw(surface)
    beam.update(0.10)
    check(not beam.active, "Beam did not expire")

    player = create_player()
    enemy = BasicEnemy(player.rect.right + 10)
    projectiles = ProjectileManager()
    skills = SkillManager(projectiles)
    check(skills.use_slot(1, player), "Ki Blast could not be used")
    projectiles.update(0.001, [enemy])
    check(enemy.health == BASIC_ENEMY_CONFIG["max_health"] - KI_BLAST_CONFIG["damage"], "Ki Blast collision failed")

    beam_enemy = BasicEnemy(280)
    beam_health = beam_enemy.health
    collision_beam = Beam(100, beam_enemy.rect.centery, 1, beam_range=260, height=40, damage=9, duration=0.10)
    projectiles.spawn_beam(collision_beam)
    projectiles.update(0.001, [beam_enemy])
    check(beam_enemy.health == beam_health - collision_beam.damage, "Beam collision failed")


def run():
    """Run every standalone smoke section."""
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT))
    checks = (
        ("config values", check_config_values),
        ("reward definitions", check_reward_definitions),
        ("dungeon layouts", check_layout_definitions),
        ("reward runtime", check_reward_runtime),
        ("mode lifecycle", check_modes_and_reward_flow),
        ("boss skill states", check_boss_skill_transitions),
        ("projectile and beam", check_projectile_and_beam),
    )
    try:
        for label, callback in checks:
            callback()
            print(f"[PASS] {label}")
    finally:
        pygame.quit()
    print(f"Smoke checks passed: {len(checks)} sections")


if __name__ == "__main__":
    run()
