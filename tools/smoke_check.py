"""Lightweight standalone regression checks for gameplay foundations."""

from pathlib import Path
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from config.boss_config import BOSS_SKILL_CONFIG, ELITE_ENEMY_CONFIG, SOLO_BOSS_COMBO_CONFIG
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
from config.mode_config import SOLO_KAMEHAMEHA_ENERGY_COST
from entities.basic_enemy import BasicEnemy
from entities.elite_enemy import EliteEnemy
from entities.player import Player
from managers.dungeon_layout import DungeonLayoutManager
from managers.game_state import GameState
from managers.room_state import ROOM_ACTIVE, ROOM_CLEARED, ROOM_REWARD
from modes.dungeon_mode import DungeonMode
from modes.solo_mode import SOLO_ACTIVE, SOLO_SETUP, SOLO_VICTORY, SoloMode
from settings import (
    ENEMY_STATE_ATTACK,
    ENEMY_STATE_IDLE,
    ENEMY_STATE_TELEGRAPH,
    GROUND_Y,
    HEIGHT,
    PLAYER_HEIGHT,
    WIDTH,
)
from systems.beam import Beam
from systems.audio_manager import AudioManager
from systems.effects import CombatImpact
from systems.boss_skill_controller import (
    BOSS_SKILL_ACTIVE,
    BOSS_SKILL_READY,
    BOSS_SKILL_RECOVERY,
    BOSS_SKILL_TELEGRAPH,
)
from systems.combat import process_enemy_attacks
from systems.projectile import Projectile
from systems.projectile_manager import ProjectileManager
from systems.reward import REWARD_EFFECTS, create_reward_pool
from systems.reward_manager import RewardManager
from systems.settings_store import SettingsStore
from systems.skill_manager import SkillManager
from systems.solo_boss_combo_controller import SoloBossComboController
from systems.solo_combo_burst import SoloComboBurst
from systems.solo_sprite_renderer import SoloSpriteRenderer
from ui.solo_setup import SLIDER_LEFT, SLIDER_WIDTH, SLIDER_Y
from ui.settings_menu import SettingsMenu


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
    check(SOLO_BOSS_COMBO_CONFIG["max_energy"] > 0, "Solo boss max energy must be positive")
    check(
        SOLO_BOSS_COMBO_CONFIG["dealt_hit_energy_gain"] == 3 * SOLO_BOSS_COMBO_CONFIG["hurt_energy_gain"],
        "Solo boss energy gain ratio must stay 3:1",
    )
    for skill_id in ("skill_1", "skill_2", "final_skill"):
        profile = SOLO_BOSS_COMBO_CONFIG[skill_id]
        check(profile["energy_cost"] <= SOLO_BOSS_COMBO_CONFIG["max_energy"], f"{skill_id} costs too much energy")
        check(profile["frames"], f"{skill_id} must expose logical frames")
        check(len(profile["hit_durations"]) == len(profile["frames"]), f"{skill_id} pacing does not match frames")
        check(profile["telegraph_duration"] > 0, f"{skill_id} telegraph must be readable")
        check(profile["recovery_duration"] > 0, f"{skill_id} recovery must be punishable")


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

    heal_manager = RewardManager()
    heal_reward = next(reward for reward in heal_manager.reward_pool if reward.reward_id == "small_heal_now")
    heal_player = create_player()
    for _ in range(heal_reward.max_stacks):
        heal_player.health = 50
        heal_manager.current_options = [heal_reward]
        check(heal_manager.apply_selected(heal_player) is heal_reward, "Immediate heal failed before cap")
    heal_manager.current_options = [heal_reward]
    check(heal_manager.apply_selected(heal_player) is None, "Immediate heal applied after reaching max stacks")

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
    check(solo.result_state == SOLO_SETUP, "Solo setup state failed to initialize")
    screen = pygame.Surface((WIDTH, HEIGHT))
    scene_surface = pygame.Surface((WIDTH, HEIGHT))
    solo.draw(screen, scene_surface)
    solo.handle_event(
        pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=(SLIDER_LEFT + SLIDER_WIDTH, SLIDER_Y[0]),
        )
    )
    check(solo.setup_player_hp > PLAYER_MAX_HEALTH, "Solo player HP mouse slider failed")
    solo.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(0, 0)))
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d))
    selected_player_hp = solo.setup_player_hp
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(solo.is_active(), "Solo setup did not start the fight")
    check(solo.player.max_health == selected_player_hp, "Solo player HP setup was not applied")
    solo.player.stun_timer = 0.5
    solo.player.skill_lock_timer = 1.0
    solo.draw(screen, scene_surface)
    solo.enemy.defeated = True
    solo.update_result_state()
    check(solo.result_state == SOLO_VICTORY, "Solo victory state failed")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    check(solo.result_state == SOLO_ACTIVE, "Solo rematch failed")
    check(solo.player.stun_timer == 0, "Solo rematch kept stale stun")
    check(solo.player.skill_lock_timer == 0, "Solo rematch kept stale skill lock")

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


def check_pause_and_controls_qol():
    """Freeze gameplay behind pause/help overlays and preserve flow inputs."""
    screen = pygame.Surface((WIDTH, HEIGHT))
    scene_surface = pygame.Surface((WIDTH, HEIGHT))
    keys = pygame.key.get_pressed()

    solo = SoloMode()
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    check(solo.controls_visible, "Solo setup controls overlay did not open")
    solo.draw(screen, scene_surface)
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
    check(not solo.paused, "Solo setup screen entered pause unexpectedly")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    solo_skill = solo.skill_manager.get_slot(1)
    solo_skill.current_cooldown = 1.0
    solo_projectile = solo.projectile_manager.spawn(Projectile(100, 100, 1, 200, 5, 1.0))
    solo_beam = solo.projectile_manager.spawn_beam(Beam(100, 180, 1, 220, 24, 8, 1.0))
    solo_enemy_x = solo.enemy.x
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
    check(solo.paused, "Solo pause did not open")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j))
    solo.update(keys, 0.25)
    check(not solo.player.is_attacking, "Solo pause allowed a combat input")
    check(solo_skill.current_cooldown == 1.0, "Solo pause ticked a skill cooldown")
    check(solo_projectile.x == 100, "Solo pause moved a projectile")
    check(solo_projectile.lifetime == 1.0, "Solo pause ticked a projectile lifetime")
    check(solo_beam.duration == 1.0, "Solo pause ticked a beam duration")
    check(solo.enemy.x == solo_enemy_x, "Solo pause moved the enemy")
    solo.draw(screen, scene_surface)

    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    check(solo.controls_visible, "Solo controls overlay did not open while paused")
    solo.draw(screen, scene_surface)
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    check(solo.is_active(), "Solo paused restart did not start an active fight")
    check(not solo.paused, "Solo paused restart kept stale pause state")
    check(not solo.projectile_manager.projectiles, "Solo paused restart kept stale projectiles")

    solo_skill = solo.skill_manager.get_slot(1)
    solo_skill.current_cooldown = 1.0
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j))
    solo.update(keys, 0.25)
    check(not solo.player.is_attacking, "Solo controls overlay allowed a combat input")
    check(solo_skill.current_cooldown == 1.0, "Solo controls overlay ticked a skill cooldown")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))

    dungeon = DungeonMode()
    dungeon_skill = dungeon.skill_manager.get_slot(1)
    dungeon_skill.current_cooldown = 1.0
    dungeon_projectile = dungeon.projectile_manager.spawn(Projectile(100, 100, 1, 200, 5, 1.0))
    dungeon_beam = dungeon.projectile_manager.spawn_beam(Beam(100, 180, 1, 220, 24, 8, 1.0))
    dungeon.encounter_manager.update_wave_progress(dungeon.encounter_manager.wave_delay_timer, dungeon.player)
    dungeon_enemy = dungeon.encounter_manager.get_enemies()[0]
    dungeon_enemy_x = dungeon_enemy.x
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
    check(dungeon.paused, "Dungeon pause did not open")
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j))
    dungeon.update(keys, 0.25)
    check(not dungeon.player.is_attacking, "Dungeon pause allowed a combat input")
    check(dungeon_skill.current_cooldown == 1.0, "Dungeon pause ticked a skill cooldown")
    check(dungeon_projectile.x == 100, "Dungeon pause moved a projectile")
    check(dungeon_projectile.lifetime == 1.0, "Dungeon pause ticked a projectile lifetime")
    check(dungeon_beam.duration == 1.0, "Dungeon pause ticked a beam duration")
    check(dungeon_enemy.x == dungeon_enemy_x, "Dungeon pause moved an enemy")
    dungeon.draw(screen, scene_surface)

    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    check(dungeon.controls_visible, "Dungeon controls overlay did not open while paused")
    dungeon.draw(screen, scene_surface)
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    check(dungeon.is_active_encounter_room(), "Dungeon paused retry did not restart the run")
    check(not dungeon.paused, "Dungeon paused retry kept stale pause state")
    check(not dungeon.projectile_manager.projectiles, "Dungeon paused retry kept stale projectiles")

    dungeon.complete_current_encounter_room()
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(dungeon.room_manager.flow_state == ROOM_REWARD, "Dungeon reward setup failed during QoL check")
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(dungeon.room_manager.flow_state == ROOM_REWARD, "Dungeon pause allowed reward confirmation")
    check(dungeon.reward_manager.selected_index == 0, "Dungeon pause allowed reward navigation")
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(dungeon.room_manager.flow_state == ROOM_REWARD, "Dungeon controls overlay allowed reward confirmation")
    dungeon.draw(screen, scene_surface)
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(dungeon.room_manager.flow_state == ROOM_ACTIVE, "Dungeon reward confirmation broke after QoL overlays")


def check_settings_foundation():
    """Persist local preferences, recover corrupt JSON, and apply safe shake settings."""
    screen = pygame.Surface((WIDTH, HEIGHT))
    settings_path = PROJECT_ROOT / "data" / "settings-smoke.tmp"
    try:
        try:
            settings_path.unlink(missing_ok=True)
        except OSError:
            pass
        store = SettingsStore(settings_path)
        check(settings_path.exists(), "Missing settings file was not created safely")
        check(store.get("master_volume") == 1.0, "Settings defaults failed to load")

        store.set("master_volume", 0.5)
        check(SettingsStore(settings_path).get("master_volume") == 0.5, "Settings value did not persist")

        menu = SettingsMenu(store)
        menu.draw(screen)
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
        check(store.get("master_volume") == 0.6, "Settings menu numeric adjustment failed")
        menu.selected_index = 3
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        check(not store.get("screen_shake_enabled"), "Settings menu toggle failed")

        settings_path.write_text("{invalid json", encoding="utf-8")
        recovered_store = SettingsStore(settings_path)
        check(recovered_store.get("master_volume") == 1.0, "Corrupt settings did not restore defaults")
        with settings_path.open("r", encoding="utf-8") as settings_file:
            check(isinstance(json.load(settings_file), dict), "Corrupt settings fallback did not write valid JSON")
    finally:
        try:
            settings_path.unlink(missing_ok=True)
        except OSError:
            pass

    game_state = GameState()
    game_state.enter_settings()
    check(game_state.is_settings(), "Settings routing did not open")
    game_state.enter_mode_select()
    check(game_state.is_mode_select(), "Settings routing did not return to mode select")

    attack_data = {"hitstop": 0.1, "shake_duration": 0.2, "shake_strength": 6}
    disabled_impact = CombatImpact({"screen_shake_enabled": False, "camera_shake_strength": 1.0})
    disabled_impact.start_hit_impact(attack_data)
    check(disabled_impact.is_hitstop_active(), "Disabling screen shake incorrectly disabled hitstop")
    check(disabled_impact.camera_shake_timer == 0, "Disabled screen shake still started a timer")

    reduced_impact = CombatImpact({"screen_shake_enabled": True, "camera_shake_strength": 0.5})
    reduced_impact.start_hit_impact(attack_data)
    check(reduced_impact.camera_shake_strength == 3, "Camera shake strength multiplier was not applied")

    preferences = {"show_controls_hint": False}
    SoloMode(preferences).draw(screen, pygame.Surface((WIDTH, HEIGHT)))
    DungeonMode(preferences).draw(screen, pygame.Surface((WIDTH, HEIGHT)))


def check_audio_hooks_foundation():
    """No-op missing audio safely and emit one-shot gameplay placeholder hooks."""
    class RecordingAudio:
        def __init__(self):
            self.sfx_events = []
            self.music_events = []
            self.refresh_count = 0

        def play_sfx(self, name):
            self.sfx_events.append(name)
            return False

        def play_music(self, name, loops=-1):
            self.music_events.append((name, loops))
            return False

        def refresh_volumes(self):
            self.refresh_count += 1

    preferences = {"master_volume": 0.5, "sfx_volume": 0.4, "music_volume": 0.6}
    audio = AudioManager(preferences, PROJECT_ROOT / "data" / "missing-audio")
    check(audio.sfx_volume() == 0.2, "Audio manager SFX volume did not apply master volume")
    check(audio.music_volume() == 0.3, "Audio manager music volume did not apply master volume")
    check(not audio.play_sfx("missing"), "Missing SFX asset did not no-op")
    check(not audio.play_music("missing"), "Missing music asset did not no-op")

    with (
        patch.object(pygame.mixer, "get_init", return_value=None),
        patch.object(pygame.mixer, "init", side_effect=pygame.error("no audio device")),
    ):
        unavailable_audio = AudioManager(preferences, PROJECT_ROOT / "data" / "missing-audio")
    check(not unavailable_audio.enabled, "Unavailable audio device did not disable playback safely")
    check(not unavailable_audio.play_sfx("missing"), "Disabled audio manager did not no-op")

    recorder = RecordingAudio()
    player = create_player()
    player.audio_manager = recorder
    player.begin_combo_attack(1)
    check(recorder.sfx_events == ["player_attack"], "Player attack hook did not fire exactly once")

    victim = create_player()
    victim.audio_manager = recorder
    check(victim.take_damage(1), "Player hit setup did not apply damage")
    check(recorder.sfx_events[-1] == "player_hit", "Player hit hook did not fire")

    enemy = BasicEnemy(420)
    enemy.audio_manager = recorder
    check(enemy.take_damage(1), "Enemy hit setup did not apply damage")
    check(recorder.sfx_events[-1] == "enemy_hit", "Enemy hit hook did not fire")

    boss = EliteEnemy(520)
    boss.audio_manager = recorder
    boss.skill_controller.start_telegraph(boss)
    check(recorder.sfx_events[-1] == "boss_skill", "Dungeon boss skill hook did not fire")

    solo = SoloMode(audio_manager=recorder)
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    solo.enemy.defeated = True
    solo.update_result_state()
    solo.update_result_state()
    check(recorder.sfx_events.count("victory") == 1, "Solo victory hook repeated or did not fire")

    defeated_solo = SoloMode(audio_manager=recorder)
    defeated_solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    defeated_solo.player.defeated = True
    defeated_solo.update_result_state()
    defeated_solo.update_result_state()
    check(recorder.sfx_events.count("defeat") == 1, "Solo defeat hook repeated or did not fire")

    dungeon = DungeonMode(audio_manager=recorder)
    dungeon.complete_current_encounter_room()
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(recorder.sfx_events[-1] == "reward_select", "Dungeon reward hook did not fire")

    dungeon.complete_dungeon_defeat()
    check(recorder.sfx_events[-1] == "defeat", "Dungeon defeat hook did not fire")

    with patch.object(SettingsStore, "save", return_value=True):
        settings_menu = SettingsMenu(SimpleNamespace(get=lambda key: 1.0, set=lambda key, value: value), recorder)
        settings_menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    check(recorder.sfx_events[-1] == "menu_select", "Menu select hook did not fire")


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


def check_solo_boss_technique_playback():
    """Hold one logical technique frame per normal Solo boss attack."""
    renderer = SoloSpriteRenderer()
    renderer.boss_technique_frames = [pygame.Surface((1, 1)) for _ in range(6)]
    boss_visual = SimpleNamespace(
        state=ENEMY_STATE_IDLE,
        skill_controller=SimpleNamespace(visual_frame_index=None),
    )
    observed_frames = []

    for _ in range(7):
        boss_visual.state = ENEMY_STATE_TELEGRAPH
        renderer.update_boss_technique(boss_visual, 1.0)
        observed_frames.append(renderer.get_boss_technique_index(boss_visual))

        boss_visual.state = ENEMY_STATE_ATTACK
        renderer.update_boss_technique(boss_visual, 1.0)
        check(
            renderer.get_boss_technique_index(boss_visual) == observed_frames[-1],
            "Solo boss normal attack advanced through multiple technique frames",
        )

        boss_visual.state = ENEMY_STATE_IDLE
        renderer.update_boss_technique(boss_visual, 0.016)

    check(observed_frames == [0, 1, 2, 3, 4, 5, 0], "Solo boss normal attack frame cycle failed")

    boss_visual.state = BOSS_SKILL_TELEGRAPH
    renderer.update_boss_technique(boss_visual, renderer.boss_skill_technique_delay)
    check(renderer.get_boss_technique_index(boss_visual) == 1, "Solo boss skill visual playback changed")

    renderer.boss_technique_frames = []
    boss_visual.state = ENEMY_STATE_IDLE
    renderer.update_boss_technique(boss_visual, 0.016)
    boss_visual.state = ENEMY_STATE_TELEGRAPH
    renderer.update_boss_technique(boss_visual, 0.016)
    check(renderer.get_boss_technique_index(boss_visual) == 0, "Missing boss technique frames broke fallback")

    natural_paths = [
        Path("frame_10_delay-0.1s.png"),
        Path("frame_3_delay-0.1s.png"),
        Path("frame_1_delay-0.1s.png"),
    ]
    natural_names = [path.name for path in sorted(natural_paths, key=renderer.natural_sort_key)]
    check(
        natural_names == [
            "frame_1_delay-0.1s.png",
            "frame_3_delay-0.1s.png",
            "frame_10_delay-0.1s.png",
        ],
        "Solo boss technique frames are not naturally sorted",
    )

    player = create_player(420)
    boss = EliteEnemy(player.rect.right + 20)
    boss.facing = -1
    boss.start_attack()
    start_health = player.health
    check(process_enemy_attacks([boss], player), "Solo boss normal attack did not connect")
    check(player.health < start_health, "Solo boss normal attack did not damage player")


def check_solo_boss_combo_skills():
    """Validate Solo boss pacing, anti-spam, frame damage, status locks, and energy."""
    player = create_player(420)
    player.max_health = 1000
    player.health = player.max_health
    boss = EliteEnemy(520)
    boss.facing = -1
    boss.skill_controller = SoloBossComboController()
    boss.max_energy = boss.skill_controller.max_energy
    boss.energy = 100
    controller = boss.skill_controller
    controller.cooldown_timer = 0
    controller.decision_delay_timer = 0

    def select_and_record():
        skill_id, profile = controller.choose_skill(boss, player)
        check(profile is not None, "Solo boss weighted cycle returned no skill")
        controller.start_telegraph(boss, skill_id, profile)
        controller.cancel()
        controller.cooldown_timer = 0
        controller.decision_delay_timer = 0
        controller.major_skill_spacing_timer = 0
        for cooldown_skill_id in controller.skill_cooldown_timers:
            controller.skill_cooldown_timers[cooldown_skill_id] = 0
        boss.state = ENEMY_STATE_IDLE
        boss.energy = 100
        return skill_id

    weighted_cycle = [select_and_record() for _ in range(5)]
    check(
        weighted_cycle == ["skill_1", "skill_1", "skill_2", "skill_2", "final_skill"],
        "Solo boss weighted anti-spam cycle failed",
    )
    check(controller.final_lockout_timer > 0, "Solo boss final skill lockout did not start")
    check(controller.choose_skill(boss, player)[0] != "final_skill", "Solo boss repeated final during lockout")

    controller = SoloBossComboController()
    boss.skill_controller = controller
    boss.energy = 100
    controller.skills_since_final = SOLO_BOSS_COMBO_CONFIG["final_min_prior_skills"]
    controller.selection_cursor = len(controller.weighted_skill_cycle) - 1
    controller.cooldown_timer = 0
    controller.decision_delay_timer = 0
    far_player = create_player(100)
    check(
        not controller.can_select_skill("final_skill", SOLO_BOSS_COMBO_CONFIG["final_skill"], boss, far_player),
        "Solo boss final skill started from fullscreen range",
    )
    check(
        controller.can_select_skill("final_skill", SOLO_BOSS_COMBO_CONFIG["final_skill"], boss, player),
        "Solo boss final skill gate did not open",
    )
    check(controller.update(boss, player, 0.016), "Solo boss final skill did not start")
    check(boss.energy == 0, "Solo boss final skill did not spend energy")
    controller.update(boss, player, SOLO_BOSS_COMBO_CONFIG["final_skill"]["telegraph_duration"])
    renderer = SoloSpriteRenderer()
    renderer.boss_technique_frames = [pygame.Surface((1, 1)) for _ in range(6)]

    observed_frames = []
    observed_damage = []
    for hit_number in range(1, 7):
        observed_frames.append(controller.visual_frame_index)
        renderer.update_boss_technique(boss, 0)
        check(
            renderer.get_boss_technique_index(boss) == controller.visual_frame_index,
            "Solo boss rendered the wrong combo frame",
        )
        start_health = player.health
        controller.update(boss, player, 0.001)
        observed_damage.append(start_health - player.health)
        if hit_number in {3, 6}:
            check(
                player.stun_timer >= SOLO_BOSS_COMBO_CONFIG["stun_duration"],
                f"Solo boss final skill hit {hit_number} did not stun",
            )
            check(
                player.skill_lock_timer >= SOLO_BOSS_COMBO_CONFIG["skill_lock_duration"],
                f"Solo boss final skill hit {hit_number} did not lock skills",
            )
        controller.update(boss, player, controller.state_timer)
        if hit_number == 3:
            expected_pause = (
                SOLO_BOSS_COMBO_CONFIG["final_skill"]["hit_durations"][3]
                + SOLO_BOSS_COMBO_CONFIG["final_skill"]["group_pause_after_hits"][3]
            )
            check(controller.state_timer == expected_pause, "Solo boss final group pause failed")

    check(observed_frames == [0, 1, 2, 3, 4, 5], "Solo boss final skill frame sequence failed")
    check(observed_damage == [18, 24, 30, 18, 24, 30], "Solo boss final skill damage sequence failed")
    check(controller.state == BOSS_SKILL_RECOVERY, "Solo boss final skill recovery did not start")
    check(
        controller.state_timer == SOLO_BOSS_COMBO_CONFIG["final_skill"]["recovery_duration"],
        "Solo boss final skill recovery window is incorrect",
    )

    def profile_damage(skill_id):
        profile = SOLO_BOSS_COMBO_CONFIG[skill_id]
        return [
            SOLO_BOSS_COMBO_CONFIG["base_hit_damage"][index % 3] * profile["damage_multiplier"]
            for index, _ in enumerate(profile["frames"])
        ]

    check(profile_damage("skill_1") == [6, 8, 10], "Solo boss Skill 1 damage sequence failed")
    check(profile_damage("skill_2") == [12, 16, 20], "Solo boss Skill 2 damage sequence failed")

    solo = SoloMode()
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    start_player_energy = solo.energy
    start_boss_energy = solo.enemy.energy
    previous_player_health = solo.player.health
    previous_enemy_health = solo.enemy.health
    solo.player.health -= 1
    solo.enemy.health -= 1
    solo.apply_energy_from_health_changes(previous_player_health, previous_enemy_health)
    check(solo.energy == start_player_energy + 12, "Solo player damage-exchange energy gain failed")
    check(solo.enemy.energy == start_boss_energy + 12, "Solo boss damage-exchange energy gain failed")
    solo.energy = SOLO_KAMEHAMEHA_ENERGY_COST
    check(solo.try_use_kamehameha(), "Solo Kamehameha did not start with enough energy")
    check(solo.energy == 0, "Solo Kamehameha did not spend its configured energy")
    locked_player = create_player()
    locked_player.skill_lock_timer = 1.0
    locked_skills = SkillManager(ProjectileManager())
    check(not locked_skills.use_slot(1, locked_player), "Player skill lock did not block skill use")
    locked_burst = SoloComboBurst()
    check(not locked_burst.can_start(locked_player, 100), "Player skill lock did not block Combo Burst")


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
        ("pause and controls QoL", check_pause_and_controls_qol),
        ("save and settings foundation", check_settings_foundation),
        ("audio hooks foundation", check_audio_hooks_foundation),
        ("boss skill states", check_boss_skill_transitions),
        ("projectile and beam", check_projectile_and_beam),
        ("solo boss technique playback", check_solo_boss_technique_playback),
        ("solo boss combo skills", check_solo_boss_combo_skills),
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
