"""Prototype player combat and movement tuning.

These values preserve the current gameplay feel. Final balance happens later.
"""

# Core body and movement
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

# Defense
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

# Mobility
GRAVITY = 2200
JUMP_STRENGTH = 850
DASH_SPEED = 1050
DASH_DURATION = 0.16
DASH_COOLDOWN = 0.55
DASH_TRAIL_LIFETIME = 0.18
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

# Readability and reaction feedback
PLAYER_ATTACK_BUFFER_DURATION = 0.12
PLAYER_RECOVERY_TINT_COLOR = (255, 220, 170)
PLAYER_UNSAFE_OUTLINE_COLOR = (255, 238, 170)
PLAYER_GUARD_STRESS_COLOR = (190, 245, 255)
PLAYER_PAYOFF_COLOR = (255, 248, 190)
PLAYER_WHIFF_FEEDBACK_DURATION = 0.18
PLAYER_WHIFF_RECOIL_DURATION = 0.12
PLAYER_WHIFF_RECOIL_PIXELS = 7
PLAYER_WHIFF_FINISHER_RECOVERY_MIN = 0.20
PLAYER_RECOVERY_FLASH_DURATION = 0.13
PLAYER_LANDING_FEEDBACK_DURATION = 0.12
PLAYER_HARD_LANDING_FEEDBACK_DURATION = 0.18
PLAYER_LANDING_COMPRESS_PIXELS = 10
PLAYER_DODGE_UNSAFE_DURATION = 0.10
PLAYER_DODGE_SETTLE_DURATION = 0.08
PLAYER_GUARD_STRESS_DURATION = 0.18
PLAYER_GUARD_RECOIL_PIXELS = 8
PLAYER_PARRY_PAYOFF_DURATION = 0.20
PLAYER_COUNTER_PAYOFF_DURATION = 0.22
PLAYER_ATTACK_HIT_PAYOFF_DURATION = 0.10
PLAYER_STATE_SETTLE_DURATION = 0.08

# Existing mechanical combo tuning
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
