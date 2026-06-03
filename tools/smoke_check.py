"""Lightweight standalone regression checks for gameplay foundations."""

from pathlib import Path
from collections import defaultdict
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
from config.enemy_config import (
    BASIC_ENEMY_CONFIG,
    FAST_ENEMY_CONFIG,
    ORC_LEVEL_2_ENEMY_CONFIG,
    ORC_LEVEL_3_ENEMY_CONFIG,
    SLIME_ENEMY_CONFIG,
)
from config.enemy_sprite_config import ENEMY_SPRITE_CONFIGS
from config.default_settings import SETTINGS_MENU_ITEMS
from config.input_config import DEFAULT_KEY_BINDINGS
from config.goku_sprite_config import (
    GOKU_ENERGY_DISC_EFFECT_PATHS,
    GOKU_KAMEHAMEHA_EFFECT_PATH,
    GOKU_KI_BLAST_ACTION_IDS,
    GOKU_KI_BLAST_EFFECT_PATH,
    GOKU_PLAYER_ANIMATION_CONFIG,
    GOKU_PROJECTILE_IMPACT_EFFECT_PATHS,
    GOKU_SUPER_SAIYAN_KAMEHAMEHA_EFFECT_PATH,
)
from config.player_config import (
    COUNTER_ATTACK,
    DASH_COOLDOWN,
    DASH_SPEED,
    KICK_ATTACK_COMBO,
    LIGHT_ATTACK_COMBO,
    PLAYER_HURT_CHAIN_RESET_TIME,
    PLAYER_HURT_DURATION,
    PLAYER_HURT_VISUAL_HOLD_DURATION,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    SUPER_SAIYAN_DAMAGE_MULTIPLIER,
    SUPER_SAIYAN_DURATION,
    SUPER_SAIYAN_MAX_ENERGY,
    SUPER_SAIYAN_TRANSFORM_DURATION,
)
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
from config.skill_config import ENERGY_DISC_CONFIG, KAMEHAMEHA_CONFIG, KI_BLAST_CONFIG
from config.mode_config import (
    SOLO_ENERGY_DISC_ENERGY_COST,
    SOLO_FIGHT_CALLOUT_DURATION,
    SOLO_INTRO_ENTRY_DURATION,
    SOLO_KAMEHAMEHA_ENERGY_COST,
    SOLO_KI_BLAST_ENERGY_COST,
)
from entities.basic_enemy import BasicEnemy
from entities.elite_enemy import EliteEnemy
from entities.fast_enemy import FastEnemy
from entities.orc_level_enemy import OrcLevel2Enemy, OrcLevel3Enemy
from entities.player import Player
from entities.player_parts.render_state import get_player_visual_state
from entities.slime_enemy import SlimeEnemy
from managers.dungeon_layout import DungeonLayoutManager
from managers.game_state import GameState
from managers.room_state import ROOM_ACTIVE, ROOM_CLEARED, ROOM_REWARD
from modes.dungeon_mode import DungeonMode
from modes.solo_mode import SOLO_ACTIVE, SOLO_INTRO, SOLO_SETUP, SOLO_VICTORY, SoloMode
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
from systems.animation_timing import get_animation_dt
from systems.audio_manager import AudioManager
from systems.display_manager import DisplayManager
from systems.effects import CombatImpact
from systems.enemy_sprite_renderer import EnemySpriteRenderer
from systems.goku_player_sprite_renderer import GokuPlayerSpriteRenderer
from systems.input_manager import InputManager
from systems.boss_skill_controller import (
    BOSS_SKILL_ACTIVE,
    BOSS_SKILL_READY,
    BOSS_SKILL_RECOVERY,
    BOSS_SKILL_TELEGRAPH,
)
from systems.combat import process_enemy_attacks, process_player_attack
from systems.combat_momentum import CombatMomentum
from systems.projectile import Projectile
from systems.projectile_manager import ProjectileManager
from systems.reward import REWARD_EFFECTS, create_reward_pool
from systems.reward_manager import RewardManager
from systems.settings_store import SettingsStore
from systems.skill_manager import SkillManager
from systems.solo_boss_combo_controller import SoloBossComboController
from systems.solo_combo_burst import SoloComboBurst
from systems.solo_sprite_renderer import SoloSpriteRenderer
from tools.validate_enemy_sprites import cut_sheet_frames, validate_enemy_sprites, validate_sprite_config
from ui.solo_setup import SLIDER_LEFT, SLIDER_WIDTH, SLIDER_Y
from ui.settings_menu import SettingsMenu
from ui.game_guide import draw_game_guide
from ui.game_preview import draw_game_preview
from ui.combat_momentum import draw_combat_momentum
from world.dungeon_decor import PROP_PATHS, DungeonDecorRenderer
from world.battlefield import get_arena_background
from world.dungeon_room import draw_dungeon_room, get_dungeon_backdrop, get_room_background


def check(condition, message):
    """Raise a readable assertion when one smoke expectation fails."""
    if not condition:
        raise AssertionError(message)


def create_player(x=180):
    """Return a grounded player for mechanical checks."""
    return Player(x, GROUND_Y - PLAYER_HEIGHT)


def finish_solo_intro(solo):
    """Advance the frozen Solo intro into active combat."""
    check(solo.result_state == SOLO_INTRO, "Solo did not enter its intro state")
    solo.update_intro(SOLO_INTRO_ENTRY_DURATION)
    check(solo.intro_phase == "fight", "Solo intro did not enter its FIGHT callout")
    solo.update_intro(SOLO_FIGHT_CALLOUT_DURATION)
    check(solo.result_state == SOLO_ACTIVE, "Solo intro did not release active combat")


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
        ("slime enemy", SLIME_ENEMY_CONFIG),
        ("orc level 2 enemy", ORC_LEVEL_2_ENEMY_CONFIG),
        ("orc level 3 enemy", ORC_LEVEL_3_ENEMY_CONFIG),
        ("elite enemy", ELITE_ENEMY_CONFIG),
    ):
        check(required_enemy_fields <= enemy_config.keys(), f"{label} config is incomplete")
        check(enemy_config["max_health"] > 0, f"{label} HP must be positive")
        check(enemy_config["chase_speed"] > 0, f"{label} chase speed must be positive")
        check(enemy_config["attack_damage"] > 0, f"{label} damage must be positive")
        check(enemy_config["attack_range"] > 0, f"{label} range must be positive")
        check(enemy_config["telegraph_duration"] > 0, f"{label} telegraph must be readable")
        check(enemy_config["attack_cooldown"] > 0, f"{label} cooldown must be positive")
    check(
        ORC_LEVEL_2_ENEMY_CONFIG["max_health"] == BASIC_ENEMY_CONFIG["max_health"] * 2,
        "Orc level 2 HP scaling changed",
    )
    check(
        ORC_LEVEL_3_ENEMY_CONFIG["max_health"] == BASIC_ENEMY_CONFIG["max_health"] * 3,
        "Orc level 3 HP scaling changed",
    )

    required_ki_blast_fields = {"damage", "cooldown", "speed", "lifetime", "width", "height"}
    check(required_ki_blast_fields <= KI_BLAST_CONFIG.keys(), "Ki Blast config is incomplete")
    for field in required_ki_blast_fields:
        check(KI_BLAST_CONFIG[field] > 0, f"Ki Blast {field} must be positive")

    required_kamehameha_fields = {"damage", "cooldown", "range", "height", "duration"}
    check(required_kamehameha_fields <= KAMEHAMEHA_CONFIG.keys(), "Kamehameha config is incomplete")
    for field in required_kamehameha_fields:
        check(KAMEHAMEHA_CONFIG[field] > 0, f"Kamehameha {field} must be positive")

    required_energy_disc_fields = {"damage", "cooldown", "speed", "lifetime", "width", "height"}
    check(required_energy_disc_fields <= ENERGY_DISC_CONFIG.keys(), "Energy Disc config is incomplete")
    for field in required_energy_disc_fields:
        check(ENERGY_DISC_CONFIG[field] > 0, f"Energy Disc {field} must be positive")

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
        check(data["torch_positions"], f"Missing torch positions: {data['layout_id']}")
        check(data["decor_props"], f"Missing decor props: {data['layout_id']}")
        check(data["title"], f"Missing authored room title: {data['layout_id']}")
        check(data["subtitle"], f"Missing authored room subtitle: {data['layout_id']}")
        for prop_id, _, _ in data["decor_props"]:
            check(prop_id in PROP_PATHS, f"Unknown Dungeon decor prop: {prop_id}")
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


def check_dungeon_decor_foundation():
    """Draw room decor, animate torches, and preserve missing-asset fallback."""
    renderer = DungeonDecorRenderer()
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    layout = DungeonLayoutManager().room_layouts[0]
    draw_dungeon_room(surface, layout, decor_renderer=renderer)
    check(get_arena_background() is get_arena_background(), "Arena background cache was not reused")
    check(get_room_background(layout) is get_room_background(layout), "Dungeon room background cache was not reused")
    backdrop_size = (layout.room_bounds[2] - 36, layout.room_bounds[3] - 18)
    check(get_dungeon_backdrop(backdrop_size) is not None, "Licensed Dungeon runtime backdrop did not load")
    check(
        get_dungeon_backdrop(backdrop_size) is get_dungeon_backdrop(backdrop_size),
        "Dungeon runtime backdrop cache was not reused",
    )
    initial_torch_frame = renderer.torch_frame_index
    renderer.update(renderer.torch_frame_duration)
    check(renderer.torch_frame_index != initial_torch_frame, "Dungeon torch playback did not advance")
    draw_dungeon_room(surface, layout, show_exit=True, decor_renderer=renderer)
    check(renderer.load_image(PROP_PATHS["sword"]) is not None, "Dungeon sword prop did not load")
    check(
        all("Không dùng đến" not in str(path) for path in PROP_PATHS.values()),
        "Excluded Free asset folder leaked into Dungeon decor",
    )

    missing_renderer = DungeonDecorRenderer()
    missing_renderer.image_cache[str(PROP_PATHS["crate"])] = None
    draw_dungeon_room(surface, layout, show_exit=True, decor_renderer=missing_renderer)


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
    finish_solo_intro(solo)
    check(solo.is_active(), "Solo setup did not start the fight")
    check(solo.player.max_health == selected_player_hp, "Solo player HP setup was not applied")
    solo.player.stun_timer = 0.5
    solo.player.skill_lock_timer = 1.0
    solo.draw(screen, scene_surface)
    solo.enemy.defeated = True
    solo.update_result_state()
    check(solo.result_state == SOLO_VICTORY, "Solo victory state failed")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    finish_solo_intro(solo)
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
    finish_solo_intro(solo)

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
    finish_solo_intro(solo)
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

        setting_changes = []
        menu = SettingsMenu(store, on_setting_changed=lambda key, value: setting_changes.append((key, value)))
        menu.draw(screen)
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
        check(store.get("master_volume") == 0.6, "Settings menu numeric adjustment failed")
        menu.selected_index = next(
            index for index, item in enumerate(SETTINGS_MENU_ITEMS)
            if item["key"] == "screen_shake_enabled"
        )
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        check(not store.get("screen_shake_enabled"), "Settings menu toggle failed")
        menu.selected_index = next(
            index for index, item in enumerate(SETTINGS_MENU_ITEMS)
            if item["key"] == "reduce_motion_enabled"
        )
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        check(store.get("reduce_motion_enabled"), "Reduced-motion accessibility toggle failed")
        check(
            ("reduce_motion_enabled", True) in setting_changes,
            "Settings menu did not publish a runtime preference edit",
        )
        store.set("target_fps", 144)
        check(SettingsStore(settings_path).get("target_fps") == 144, "Target FPS setting did not persist")
        store.set("animation_speed", 0.65)
        check(SettingsStore(settings_path).get("animation_speed") == 0.65, "Animation speed setting did not persist")

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
    game_state.enter_guide()
    check(game_state.is_guide(), "Guide routing did not open")
    draw_game_guide(screen, InputManager())
    game_state.enter_preview()
    check(game_state.is_preview(), "Preview routing did not open")
    draw_game_preview(screen, InputManager())
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

    accessible_impact = CombatImpact(
        {
            "screen_shake_enabled": True,
            "camera_shake_strength": 1.0,
            "reduce_motion_enabled": True,
        }
    )
    accessible_impact.start_hit_impact(attack_data)
    check(accessible_impact.is_hitstop_active(), "Reduced motion incorrectly disabled gameplay hitstop")
    check(accessible_impact.camera_shake_timer == 0, "Reduced motion still started camera shake")

    display_surface = pygame.Surface((WIDTH, HEIGHT))
    with patch.object(pygame.display, "set_mode", return_value=display_surface) as set_mode:
        display_manager = DisplayManager()
        check(display_manager.apply_fullscreen(True) is display_surface, "Fullscreen display surface was not retained")
        check(
            set_mode.call_args.args == ((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED),
            "Scaled fullscreen flags were not applied",
        )
        display_manager.handle_setting_changed("master_volume", 0.5)
        check(set_mode.call_count == 1, "Unrelated setting rebuilt the display surface")

    fallback_surface = pygame.Surface((WIDTH, HEIGHT))
    with patch.object(pygame.display, "set_mode", side_effect=(pygame.error("unsupported"), fallback_surface)) as set_mode:
        display_manager = DisplayManager()
        check(display_manager.apply_fullscreen(True) is fallback_surface, "Fullscreen failure did not fall back to windowed")
        check(set_mode.call_args_list[-1].args == ((WIDTH, HEIGHT),), "Windowed fullscreen fallback was not applied")

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


def check_combat_momentum_presentation():
    """Validate that momentum reacts to combat without changing mechanics."""
    player = create_player()
    momentum = CombatMomentum()
    player.combat_momentum = momentum
    starting_damage = player.attack_damage

    player.combo_step = 1
    player.attack_style = "punch"
    player.register_attack_payoff()
    check(momentum.chain_count == 1, "Momentum did not count a connected hit")
    check(momentum.score > 0, "Momentum did not gain score from a connected hit")
    check(player.attack_damage == starting_damage, "Momentum changed combat damage")

    player.combo_step = 2
    player.attack_style = "kick"
    player.register_attack_payoff()
    check(momentum.chain_count == 2, "Momentum did not preserve a clean string")
    style_switch_score = momentum.score
    momentum.register_parry()
    check(momentum.score > style_switch_score, "Momentum did not reward a clean parry")

    momentum.register_damage_taken()
    check(momentum.chain_count == 0, "Momentum did not break after taking damage")
    momentum.update(10)
    check(momentum.score < style_switch_score, "Momentum presentation score did not decay")

    screen = pygame.Surface((WIDTH, HEIGHT))
    draw_combat_momentum(screen, momentum)


def check_input_binding_foundation():
    """Load default actions, persist safe overrides, and route custom controls."""
    required_actions = {
        "move_left",
        "move_right",
        "jump",
        "dash",
        "attack",
        "kick",
        "skill_1",
        "skill_2",
        "skill_3",
        "pause",
        "help",
        "confirm",
        "back",
        "retry",
        "select_guide",
        "select_preview",
    }
    check(required_actions <= DEFAULT_KEY_BINDINGS.keys(), "Required default input actions are missing")

    defaults = InputManager()
    check(defaults.get_binding_label("move_left") == "A", "Default move-left label changed")
    check(defaults.get_binding_label("dash") == "Shift", "Default dash label changed")
    check(defaults.get_binding_label("kick") == "C", "Default kick label changed")
    check(defaults.get_binding_label("select_preview") == "6", "Default preview label changed")
    check(
        defaults.was_pressed("confirm", [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]),
        "InputManager did not detect a default press event",
    )

    settings_path = PROJECT_ROOT / "data" / "input-smoke.tmp"
    try:
        try:
            settings_path.unlink(missing_ok=True)
        except OSError:
            pass
        store = SettingsStore(settings_path)
        store.set(
            "key_bindings",
            {
                "move_left": "left",
                "attack": "x",
                "pause": "space",
                "help": "f1",
                "confirm": "e",
                "retry": "t",
                "skill_1": "q",
            },
        )
        reloaded_store = SettingsStore(settings_path)
        bindings = reloaded_store.get("key_bindings")
        check(bindings["attack"] == "x", "Input binding override did not persist")
        check(bindings["skill_2"] == "i", "Missing binding did not preserve its default")
        manager = InputManager(reloaded_store.settings)
    finally:
        try:
            settings_path.unlink(missing_ok=True)
        except OSError:
            pass

    check(manager.get_binding_label("attack") == "X", "Custom attack label did not load")
    check(manager.get_binding_label("pause") == "SPACE", "Custom pause label did not load")
    check(
        manager.event_matches("attack", pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x)),
        "Custom attack event did not route",
    )
    held_keys = defaultdict(bool, {pygame.K_LEFT: True})
    check(manager.is_pressed("move_left", held_keys), "Custom held movement binding did not route")

    invalid = InputManager({"key_bindings": {"attack": "not-a-real-key"}})
    check(invalid.get_binding_label("attack") == "J", "Invalid binding did not fall back safely")

    kick_solo = SoloMode()
    kick_solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    finish_solo_intro(kick_solo)
    kick_solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c))
    check(kick_solo.player.attack_style == "kick", "Default Solo C binding did not start the kick combo")

    kick_dungeon = DungeonMode()
    kick_dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c))
    check(kick_dungeon.player.attack_style == "kick", "Default Dungeon C binding did not start the kick combo")

    solo = SoloMode(input_manager=manager)
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
    finish_solo_intro(solo)
    check(solo.is_active(), "Custom Solo confirm binding did not start the fight")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x))
    check(solo.player.is_attacking, "Custom Solo attack binding did not start an attack")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    check(solo.paused, "Custom Solo pause binding did not open pause")
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_t))
    finish_solo_intro(solo)
    check(solo.is_active() and not solo.paused, "Custom Solo retry binding did not restart from pause")

    dungeon = DungeonMode(input_manager=manager)
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
    check(dungeon.controls_visible, "Custom Dungeon help binding did not open controls")
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
    dungeon.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    check(dungeon.paused, "Custom Dungeon pause binding did not open pause")


def check_enemy_sprite_validation():
    """Validate prototype sheet metadata, cutting, and missing-file safety."""
    check(
        set(ENEMY_SPRITE_CONFIGS) == {"orc", "soldier", "slime", "orc2", "orc3"},
        "Enemy sprite prototype ids changed",
    )
    reports = validate_enemy_sprites()
    check(len(reports) == 5, "Enemy sprite validator did not inspect every prototype")
    for report in reports:
        statuses = {animation["status"] for animation in report["animations"]}
        check(statuses <= {"OK", "MISSING"}, "Enemy sprite report contains an unexpected validation error")
        check(report["valid"] == (statuses == {"OK"}), "Enemy sprite report validity summary is inconsistent")

    orc_config = ENEMY_SPRITE_CONFIGS["orc"]
    idle_config = orc_config["animations"]["idle"]
    idle_sheet = pygame.Surface((idle_config["frame_count"] * orc_config["frame_width"], orc_config["frame_height"]))
    frames = cut_sheet_frames(
        idle_sheet,
        orc_config["frame_width"],
        orc_config["frame_height"],
        idle_config["frame_count"],
    )
    check(len(frames) == idle_config["frame_count"], "Enemy sprite sheet cutter returned the wrong frame count")
    check(frames[0].get_size() == (100, 100), "Enemy sprite sheet cutter returned the wrong frame size")

    orc2_config = ENEMY_SPRITE_CONFIGS["orc2"]
    orc2_idle = orc2_config["animations"]["idle"]
    orc2_sheet = pygame.Surface(
        (
            orc2_idle["frame_count"] * orc2_config["frame_width"],
            orc2_idle["sheet_rows"] * orc2_config["frame_height"],
        )
    )
    orc2_frames = cut_sheet_frames(
        orc2_sheet,
        orc2_config["frame_width"],
        orc2_config["frame_height"],
        orc2_idle["frame_count"],
        orc2_idle["sheet_row"],
    )
    check(len(orc2_frames) == 4, "Directional Orc sprite cutter returned the wrong frame count")
    check(orc2_frames[0].get_size() == (64, 64), "Directional Orc sprite cutter returned the wrong frame size")

    missing_config = {
        "enemy_id": "missing_test",
        "root_folder": PROJECT_ROOT / "assets" / "sprites" / "missing-test-only",
        "frame_width": 100,
        "frame_height": 100,
        "animations": {
            "idle": {
                "filename": "Missing-Idle.png",
                "frame_count": 1,
                "frame_speed": 0.1,
                "hold_last": False,
            },
        },
    }
    missing_report = validate_sprite_config(missing_config)
    check(not missing_report["valid"], "Missing enemy sprite file unexpectedly validated")
    check(missing_report["animations"][0]["status"] == "MISSING", "Missing enemy sprite file did not report safely")


def check_dungeon_enemy_sprite_integration():
    """Exercise prototype Dungeon sprite mapping, playback, and fallback."""
    renderer = EnemySpriteRenderer()
    basic_enemy = BasicEnemy(420)
    fast_enemy = FastEnemy(520)
    slime_enemy = SlimeEnemy(570)
    orc2_enemy = OrcLevel2Enemy(620)
    orc3_enemy = OrcLevel3Enemy(670)
    elite_enemy = EliteEnemy(720)
    check(renderer.get_sprite_id(basic_enemy) == "orc", "BasicEnemy did not map to the Orc prototype")
    check(renderer.get_sprite_id(fast_enemy) == "soldier", "FastEnemy did not map to the Soldier prototype")
    check(renderer.get_sprite_id(slime_enemy) == "slime", "SlimeEnemy did not map to the Slime prototype")
    check(renderer.get_sprite_id(orc2_enemy) == "orc2", "OrcLevel2Enemy did not map to its prototype")
    check(renderer.get_sprite_id(orc3_enemy) == "orc3", "OrcLevel3Enemy did not map to its prototype")
    check(renderer.get_sprite_id(elite_enemy) is None, "Elite enemy should keep its existing visual")

    expected_animations = {
        "idle": ("orc", "idle"),
        "chase": ("orc", "walk"),
        "telegraph": ("orc", "attack_01"),
        "attack": ("orc", "attack_02"),
        "hurt": ("orc", "hurt"),
        "stagger": ("orc", "hurt"),
        "defeated": ("orc", "death"),
    }
    for visual_state, (sprite_id, animation_name) in expected_animations.items():
        check(
            renderer.get_animation_name(sprite_id, visual_state) == animation_name,
            f"Dungeon enemy sprite state did not map safely: {visual_state}",
        )
    check(renderer.get_animation_name("slime", "attack") == "attack", "Slime attack strip fallback failed")
    check(renderer.get_animation_name("slime", "hurt") == "idle", "Slime hurt strip fallback failed")
    check(renderer.get_animation_name("orc2", "attack") == "attack", "Orc 2 attack strip fallback failed")

    for animation_name, animation in ENEMY_SPRITE_CONFIGS["orc"]["animations"].items():
        renderer.frame_cache[("orc", animation_name)] = tuple(
            pygame.Surface((100, 100), pygame.SRCALPHA)
            for _ in range(animation["frame_count"])
        )
    renderer.update(basic_enemy, "idle", ENEMY_SPRITE_CONFIGS["orc"]["animations"]["idle"]["frame_speed"])
    check(renderer.playback[basic_enemy]["frame_index"] == 1, "Looping Dungeon enemy sprite did not advance")
    renderer.update(basic_enemy, "defeated", 10)
    check(renderer.playback[basic_enemy]["frame_index"] == 3, "Dungeon enemy death sprite did not hold its last frame")
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    basic_enemy.facing = -1
    check(renderer.draw(surface, basic_enemy, basic_enemy.rect, "idle"), "Dungeon enemy sprite draw failed")

    for animation_name, animation in ENEMY_SPRITE_CONFIGS["slime"]["animations"].items():
        renderer.frame_cache[("slime", animation_name)] = tuple(
            pygame.Surface((32, 32), pygame.SRCALPHA)
            for _ in range(animation["frame_count"])
        )
    renderer.update(slime_enemy, "defeated", 10)
    check(renderer.playback[slime_enemy]["frame_index"] == 5, "Slime death sprite did not hold its last frame")
    check(renderer.draw(surface, slime_enemy, slime_enemy.rect, "attack"), "Slime sprite draw failed")
    check(len(renderer.load_frames("orc2", "idle")) == 4, "Directional Orc 2 idle strip did not load")
    check(renderer.draw(surface, orc2_enemy, orc2_enemy.rect, "idle"), "Directional Orc 2 draw failed")
    check(len(renderer.load_frames("orc3", "idle")) == 4, "Directional Orc 3 idle strip did not load")
    check(renderer.draw(surface, orc3_enemy, orc3_enemy.rect, "idle"), "Directional Orc 3 draw failed")

    missing_renderer = EnemySpriteRenderer(
        {
            "missing": {
                "enemy_id": "missing",
                "root_folder": PROJECT_ROOT / "assets" / "sprites" / "missing-test-only",
                "frame_width": 100,
                "frame_height": 100,
                "render_scale": 1,
                "feet_anchor": (50, 60),
                "animations": {
                    "idle": {
                        "filename": "Missing-Idle.png",
                        "frame_count": 1,
                        "frame_speed": 0.1,
                        "hold_last": False,
                    },
                },
            },
        }
    )
    basic_enemy.dungeon_sprite_id = "missing"
    basic_enemy.dungeon_sprite_renderer = missing_renderer
    check(
        not missing_renderer.draw(surface, basic_enemy, basic_enemy.rect, "idle"),
        "Missing Dungeon enemy sprite did not return rectangle fallback",
    )
    basic_enemy.draw(surface)

    player = create_player(420)
    combat_enemy = BasicEnemy(player.rect.right + 10)
    combat_enemy.facing = -1
    combat_enemy.start_attack()
    start_health = player.health
    check(process_enemy_attacks([combat_enemy], player), "Basic enemy attack stopped connecting")
    check(player.health < start_health, "Basic enemy attack stopped damaging player")
    combat_enemy.take_damage(combat_enemy.health)
    check(combat_enemy.defeated, "Basic enemy can no longer be defeated")

    slime_player = create_player(420)
    slime_enemy = SlimeEnemy(slime_player.rect.right + 10)
    slime_enemy.facing = -1
    slime_enemy.start_attack()
    slime_start_health = slime_player.health
    check(process_enemy_attacks([slime_enemy], slime_player), "Slime enemy attack did not connect")
    check(slime_player.health < slime_start_health, "Slime enemy attack did not damage player")
    slime_enemy.take_damage(slime_enemy.health)
    check(slime_enemy.defeated, "Slime enemy can no longer be defeated")

    dungeon = DungeonMode()
    dungeon.encounter_manager.spawn_wave(0, dungeon.player)
    spawned_enemy = dungeon.encounter_manager.active_enemies[0]
    check(isinstance(spawned_enemy, SlimeEnemy), "Dungeon Wave 1 did not spawn the Slime prototype")
    check(
        spawned_enemy.dungeon_sprite_renderer is dungeon.enemy_sprite_renderer,
        "Dungeon encounter did not attach its sprite renderer",
    )
    dungeon.encounter_manager.spawn_wave(1, dungeon.player)
    check(
        any(isinstance(enemy, OrcLevel2Enemy) for enemy in dungeon.encounter_manager.active_enemies),
        "Dungeon Wave 2 did not spawn Orc level 2",
    )
    dungeon.encounter_manager.spawn_wave(2, dungeon.player)
    check(
        any(isinstance(enemy, OrcLevel3Enemy) for enemy in dungeon.encounter_manager.active_enemies),
        "Dungeon Wave 3 did not spawn Orc level 3",
    )


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


def check_goku_player_sprite_integration():
    """Exercise approved Goku frame groups, Solo intro, and Dungeon fallback wiring."""
    renderer = GokuPlayerSpriteRenderer()
    expected_counts = {
        "intro_entry": 4,
        "fight_ready": 4,
        "idle_hold": 1,
        "victory": 1,
        "walk": 4,
        "run": 4,
        "jump": 6,
        "guard": 4,
        "attack_punch_1": 3,
        "super_saiyan_punch_1": 3,
        "attack_punch_2": 2,
        "super_saiyan_punch_2": 2,
        "attack_punch_3": 4,
        "super_saiyan_punch_3": 4,
        "attack_punch_4": 3,
        "super_saiyan_punch_4": 3,
        "attack_punch_5": 2,
        "super_saiyan_punch_5": 2,
        "punch_recovery": 2,
        "kick_1": 3,
        "super_saiyan_kick_1": 3,
        "kick_2": 3,
        "super_saiyan_kick_2": 3,
        "kick_3": 5,
        "super_saiyan_kick_3": 5,
        "kick_recovery_1": 2,
        "hurt_1": 2,
        "hurt_2": 1,
        "hurt_3": 1,
        "hurt_4": 1,
        "defeated": 2,
        "skill_1_shot_1": 2,
        "skill_1_shot_2": 2,
        "skill_1_shot_3": 2,
        "skill_2": 9,
        "super_saiyan_skill_2": 5,
        "skill_3": 4,
        "super_saiyan_transform": 10,
        "super_saiyan_idle": 1,
    }
    check(renderer.has_frames(), "Approved Goku fallback frames did not load")
    check(set(renderer.frames) == set(expected_counts), "Approved Goku action catalog changed")
    for action_id, expected_count in expected_counts.items():
        check(len(renderer.frames[action_id]) == expected_count, f"Goku {action_id} frame count changed")
        check(action_id in GOKU_PLAYER_ANIMATION_CONFIG, f"Goku {action_id} config is missing")

    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    player = create_player()
    intro_config = GOKU_PLAYER_ANIMATION_CONFIG["intro_entry"]
    check(not intro_config["loop"], "Goku intro entry unexpectedly loops")
    check(
        intro_config["frame_delay"] * 4 == SOLO_INTRO_ENTRY_DURATION,
        "Goku intro entry frames do not end exactly when FIGHT appears",
    )
    renderer.update(player, "idle", 0, "intro_entry")
    renderer.update(player, "idle", intro_config["frame_delay"], "intro_entry")
    check(renderer.get_playback(player)["frame_index"] == 1, "Goku intro playback did not advance")
    check(renderer.resolve_action("idle") == "idle_hold", "Goku idle did not hold R01-08")
    check(renderer.resolve_action("run") == "walk", "Goku normal movement did not map to walk")
    check(renderer.resolve_action("dash") == "run", "Goku dash did not map to run")
    check(renderer.resolve_action("jump") == "jump", "Goku jump did not map to R04")
    check(renderer.resolve_action("punch_1") == "attack_punch_1", "Goku punch hit 1 did not map to R06")
    check(renderer.resolve_action("punch_5") == "attack_punch_5", "Goku punch hit 5 did not map to R06")
    check(renderer.resolve_action("kick_1") == "kick_1", "Goku kick hit 1 did not map to R07")
    check(renderer.resolve_action("kick_3") == "kick_3", "Goku kick hit 3 did not map to R07")
    check(renderer.resolve_action("kick_recovery_1") == "kick_recovery_1", "Goku kick recovery did not map to R04")
    check(renderer.resolve_action("hurt") == "hurt_1", "Goku hurt fallback did not map to R09-01..02")
    check(renderer.resolve_action("hurt_4") == "hurt_4", "Goku fourth hurt did not map to R09-05")
    check(renderer.resolve_action("defeated") == "defeated", "Goku defeat did not map to R09-06..07")
    check(renderer.resolve_action("block") == "guard", "Goku guard mapping changed")
    check(
        renderer.resolve_action("skill_1") == GOKU_KI_BLAST_ACTION_IDS[0],
        "Goku Skill 1 fallback mapping changed",
    )
    check(renderer.resolve_action("skill_2") == "skill_2", "Goku Kamehameha mapping changed")
    check(
        renderer.resolve_action("super_saiyan_skill_2") == "super_saiyan_skill_2",
        "Super Saiyan Kamehameha body did not map to its R21 frames",
    )
    check(renderer.resolve_action("skill_3") == "skill_3", "Goku Energy Disc mapping changed")
    check(
        renderer.resolve_action("super_saiyan_transform") == "super_saiyan_transform",
        "Goku transformation did not map to R22-01..10",
    )
    check(
        renderer.resolve_action("super_saiyan_idle") == "super_saiyan_idle",
        "Goku powered idle did not map to R22-11",
    )
    check(renderer.draw(surface, player, player.rect, "idle") is not None, "Goku player draw failed")

    hurt_player = create_player()
    check(hurt_player.take_damage(1), "Goku first hurt setup did not apply")
    check(get_player_visual_state(hurt_player) == "hurt_1", "Goku first hurt did not select R09-01..02")
    renderer.update(hurt_player, get_player_visual_state(hurt_player), 0)
    renderer.update(hurt_player, get_player_visual_state(hurt_player), GOKU_PLAYER_ANIMATION_CONFIG["hurt_1"]["frame_delay"])
    check(renderer.get_playback(hurt_player)["frame_index"] == 1, "Goku first hurt did not advance to R09-02")
    for expected_step in range(2, 5):
        hurt_player.invulnerability_timer = 0
        check(hurt_player.take_damage(1), f"Goku connected hurt {expected_step} did not apply")
        check(
            get_player_visual_state(hurt_player) == f"hurt_{expected_step}",
            f"Goku connected hurt {expected_step} did not advance its R09 frame",
        )
    hurt_player.invulnerability_timer = 0
    check(hurt_player.take_damage(1), "Goku fifth connected hurt did not apply")
    check(get_player_visual_state(hurt_player) == "hurt_4", "Goku hurt chain did not clamp at R09-05")
    hurt_player.update_hurt_timers(PLAYER_HURT_VISUAL_HOLD_DURATION)
    check(get_player_visual_state(hurt_player) == "idle", "Goku hurt chain did not return to R01-08 after no hit")
    hurt_player.update_hurt_timers(PLAYER_HURT_CHAIN_RESET_TIME)
    check(hurt_player.hurt_chain_step == 0, "Goku hurt chain did not reset after its timeout")

    recovered_player = create_player()
    check(recovered_player.take_damage(1), "Goku recovered-action hurt setup did not apply")
    recovered_player.update_hurt_timers(PLAYER_HURT_DURATION)
    recovered_player.start_light_attack()
    check(
        get_player_visual_state(recovered_player) == "punch_1",
        "Residual Goku hurt pose hid a recovered player attack",
    )

    defeated_player = create_player()
    defeated_player.health = 1
    check(defeated_player.take_damage(1), "Goku lethal hurt setup did not apply")
    check(get_player_visual_state(defeated_player) == "defeated", "Goku lethal hurt did not select R09-06..07")
    renderer.update(defeated_player, "defeated", 0)
    renderer.update(defeated_player, "defeated", GOKU_PLAYER_ANIMATION_CONFIG["defeated"]["frame_delay"])
    check(renderer.get_playback(defeated_player)["frame_index"] == 1, "Goku defeat did not advance to R09-07")

    missing_renderer = GokuPlayerSpriteRenderer(PROJECT_ROOT / "assets" / "sprites" / "missing-test-only")
    check(not missing_renderer.has_frames(), "Missing Goku sprite folder unexpectedly loaded")
    check(
        missing_renderer.draw(surface, player, player.rect, "idle") is None,
        "Missing Goku frames did not preserve placeholder fallback",
    )

    solo = SoloMode()
    solo.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    check(solo.get_player_action_override() == "intro_entry", "Solo intro did not select R01-01 through R01-04")
    solo.update_intro(SOLO_INTRO_ENTRY_DURATION)
    check(solo.get_player_action_override() == "fight_ready", "Solo FIGHT did not select R01-05 through R01-08")
    solo.update_intro(SOLO_FIGHT_CALLOUT_DURATION)
    check(solo.is_active(), "Solo intro did not release combat")
    solo.enemy.defeated = True
    solo.update_result_state()
    check(solo.get_player_action_override() == "victory", "Solo victory did not select R01-09")

    dungeon = DungeonMode()
    check(
        dungeon.player.player_sprite_renderer is dungeon.player_sprite_renderer,
        "Dungeon player did not attach the approved Goku renderer",
    )


def check_player_melee_combo_sequences():
    """Keep queued R06/R07 playback continuous and preserve stop-only recovery."""
    punch_player = create_player()
    punch_player.start_light_attack()
    check(get_player_visual_state(punch_player) == "punch_1", "Punch combo did not start at R06-01..03")
    for expected_step in range(2, len(LIGHT_ATTACK_COMBO) + 1):
        punch_player.start_light_attack()
        punch_player.update_attack_timers(punch_player.attack_duration)
        check(punch_player.is_attacking, f"Punch combo inserted idle before hit {expected_step}")
        check(punch_player.combo_step == expected_step, f"Punch combo did not advance to hit {expected_step}")
        check(
            get_player_visual_state(punch_player) == f"punch_{expected_step}",
            f"Punch combo visual did not stay on the continuous R06 stream at hit {expected_step}",
        )
    punch_player.update_attack_timers(punch_player.attack_duration)
    check(not punch_player.is_attacking, "Punch combo did not stop after hit 5")
    check(get_player_visual_state(punch_player) == "punch_recovery", "Punch finisher did not play R02-01..02")

    kick_player = create_player()
    kick_player.start_kick_attack()
    check(get_player_visual_state(kick_player) == "kick_1", "Kick combo did not start at R07-01..03")
    launch_enemy = BasicEnemy(kick_player.rect.right + 1)
    check(process_player_attack(kick_player, launch_enemy), "Kick hit 1 did not connect")
    check(launch_enemy.knockback_velocity_y < 0, "Kick hit 1 did not launch the enemy")
    launch_enemy.update_knockback(0.10)
    check(launch_enemy.rect.y < launch_enemy.launch_ground_y, "Launched enemy did not leave the ground")

    for expected_step in range(2, len(KICK_ATTACK_COMBO) + 1):
        kick_player.start_kick_attack()
        kick_player.update_attack_timers(kick_player.attack_duration)
        check(kick_player.is_attacking, f"Kick combo inserted idle before hit {expected_step}")
        check(kick_player.combo_step == expected_step, f"Kick combo did not advance to hit {expected_step}")
        check(get_player_visual_state(kick_player) == f"kick_{expected_step}", "Kick visual sequence broke")
    check(kick_player.attack_knockback == KICK_ATTACK_COMBO[2]["knockback"], "Kick hit 3 pushback changed")
    kick_player.update_attack_timers(kick_player.attack_duration)
    check(not kick_player.is_attacking, "Kick combo did not return to idle after hit 3")

    stopped_kick_player = create_player()
    stopped_kick_player.start_kick_attack()
    stopped_kick_player.update_attack_timers(stopped_kick_player.attack_duration)
    check(
        get_player_visual_state(stopped_kick_player) == "kick_recovery_1",
        "Stopped kick hit 1 did not play R04-07..08",
    )


def check_super_saiyan_burst():
    """Charge, transform, drain, and double every player damage route."""
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    player = create_player()
    player.add_saiyan_energy(SUPER_SAIYAN_MAX_ENERGY)
    check(player.is_super_saiyan, "Full SAIYAN gauge did not auto-transform")
    check(player.is_transforming(), "Super Saiyan did not enter its R22 transformation lock")
    check(
        get_player_visual_state(player) == "super_saiyan_transform",
        "Super Saiyan transformation did not select R22-01..10",
    )
    player.start_light_attack()
    check(not player.is_attacking, "Transformation lock allowed melee input")
    SkillManager(ProjectileManager()).use_slot(1, player)
    check(not player.skill_visual_state, "Transformation lock allowed skill input")
    player.draw(surface)

    player.update_super_saiyan(SUPER_SAIYAN_TRANSFORM_DURATION)
    check(not player.is_transforming(), "Super Saiyan transformation lock did not expire")
    check(get_player_visual_state(player) == "super_saiyan_idle", "Powered idle did not select R22-11")
    check(player.super_saiyan_damage_multiplier == SUPER_SAIYAN_DAMAGE_MULTIPLIER, "Super Saiyan multiplier changed")

    melee_enemy = BasicEnemy(player.rect.right + 1)
    player.start_light_attack()
    check(
        get_player_visual_state(player) == "super_saiyan_punch_1",
        "Super Saiyan melee fell back to base-form punch frames",
    )
    check(process_player_attack(player, melee_enemy), "Super Saiyan melee did not connect")
    check(
        melee_enemy.health == BASIC_ENEMY_CONFIG["max_health"] - LIGHT_ATTACK_COMBO[0]["damage"] * 2,
        "Super Saiyan melee did not deal x2 damage",
    )

    counter_player = create_player()
    counter_player.add_saiyan_energy(SUPER_SAIYAN_MAX_ENERGY)
    counter_player.update_super_saiyan(SUPER_SAIYAN_TRANSFORM_DURATION)
    counter_player.can_counter = True
    counter_player.counter_window_timer = 1.0
    counter_player.start_light_attack()
    counter_enemy = BasicEnemy(counter_player.rect.right + 1)
    check(process_player_attack(counter_player, counter_enemy), "Super Saiyan counter did not connect")
    check(
        counter_enemy.health == BASIC_ENEMY_CONFIG["max_health"] - COUNTER_ATTACK["damage"] * 2,
        "Super Saiyan counter did not deal x2 damage",
    )

    skill_player = create_player()
    skill_player.add_saiyan_energy(SUPER_SAIYAN_MAX_ENERGY)
    skill_player.update_super_saiyan(SUPER_SAIYAN_TRANSFORM_DURATION)
    projectiles = ProjectileManager()
    skills = SkillManager(projectiles)
    check(skills.use_slot(1, skill_player), "Super Saiyan Ki Blast could not start")
    check(projectiles.projectiles[0].damage == KI_BLAST_CONFIG["damage"] * 2, "Super Saiyan Ki Blast did not deal x2")
    check(skills.use_slot(2, skill_player), "Super Saiyan Kamehameha could not start")
    check(
        skill_player.skill_visual_state == "super_saiyan_skill_2",
        "Super Saiyan Kamehameha did not select its SSJ body frames",
    )
    check(
        projectiles.pending_kamehamehas[0]["damage"] == KAMEHAMEHA_CONFIG["damage"] * 2,
        "Super Saiyan Kamehameha did not deal x2",
    )
    projectiles.update(KAMEHAMEHA_CONFIG["windup_duration"] - 0.01, [])
    check(not projectiles.beams, "Super Saiyan Kamehameha released before its SSJ windup finished")
    projectiles.update(0.02, [])
    check(projectiles.beams, "Super Saiyan Kamehameha did not release after its SSJ windup")
    check(
        projectiles.beams[0].sprite_path == GOKU_SUPER_SAIYAN_KAMEHAMEHA_EFFECT_PATH,
        "Super Saiyan Kamehameha did not use its SSJ beam PNG",
    )
    check(skills.use_slot(3, skill_player), "Super Saiyan Energy Disc could not start")
    check(
        projectiles.pending_energy_discs[0]["damage"] == ENERGY_DISC_CONFIG["damage"] * 2,
        "Super Saiyan Energy Disc did not deal x2",
    )

    draining_player = create_player()
    draining_player.add_saiyan_energy(SUPER_SAIYAN_MAX_ENERGY)
    draining_player.update_super_saiyan(SUPER_SAIYAN_TRANSFORM_DURATION)
    draining_player.update_super_saiyan(SUPER_SAIYAN_DURATION)
    check(not draining_player.is_super_saiyan, "Super Saiyan did not return to base form after the burst")
    check(draining_player.saiyan_energy == 0, "Super Saiyan drain did not empty its gauge")


def check_projectile_and_beam():
    """Update and draw neutral projectile primitives safely."""
    surface = pygame.Surface((WIDTH, HEIGHT))
    projectile = Projectile(100, 100, 1, speed=200, damage=5, lifetime=0.10)
    projectile.update(0.05)
    projectile.draw(surface)
    check(projectile.active, "Projectile expired too early")
    projectile.update(0.05)
    check(not projectile.active, "Projectile did not expire")
    check(get_animation_dt({"animation_speed": 0.65}, 1.0) == 0.65, "Presentation animation speed did not apply")

    beam = Beam(100, 180, 1, beam_range=220, height=24, damage=8, duration=0.10)
    beam.draw(surface)
    beam.update(0.10)
    check(not beam.active, "Beam did not expire")

    player = create_player()
    enemy = BasicEnemy(player.rect.right + 10)
    projectiles = ProjectileManager()
    skills = SkillManager(projectiles)
    check(skills.use_slot(1, player), "Ki Blast could not be used")
    check(
        player.skill_visual_state == GOKU_KI_BLAST_ACTION_IDS[0],
        "Ki Blast did not select its first R10 shot pair",
    )
    check(
        projectiles.projectiles[0].sprite_path == GOKU_KI_BLAST_EFFECT_PATH,
        "Ki Blast did not use the approved yellow projectile",
    )
    check(projectiles.projectiles[0].load_sprite() is not None, "Ki Blast yellow projectile did not load")
    check(projectiles.projectiles[0].sprite_scale == 1.15, "Ki Blast render scale changed")
    projectiles.projectiles[0].draw(surface)
    ki_blast_sprite = projectiles.projectiles[0].load_sprite()
    check(
        projectiles.projectiles[0].get_transformed_sprite(ki_blast_sprite)
        is projectiles.projectiles[0].get_transformed_sprite(ki_blast_sprite),
        "Ki Blast render transform was not cached",
    )
    projectiles.update(0.001, [enemy])
    check(enemy.health == BASIC_ENEMY_CONFIG["max_health"] - KI_BLAST_CONFIG["damage"], "Ki Blast collision failed")
    check(player.saiyan_energy > 0, "Ki Blast collision did not charge the SAIYAN gauge")
    check(len(projectiles.impacts) == 1, "Ki Blast did not spawn its R13 impact")
    check(
        projectiles.impacts[0].sprite_paths == GOKU_PROJECTILE_IMPACT_EFFECT_PATHS,
        "Ki Blast impact did not use R13-03 and R13-04",
    )
    check(projectiles.impacts[0].load_sprite() is not None, "Ki Blast R13 impact did not load")

    far_projectiles = ProjectileManager()
    far_skills = SkillManager(far_projectiles)
    far_player = create_player(80)
    far_enemy = BasicEnemy(WIDTH - 100)
    check(far_skills.use_slot(1, far_player), "Long-range Ki Blast could not be used")
    for _ in range(120):
        far_projectiles.update(1 / 60, [far_enemy])
        if far_enemy.health < BASIC_ENEMY_CONFIG["max_health"]:
            break
    check(
        far_enemy.health == BASIC_ENEMY_CONFIG["max_health"] - KI_BLAST_CONFIG["damage"],
        "Ki Blast expired before reaching a distant enemy",
    )

    for expected_action in GOKU_KI_BLAST_ACTION_IDS[1:]:
        skills.get_slot(1).current_cooldown = 0
        check(skills.use_slot(1, player), "Repeated Ki Blast could not be used")
        check(player.skill_visual_state == expected_action, "Ki Blast R10 shot pairs did not rotate")

    disc_projectiles = ProjectileManager()
    disc_skills = SkillManager(disc_projectiles)
    disc_enemy = BasicEnemy(player.rect.right + 20)
    check(disc_skills.use_slot(3, player), "Energy Disc could not be used")
    check(player.skill_visual_state == "skill_3", "Energy Disc did not select its R12 body animation")
    check(not disc_projectiles.projectiles, "Energy Disc released before its R12 throw finished")
    check(len(disc_projectiles.pending_energy_discs) == 1, "Energy Disc throw was not queued")
    disc_projectiles.update(ENERGY_DISC_CONFIG["windup_duration"] - 0.01, [])
    check(not disc_projectiles.projectiles, "Energy Disc released during its R12 throw")
    disc_projectiles.update(0.01, [])
    check(len(disc_projectiles.projectiles) == 1, "Energy Disc did not release after R12-01..04")
    disc = disc_projectiles.projectiles[0]
    check(disc.sprite_paths == GOKU_ENERGY_DISC_EFFECT_PATHS, "Energy Disc did not use R12-05 and R12-06")
    check(disc.load_sprite() is not None, "Energy Disc first projectile frame did not load")
    disc.update(ENERGY_DISC_CONFIG["sprite_frame_delay"])
    check(disc.sprite_frame_index == 1, "Energy Disc projectile animation did not advance")
    check(disc.load_sprite() is not None, "Energy Disc second projectile frame did not load")
    disc_projectiles.update(0.001, [disc_enemy])
    check(
        disc_enemy.health == BASIC_ENEMY_CONFIG["max_health"] - ENERGY_DISC_CONFIG["damage"],
        "Energy Disc collision failed",
    )
    check(len(disc_projectiles.impacts) == 1, "Energy Disc did not spawn its R13 impact")

    kamehameha_projectiles = ProjectileManager()
    kamehameha_skills = SkillManager(kamehameha_projectiles)
    check(kamehameha_skills.use_slot(2, player), "Kamehameha could not be used")
    check(player.skill_visual_state == "skill_2", "Kamehameha did not select its R11 windup")
    check(not kamehameha_projectiles.beams, "Kamehameha released before its R11 windup")
    kamehameha_projectiles.update(KAMEHAMEHA_CONFIG["windup_duration"] - 0.01, [])
    check(not kamehameha_projectiles.beams, "Kamehameha released during its R11 windup")
    kamehameha_projectiles.update(0.01, [])
    check(len(kamehameha_projectiles.beams) == 1, "Kamehameha did not release after its R11 windup")
    check(
        kamehameha_projectiles.beams[0].sprite_path == GOKU_KAMEHAMEHA_EFFECT_PATH,
        "Kamehameha did not use the approved blue beam",
    )
    kamehameha_beam = kamehameha_projectiles.beams[0]
    check(kamehameha_beam.load_sprite() is not None, "Kamehameha blue beam did not load")
    source_beam_sprite = kamehameha_beam.load_sprite()
    extended_beam_sprite = kamehameha_beam.extend_sprite_body(source_beam_sprite, WIDTH)
    midpoint = source_beam_sprite.get_width() // 2
    check(
        extended_beam_sprite.subsurface((0, 0, midpoint, source_beam_sprite.get_height())).copy()
        .get_buffer()
        .raw
        == source_beam_sprite.subsurface((0, 0, midpoint, source_beam_sprite.get_height())).copy()
        .get_buffer()
        .raw,
        "Kamehameha left end changed shape while extending",
    )
    right_width = source_beam_sprite.get_width() - midpoint
    check(
        extended_beam_sprite.subsurface(
            (WIDTH - right_width, 0, right_width, source_beam_sprite.get_height())
        )
        .copy()
        .get_buffer()
        .raw
        == source_beam_sprite.subsurface(
            (midpoint, 0, right_width, source_beam_sprite.get_height())
        )
        .copy()
        .get_buffer()
        .raw,
        "Kamehameha right end changed shape while extending",
    )
    front_enemy = BasicEnemy(600)
    rear_enemy = BasicEnemy(700)
    kamehameha_beam.refresh_hitbox([front_enemy, rear_enemy])
    check(kamehameha_beam.rect.right == WIDTH, "Kamehameha did not extend through the arena")
    front_health = front_enemy.health
    rear_health = rear_enemy.health
    kamehameha_projectiles.apply_beam_collisions(kamehameha_beam, [front_enemy, rear_enemy])
    check(front_enemy.health == front_health - kamehameha_beam.damage, "Kamehameha missed its front target")
    check(rear_enemy.health == rear_health - kamehameha_beam.damage, "Kamehameha did not pierce its rear target")
    kamehameha_beam.draw(surface)
    cached_beam_sprite = kamehameha_beam.get_extended_sprite(source_beam_sprite, WIDTH)
    check(
        cached_beam_sprite is kamehameha_beam.get_extended_sprite(source_beam_sprite, WIDTH),
        "Kamehameha render extension was not cached",
    )

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
    finish_solo_intro(solo)
    start_player_energy = solo.energy
    start_boss_energy = solo.enemy.energy
    previous_player_health = solo.player.health
    previous_enemy_health = solo.enemy.health
    solo.player.health -= 1
    solo.enemy.health -= 1
    solo.apply_energy_from_health_changes(previous_player_health, previous_enemy_health)
    check(solo.energy == start_player_energy + 12, "Solo player damage-exchange energy gain failed")
    check(solo.enemy.energy == start_boss_energy + 12, "Solo boss damage-exchange energy gain failed")
    solo.energy = SOLO_KI_BLAST_ENERGY_COST
    check(solo.try_use_ki_blast(), "Solo Ki Blast did not start with enough energy")
    check(solo.energy == 0, "Solo Ki Blast did not spend its configured energy")
    check(
        solo.player.skill_visual_state == GOKU_KI_BLAST_ACTION_IDS[0],
        "Solo Ki Blast did not start its approved R10 shot pair",
    )
    solo.energy = SOLO_KAMEHAMEHA_ENERGY_COST
    check(solo.try_use_kamehameha(), "Solo Kamehameha did not start with enough energy")
    check(solo.energy == 0, "Solo Kamehameha did not spend its configured energy")
    solo.energy = SOLO_ENERGY_DISC_ENERGY_COST
    check(solo.try_use_energy_disc(), "Solo Energy Disc did not start with enough energy")
    check(solo.energy == 0, "Solo Energy Disc did not spend its configured energy")
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
        ("dungeon decor foundation", check_dungeon_decor_foundation),
        ("reward runtime", check_reward_runtime),
        ("mode lifecycle", check_modes_and_reward_flow),
        ("pause and controls QoL", check_pause_and_controls_qol),
        ("save and settings foundation", check_settings_foundation),
        ("audio hooks foundation", check_audio_hooks_foundation),
        ("combat momentum presentation", check_combat_momentum_presentation),
        ("input binding foundation", check_input_binding_foundation),
        ("enemy sprite asset validation", check_enemy_sprite_validation),
        ("dungeon enemy sprite integration", check_dungeon_enemy_sprite_integration),
        ("goku player sprite integration", check_goku_player_sprite_integration),
        ("player melee combo sequences", check_player_melee_combo_sequences),
        ("super saiyan burst", check_super_saiyan_burst),
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
