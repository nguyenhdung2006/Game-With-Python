"""Base enemy state initialization helpers."""

import pygame

from entities.enemy_parts.reaction import initialize_reaction_state
from settings import ENEMY_STATE_IDLE, GROUND_Y


def initialize_enemy_state(enemy, x, y, config):
    """Populate a BaseEnemy instance from one archetype config."""
    enemy.audio_manager = None
    enemy.config = config
    enemy.label = config["label"]
    enemy.width = config["width"]
    enemy.height = config["height"]
    enemy.max_health = config["max_health"]
    enemy.health = config["max_health"]

    if y is None:
        y = GROUND_Y - enemy.height

    enemy.rect = pygame.Rect(x, y, enemy.width, enemy.height)
    enemy.x = float(x)
    enemy.y = float(y)
    enemy.launch_ground_y = float(y)

    enemy.hurt_flash_duration = config["hurt_flash_duration"]
    enemy.knockback_friction = config["knockback_friction"]
    enemy.chase_speed = config["chase_speed"]
    enemy.attack_start_distance = config["attack_start_distance"]
    enemy.telegraph_duration = config["telegraph_duration"]
    enemy.attack_duration = config["attack_duration"]
    enemy.attack_cooldown = config["attack_cooldown"]
    enemy.attack_damage = config["attack_damage"]
    enemy.attack_range = config["attack_range"]
    enemy.attack_height = config["attack_height"]
    enemy.attack_knockback = config["attack_knockback"]
    enemy.retreat_duration = config["retreat_duration"]
    enemy.retreat_speed = config["retreat_speed"]
    enemy.attack_hitstop = config["attack_hitstop"]
    enemy.attack_shake_duration = config["attack_shake_duration"]
    enemy.attack_shake_strength = config["attack_shake_strength"]
    enemy.recovery_duration = config["recovery_duration"]
    enemy.stagger_duration = config["stagger_duration"]

    enemy.body_color = config["body_color"]
    enemy.hurt_color = config["hurt_color"]
    enemy.defeated_color = config["defeated_color"]
    enemy.telegraph_color = config["telegraph_color"]
    enemy.attack_color = config["attack_color"]
    enemy.telegraph_pulse_speed = config["telegraph_pulse_speed"]
    enemy.recoil_outline_color = config["recoil_outline_color"]

    enemy.hurt_flash_timer = 0
    enemy.knockback_velocity_x = 0
    enemy.knockback_velocity_y = 0
    enemy.launch_gravity = 2200
    enemy.defeated = False
    enemy.facing = -1
    enemy.sprite_paths = config.get("sprite_paths", {})
    enemy.sprite_size = config.get("sprite_size", (enemy.width, enemy.height))
    enemy.sprite_offset = config.get("sprite_offset", (0, 0))
    enemy.sprite_flip_with_facing = config.get("sprite_flip_with_facing", True)
    enemy.dungeon_sprite_renderer = None

    enemy.state = ENEMY_STATE_IDLE
    enemy.telegraph_timer = 0
    enemy.attack_timer = 0
    enemy.attack_cooldown_timer = 0
    enemy.has_hit_this_attack = False
    enemy.retreat_timer = 0
    enemy.recovery_timer = 0
    enemy.stagger_timer = 0

    # Presentation-state timers let the encounter director stage entrances and
    # pressure communication without changing the combat rules themselves.
    enemy.spawn_target_x = enemy.rect.x
    enemy.entrance_delay_timer = 0
    enemy.entrance_pause_timer = 0
    enemy.entrance_move_speed = 0
    enemy.pressure_indicator_timer = 0
    enemy.aggression_focus_timer = 0

    initialize_reaction_state(enemy, config)
