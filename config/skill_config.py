"""Prototype tuning for the existing user-approved skill slots.

No new skill identity is defined here. Any future named skill or fantasy
behavior still requires user approval before implementation.
"""

KI_BLAST_CONFIG = {
    "cooldown": 0.45,
    "damage": 10,
    "speed": 760,
    "lifetime": 1.70,
    "width": 20,
    "height": 12,
    "knockback": 190,
    "forward_offset": 8,
    "reverse_offset": 26,
    "vertical_offset": 5,
    "visual_duration": 0.54,
    "sprite_scale": 1.15,
}

KAMEHAMEHA_CONFIG = {
    "cooldown": 5.0,
    "damage": 34,
    "range": 1280,
    "height": 46,
    "duration": 0.42,
    "knockback": 430,
    "origin_offset": 6,
    "windup_duration": 1.26,
    "visual_duration": 1.68,
    "super_saiyan_duration_multiplier": 1.65,
}

ENERGY_DISC_CONFIG = {
    "cooldown": 1.35,
    "damage": 22,
    "speed": 610,
    "lifetime": 1.90,
    "width": 58,
    "height": 24,
    "knockback": 280,
    "forward_offset": 8,
    "reverse_offset": 66,
    "vertical_offset": 8,
    "windup_duration": 0.48,
    "visual_duration": 0.48,
    "sprite_frame_delay": 0.08,
}
