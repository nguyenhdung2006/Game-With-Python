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
        "color": (130, 220, 255),
    },
    {
        "damage": 10,
        "range": 78,
        "height": 58,
        "duration": 0.16,
        "cooldown": 0.22,
        "knockback": 430,
        "color": (125, 255, 210),
    },
    {
        "damage": 16,
        "range": 94,
        "height": 66,
        "duration": 0.22,
        "cooldown": 0.36,
        "knockback": 650,
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
