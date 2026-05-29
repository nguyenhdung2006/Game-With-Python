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
PLAYER_DODGE_SPEED = 820
PLAYER_DODGE_DURATION = 0.12
PLAYER_DODGE_COOLDOWN = 0.45
PLAYER_DODGE_INVULNERABILITY_DURATION = 0.16
PLAYER_DODGE_SHAKE_DURATION = 0.05
PLAYER_DODGE_SHAKE_STRENGTH = 1
PLAYER_DODGE_COLOR = (190, 240, 255)

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

# Enemy state names
ENEMY_STATE_IDLE = "IDLE"
ENEMY_STATE_CHASE = "CHASE"
ENEMY_STATE_TELEGRAPH = "TELEGRAPH"
ENEMY_STATE_ATTACK = "ATTACK"
ENEMY_STATE_HURT = "HURT"
ENEMY_STATE_DEFEATED = "DEFEATED"

# Light attack combo settings
COMBO_RESET_TIME = 0.75
LIGHT_ATTACK_COMBO = (
    {
        "damage": 8,
        "range": 68,
        "height": 50,
        "duration": 0.14,
        "cooldown": 0.20,
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
        "knockback": 650,
        "movement_multiplier": 0.20,
        "hitstop": 0.060,
        "shake_duration": 0.18,
        "shake_strength": 7,
        "color": (255, 210, 120),
    },
)

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
