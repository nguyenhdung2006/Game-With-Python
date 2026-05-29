"""Shared game settings.

This file keeps numbers and colors in one place so gameplay code can stay
focused on behavior instead of scattered magic values.
"""

# Window settings
WIDTH = 1280
HEIGHT = 720
FPS = 60

# World settings
GROUND_Y = 540
ENCOUNTER_WAVE_DELAY = 1.10
ENCOUNTER_STATUS_Y = 126

# Player settings
PLAYER_WIDTH = 54
PLAYER_HEIGHT = 118
PLAYER_SPEED = 360
PLAYER_MAX_HEALTH = 100
PLAYER_HURT_DURATION = 0.20
PLAYER_HURT_FLASH_DURATION = 0.12
PLAYER_INVULNERABILITY_DURATION = 0.65
PLAYER_KNOCKBACK_FRICTION = 1800
PLAYER_HURT_COLOR = (255, 235, 245)
PLAYER_INVULNERABLE_COLOR = (155, 225, 255)
PLAYER_DEFEATED_COLOR = (45, 55, 70)
PLAYER_BLOCK_MOVE_MULTIPLIER = 0.38
PLAYER_BLOCK_DAMAGE_REDUCTION = 0.35
PLAYER_BLOCK_PUSHBACK = 125
PLAYER_BLOCK_FLASH_DURATION = 0.10
PLAYER_BLOCK_HITSTOP = 0.020
PLAYER_BLOCK_SHAKE_DURATION = 0.06
PLAYER_BLOCK_SHAKE_STRENGTH = 1
PLAYER_BLOCK_COLOR = (110, 210, 255)
PLAYER_BLOCK_FLASH_COLOR = (235, 255, 255)
PLAYER_PARRY_WINDOW_DURATION = 0.16
PLAYER_PARRY_COOLDOWN = 0.18
PLAYER_PARRY_SUCCESS_DURATION = 0.16
PLAYER_PARRY_HITSTOP = 0.060
PLAYER_PARRY_SHAKE_DURATION = 0.14
PLAYER_PARRY_SHAKE_STRENGTH = 5
PLAYER_PARRY_COLOR = (255, 245, 180)
PLAYER_PARRY_FLASH_COLOR = (255, 255, 255)
PLAYER_COUNTER_WINDOW_DURATION = 0.72
PLAYER_COUNTER_READY_COLOR = (255, 236, 165)
PLAYER_DODGE_SPEED = 820
PLAYER_DODGE_DURATION = 0.12
PLAYER_DODGE_COOLDOWN = 0.45
PLAYER_DODGE_INVULNERABILITY_DURATION = 0.16
PLAYER_DODGE_SHAKE_DURATION = 0.05
PLAYER_DODGE_SHAKE_STRENGTH = 1
PLAYER_DODGE_COLOR = (190, 240, 255)
PLAYER_DODGE_RECOVERY_DURATION = 0.10
PLAYER_LANDING_RECOVERY_DURATION = 0.05
PLAYER_HARD_LANDING_RECOVERY_DURATION = 0.10
PLAYER_HARD_LANDING_SPEED = 700
PLAYER_ATTACK_BUFFER_DURATION = 0.12

# Physics settings
GRAVITY = 2200
JUMP_STRENGTH = 850

# Dash settings
DASH_SPEED = 1050
DASH_DURATION = 0.16
DASH_COOLDOWN = 0.55
DASH_TRAIL_LIFETIME = 0.18

# Enemy settings
ENEMY_WIDTH = 54
ENEMY_HEIGHT = 118
ENEMY_MAX_HEALTH = 100
ENEMY_HURT_FLASH_DURATION = 0.12
ENEMY_KNOCKBACK_FRICTION = 1600
ENEMY_CHASE_SPEED = 135
ENEMY_ATTACK_START_DISTANCE = 92
ENEMY_TELEGRAPH_DURATION = 0.40
ENEMY_ATTACK_DURATION = 0.20
ENEMY_ATTACK_COOLDOWN = 1.00
ENEMY_ATTACK_DAMAGE = 8
ENEMY_ATTACK_RANGE = 72
ENEMY_ATTACK_HEIGHT = 62
ENEMY_ATTACK_KNOCKBACK = 220
ENEMY_RETREAT_DURATION = 0.35
ENEMY_RETREAT_SPEED = 105
ENEMY_ATTACK_HITSTOP = 0.035
ENEMY_ATTACK_SHAKE_DURATION = 0.08
ENEMY_ATTACK_SHAKE_STRENGTH = 2
ENEMY_TELEGRAPH_COLOR = (255, 205, 80)
ENEMY_ATTACK_COLOR = (255, 120, 95)
ENEMY_RECOVERY_DURATION = 0.25
ENEMY_STAGGER_DURATION = 0.52
ENEMY_COUNTER_STAGGER_DURATION = 0.45

# Enemy state names
ENEMY_STATE_IDLE = "IDLE"
ENEMY_STATE_CHASE = "CHASE"
ENEMY_STATE_TELEGRAPH = "TELEGRAPH"
ENEMY_STATE_ATTACK = "ATTACK"
ENEMY_STATE_HURT = "HURT"
ENEMY_STATE_STAGGER = "STAGGER"
ENEMY_STATE_DEFEATED = "DEFEATED"

# Enemy archetype configs keep each enemy type readable and scalable.
# BaseEnemy reads one of these dictionaries so future archetypes can add
# variety without duplicating the whole AI state machine.
BASIC_ENEMY_CONFIG = {
    "label": "BASIC ENEMY",
    "width": ENEMY_WIDTH,
    "height": ENEMY_HEIGHT,
    "max_health": ENEMY_MAX_HEALTH,
    "hurt_flash_duration": ENEMY_HURT_FLASH_DURATION,
    "knockback_friction": ENEMY_KNOCKBACK_FRICTION,
    "chase_speed": ENEMY_CHASE_SPEED,
    "attack_start_distance": ENEMY_ATTACK_START_DISTANCE,
    "telegraph_duration": ENEMY_TELEGRAPH_DURATION,
    "attack_duration": ENEMY_ATTACK_DURATION,
    "attack_cooldown": ENEMY_ATTACK_COOLDOWN,
    "attack_damage": ENEMY_ATTACK_DAMAGE,
    "attack_range": ENEMY_ATTACK_RANGE,
    "attack_height": ENEMY_ATTACK_HEIGHT,
    "attack_knockback": ENEMY_ATTACK_KNOCKBACK,
    "retreat_duration": ENEMY_RETREAT_DURATION,
    "retreat_speed": ENEMY_RETREAT_SPEED,
    "attack_hitstop": ENEMY_ATTACK_HITSTOP,
    "attack_shake_duration": ENEMY_ATTACK_SHAKE_DURATION,
    "attack_shake_strength": ENEMY_ATTACK_SHAKE_STRENGTH,
    "recovery_duration": ENEMY_RECOVERY_DURATION,
    "stagger_duration": ENEMY_STAGGER_DURATION,
    "body_color": (225, 70, 74),
    "hurt_color": (255, 235, 235),
    "defeated_color": (80, 45, 48),
    "telegraph_color": ENEMY_TELEGRAPH_COLOR,
    "attack_color": ENEMY_ATTACK_COLOR,
    "telegraph_pulse_speed": 14,
    "recoil_outline_color": (120, 35, 45),
}

FAST_ENEMY_CONFIG = {
    "label": "FAST ENEMY",
    "width": 46,
    "height": 102,
    "max_health": 72,
    "hurt_flash_duration": 0.10,
    "knockback_friction": 1750,
    "chase_speed": 215,
    "attack_start_distance": 84,
    "telegraph_duration": 0.24,
    "attack_duration": 0.16,
    "attack_cooldown": 0.78,
    "attack_damage": 5,
    "attack_range": 64,
    "attack_height": 52,
    "attack_knockback": 170,
    "retreat_duration": 0.18,
    "retreat_speed": 168,
    "attack_hitstop": 0.024,
    "attack_shake_duration": 0.06,
    "attack_shake_strength": 1,
    "recovery_duration": 0.14,
    "stagger_duration": 0.34,
    "body_color": (245, 145, 92),
    "hurt_color": (255, 234, 214),
    "defeated_color": (90, 58, 42),
    "telegraph_color": (255, 170, 95),
    "attack_color": (255, 208, 110),
    "telegraph_pulse_speed": 22,
    "recoil_outline_color": (135, 80, 42),
}

# Light attack combo settings
COMBO_RESET_TIME = 0.75
LIGHT_ATTACK_COMBO = (
    {
        "damage": 8,
        "range": 68,
        "height": 50,
        "duration": 0.14,
        "cooldown": 0.20,
        "recovery": 0.08,
        "cancel_window": 0.05,
        "knockback": 330,
        "movement_multiplier": 0.55,
        "hitstop": 0.035,
        "shake_duration": 0.10,
        "shake_strength": 3,
        "color": (130, 220, 255),
    },
    {
        "damage": 10,
        "range": 78,
        "height": 58,
        "duration": 0.16,
        "cooldown": 0.22,
        "recovery": 0.10,
        "cancel_window": 0.05,
        "knockback": 430,
        "movement_multiplier": 0.40,
        "hitstop": 0.045,
        "shake_duration": 0.13,
        "shake_strength": 4,
        "color": (125, 255, 210),
    },
    {
        "damage": 16,
        "range": 94,
        "height": 66,
        "duration": 0.22,
        "cooldown": 0.36,
        "recovery": 0.16,
        "cancel_window": 0.07,
        "knockback": 650,
        "movement_multiplier": 0.20,
        "hitstop": 0.060,
        "shake_duration": 0.18,
        "shake_strength": 7,
        "color": (255, 210, 120),
    },
)

COUNTER_ATTACK = {
    "damage": 30,
    "range": 122,
    "height": 82,
    "duration": 0.24,
    "cooldown": 0.42,
    "recovery": 0.18,
    "cancel_window": 0.00,
    "knockback": 980,
    "movement_multiplier": 0.14,
    "hitstop": 0.090,
    "shake_duration": 0.24,
    "shake_strength": 9,
    "color": (255, 240, 180),
}

# Basic colors used by the arena and characters.
SKY_TOP = (12, 14, 26)
SKY_BOTTOM = (42, 36, 48)
GROUND = (70, 62, 58)
GROUND_DARK = (34, 31, 32)
CRACK = (18, 18, 22)
PLAYER_COLOR = (76, 180, 255)
ENEMY_COLOR = (225, 70, 74)
ENEMY_HURT_COLOR = (255, 235, 235)
ENEMY_DEFEATED_COLOR = (80, 45, 48)
HEALTH_BG = (35, 35, 40)
HEALTH_PLAYER = (60, 220, 120)
HEALTH_ENEMY = (230, 60, 70)
WHITE = (235, 235, 240)
