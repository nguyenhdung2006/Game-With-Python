"""Prototype normal-enemy tuning.

Generic archetypes stay mechanical here. New enemy identity still requires
user approval, and final balance happens after the gameplay loop stabilizes.
"""

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
ENEMY_RECOVERY_TINT_COLOR = (255, 205, 150)
ENEMY_PUNISH_OUTLINE_COLOR = (255, 234, 170)
ENEMY_STAGGER_EMPHASIS_COLOR = (255, 250, 205)

ENEMY_STATE_IDLE = "IDLE"
ENEMY_STATE_CHASE = "CHASE"
ENEMY_STATE_TELEGRAPH = "TELEGRAPH"
ENEMY_STATE_ATTACK = "ATTACK"
ENEMY_STATE_HURT = "HURT"
ENEMY_STATE_STAGGER = "STAGGER"
ENEMY_STATE_DEFEATED = "DEFEATED"

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
    "hurt_reaction_duration": 0.11,
    "hurt_reaction_heavy_bonus": 0.05,
    "punish_window_duration": 0.26,
    "recovery_flash_duration": 0.22,
    "stagger_emphasis_duration": 0.18,
    "post_stagger_recovery_duration": 0.10,
    "reaction_recoil_pixels": 8,
    "recovery_tint_color": ENEMY_RECOVERY_TINT_COLOR,
    "punish_outline_color": ENEMY_PUNISH_OUTLINE_COLOR,
    "stagger_emphasis_color": ENEMY_STAGGER_EMPHASIS_COLOR,
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
    "hurt_reaction_duration": 0.08,
    "hurt_reaction_heavy_bonus": 0.03,
    "punish_window_duration": 0.18,
    "recovery_flash_duration": 0.15,
    "stagger_emphasis_duration": 0.13,
    "post_stagger_recovery_duration": 0.06,
    "reaction_recoil_pixels": 6,
    "recovery_tint_color": (255, 215, 165),
    "punish_outline_color": (255, 228, 175),
    "stagger_emphasis_color": (255, 245, 215),
}
