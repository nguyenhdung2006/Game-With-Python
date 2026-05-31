"""Player state initialization helpers."""

import pygame

from entities.player_parts.reaction import initialize_reaction_state
from settings import (
    COMBO_RESET_TIME,
    COUNTER_ATTACK,
    DASH_COOLDOWN,
    DASH_DURATION,
    DASH_SPEED,
    DASH_TRAIL_LIFETIME,
    GRAVITY,
    JUMP_STRENGTH,
    LIGHT_ATTACK_COMBO,
    PLAYER_ATTACK_BUFFER_DURATION,
    PLAYER_BLOCK_COLOR,
    PLAYER_BLOCK_DAMAGE_REDUCTION,
    PLAYER_BLOCK_FLASH_COLOR,
    PLAYER_BLOCK_FLASH_DURATION,
    PLAYER_BLOCK_MOVE_MULTIPLIER,
    PLAYER_BLOCK_PUSHBACK,
    PLAYER_COLOR,
    PLAYER_COUNTER_READY_COLOR,
    PLAYER_DODGE_COLOR,
    PLAYER_DODGE_COOLDOWN,
    PLAYER_DODGE_DURATION,
    PLAYER_DODGE_SPEED,
    PLAYER_HEIGHT,
    PLAYER_KNOCKBACK_FRICTION,
    PLAYER_MAX_HEALTH,
    PLAYER_PARRY_COLOR,
    PLAYER_PARRY_FLASH_COLOR,
    PLAYER_SPEED,
    PLAYER_WIDTH,
)


def initialize_player_state(player, x, y):
    """Populate the Player instance with all gameplay state fields."""
    initialize_core_state(player, x, y)
    initialize_attack_state(player)
    initialize_defense_state(player)
    initialize_mobility_state(player)
    initialize_reaction_state(player)


def initialize_core_state(player, x, y):
    """Set the basic body, movement, and shared state fields."""
    player.audio_manager = None
    player.width = PLAYER_WIDTH
    player.height = PLAYER_HEIGHT
    player.speed = PLAYER_SPEED
    player.health = PLAYER_MAX_HEALTH
    player.max_health = PLAYER_MAX_HEALTH
    player.max_health_bonus = 0
    player.damage_multiplier = 1.0
    player.skill_damage_multiplier = 1.0
    player.combo_finisher_damage_multiplier = 1.0
    player.damage_taken_multiplier = 1.0
    player.skill_cooldown_multiplier = 1.0
    player.stamina_regen_multiplier = 1.0
    player.defense_cost_multiplier = 1.0
    player.room_clear_heal = 0
    player.base_move_speed = PLAYER_SPEED
    player.move_speed_multiplier = 1.0
    player.rect = pygame.Rect(x, y, player.width, player.height)

    player.x = float(x)
    player.y = float(y)

    player.velocity_y = 0
    player.gravity = GRAVITY
    player.jump_strength = JUMP_STRENGTH
    player.grounded = True
    player.facing = 1
    player.last_move_direction = 0
    player.sprite_paths = {}
    player.sprite_size = (player.width, player.height)
    player.sprite_offset = (0, 0)
    player.sprite_flip_with_facing = True

    player.knockback_velocity_x = 0
    player.is_hurt = False
    player.defeated = False
    player.hurt_timer = 0
    player.hurt_flash_timer = 0
    player.invulnerability_timer = 0
    player.stun_timer = 0
    player.skill_lock_timer = 0


def initialize_attack_state(player):
    """Set combo, counter, and attack timing fields."""
    first_attack = LIGHT_ATTACK_COMBO[0]

    player.attack_damage = first_attack["damage"]
    player.attack_range = first_attack["range"]
    player.attack_height = first_attack["height"]
    player.attack_knockback = first_attack["knockback"]
    player.attack_movement_multiplier = first_attack["movement_multiplier"]
    player.attack_color = first_attack["color"]
    player.attack_hitstop = first_attack["hitstop"]
    player.attack_shake_duration = first_attack["shake_duration"]
    player.attack_shake_strength = first_attack["shake_strength"]

    player.attack_duration = first_attack["duration"]
    player.attack_timer = 0
    player.attack_recovery = first_attack["recovery"]
    player.attack_cancel_window = first_attack["cancel_window"]
    player.attack_recovery_timer = 0

    player.attack_cooldown = first_attack["cooldown"]
    player.attack_cooldown_timer = 0
    player.is_attacking = False
    player.is_counter_attacking = False
    player.has_hit_this_attack = False

    player.combo_step = 0
    player.combo_timer = 0
    player.combo_reset_time = COMBO_RESET_TIME
    player.queued_next_attack = False
    player.attack_buffer_timer = 0
    player.buffered_attack = False
    player.counter_window_timer = 0
    player.can_counter = False
    player.counter_ready_color = PLAYER_COUNTER_READY_COLOR
    player.attack_buffer_duration = PLAYER_ATTACK_BUFFER_DURATION


def initialize_defense_state(player):
    """Set block and parry state."""
    player.is_blocking = False
    player.block_direction = player.facing
    player.block_damage_reduction = PLAYER_BLOCK_DAMAGE_REDUCTION
    player.block_pushback = PLAYER_BLOCK_PUSHBACK
    player.block_stamina = 100
    player.block_flash_timer = 0
    player.block_flash_duration = PLAYER_BLOCK_FLASH_DURATION
    player.block_move_multiplier = PLAYER_BLOCK_MOVE_MULTIPLIER
    player.block_color = PLAYER_BLOCK_COLOR
    player.block_flash_color = PLAYER_BLOCK_FLASH_COLOR
    player.parry_color = PLAYER_PARRY_COLOR
    player.parry_flash_color = PLAYER_PARRY_FLASH_COLOR

    player.is_parrying = False
    player.parry_window_timer = 0
    player.parry_cooldown_timer = 0
    player.successful_parry_timer = 0


def initialize_mobility_state(player):
    """Set dash, dodge, landing, and trail state."""
    player.base_dash_speed = DASH_SPEED
    player.dash_speed_multiplier = 1.0
    player.dash_speed = DASH_SPEED
    player.dash_duration = DASH_DURATION
    player.dash_timer = 0
    player.base_dash_cooldown = DASH_COOLDOWN
    player.dash_cooldown_multiplier = 1.0
    player.dash_cooldown = DASH_COOLDOWN
    player.dash_cooldown_timer = 0
    player.is_dashing = False

    player.dash_trail = []
    player.trail_lifetime = DASH_TRAIL_LIFETIME

    player.is_dodging = False
    player.dodge_timer = 0
    player.dodge_duration = PLAYER_DODGE_DURATION
    player.dodge_cooldown = PLAYER_DODGE_COOLDOWN
    player.dodge_cooldown_timer = 0
    player.dodge_invulnerability_timer = 0
    player.dodge_direction = player.facing
    player.dodge_speed = PLAYER_DODGE_SPEED
    player.dodge_color = PLAYER_DODGE_COLOR
    player.dodge_recovery_timer = 0

    player.landing_recovery_timer = 0
    player.knockback_friction = PLAYER_KNOCKBACK_FRICTION
