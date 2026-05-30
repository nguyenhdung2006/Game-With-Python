"""Hardcoded wave profiles for pacing and presentation.

These profiles give each wave slightly different emotional timing without
turning encounter flow into giant scripted sequences.
"""

from entities.basic_enemy import BasicEnemy
from entities.elite_enemy import EliteEnemy
from entities.fast_enemy import FastEnemy
from settings import (
    ENCOUNTER_ATTACK_SWAP_DELAY,
    ENCOUNTER_ENTRANCE_MOVE_SPEED,
    ENCOUNTER_ENTRANCE_OFFSET,
    ENCOUNTER_ENTRANCE_PAUSE,
    ENCOUNTER_PRESSURE_LEAD_TIME,
    ENCOUNTER_SPAWN_STAGGER,
    ENCOUNTER_WAVE_ACTIVATION_DELAY,
    ENCOUNTER_WAVE_BANNER_DURATION,
    ENEMY_FLANK_FAR_OFFSET,
    ENEMY_FLANK_NEAR_OFFSET,
    ENEMY_SPACING_MIN_DISTANCE,
)


WAVE_PROFILES = [
    {
        "label": "Wave 1",
        "enemies": [BasicEnemy],
        "banner_duration": ENCOUNTER_WAVE_BANNER_DURATION,
        "activation_delay": ENCOUNTER_WAVE_ACTIVATION_DELAY + 0.18,
        "attack_swap_delay": ENCOUNTER_ATTACK_SWAP_DELAY + 0.08,
        "pressure_lead_time": ENCOUNTER_PRESSURE_LEAD_TIME + 0.06,
        "spawn_stagger": ENCOUNTER_SPAWN_STAGGER,
        "entrance_offset": ENCOUNTER_ENTRANCE_OFFSET - 8,
        "entrance_move_speed": ENCOUNTER_ENTRANCE_MOVE_SPEED - 20,
        "entrance_pause": ENCOUNTER_ENTRANCE_PAUSE + 0.06,
        "flank_near_offset": ENEMY_FLANK_NEAR_OFFSET - 10,
        "flank_far_offset": ENEMY_FLANK_FAR_OFFSET - 30,
        "spacing_min_distance": ENEMY_SPACING_MIN_DISTANCE - 6,
        "recovery_text": "Regroup",
    },
    {
        "label": "Wave 2",
        "enemies": [BasicEnemy, FastEnemy],
        "banner_duration": ENCOUNTER_WAVE_BANNER_DURATION,
        "activation_delay": ENCOUNTER_WAVE_ACTIVATION_DELAY,
        "attack_swap_delay": ENCOUNTER_ATTACK_SWAP_DELAY,
        "pressure_lead_time": ENCOUNTER_PRESSURE_LEAD_TIME,
        "spawn_stagger": ENCOUNTER_SPAWN_STAGGER,
        "entrance_offset": ENCOUNTER_ENTRANCE_OFFSET + 8,
        "entrance_move_speed": ENCOUNTER_ENTRANCE_MOVE_SPEED,
        "entrance_pause": ENCOUNTER_ENTRANCE_PAUSE,
        "flank_near_offset": ENEMY_FLANK_NEAR_OFFSET,
        "flank_far_offset": ENEMY_FLANK_FAR_OFFSET,
        "spacing_min_distance": ENEMY_SPACING_MIN_DISTANCE,
        "recovery_text": "Pressure Rising",
    },
    {
        "label": "Wave 3",
        "enemies": [FastEnemy, FastEnemy, BasicEnemy],
        "banner_duration": ENCOUNTER_WAVE_BANNER_DURATION + 0.08,
        "activation_delay": ENCOUNTER_WAVE_ACTIVATION_DELAY - 0.14,
        "attack_swap_delay": ENCOUNTER_ATTACK_SWAP_DELAY - 0.06,
        "pressure_lead_time": ENCOUNTER_PRESSURE_LEAD_TIME - 0.04,
        "spawn_stagger": ENCOUNTER_SPAWN_STAGGER - 0.04,
        "entrance_offset": ENCOUNTER_ENTRANCE_OFFSET + 18,
        "entrance_move_speed": ENCOUNTER_ENTRANCE_MOVE_SPEED + 40,
        "entrance_pause": ENCOUNTER_ENTRANCE_PAUSE - 0.04,
        "flank_near_offset": ENEMY_FLANK_NEAR_OFFSET + 18,
        "flank_far_offset": ENEMY_FLANK_FAR_OFFSET + 30,
        "spacing_min_distance": ENEMY_SPACING_MIN_DISTANCE + 10,
        "recovery_text": "Final Push",
    },
]

BOSS_ROOM_PROFILES = [
    {
        "label": "Elite Room",
        "enemies": [EliteEnemy],
        "banner_duration": ENCOUNTER_WAVE_BANNER_DURATION + 0.15,
        "activation_delay": ENCOUNTER_WAVE_ACTIVATION_DELAY + 0.28,
        "attack_swap_delay": ENCOUNTER_ATTACK_SWAP_DELAY + 0.22,
        "pressure_lead_time": ENCOUNTER_PRESSURE_LEAD_TIME + 0.18,
        "spawn_stagger": 0,
        "entrance_offset": ENCOUNTER_ENTRANCE_OFFSET + 18,
        "entrance_move_speed": ENCOUNTER_ENTRANCE_MOVE_SPEED - 70,
        "entrance_pause": ENCOUNTER_ENTRANCE_PAUSE + 0.12,
        "flank_near_offset": ENEMY_FLANK_NEAR_OFFSET,
        "flank_far_offset": ENEMY_FLANK_FAR_OFFSET,
        "spacing_min_distance": ENEMY_SPACING_MIN_DISTANCE + 24,
        "recovery_text": "Regroup",
    },
]
