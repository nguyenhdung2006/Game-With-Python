"""Prototype mechanical reward tuning and definitions.

Rewards stay neutral and conservative. Fantasy rewards require user approval,
and final balance happens after broader run progression exists.
"""

MAX_DAMAGE_MULTIPLIER = 1.6
MAX_SKILL_DAMAGE_MULTIPLIER = 1.5
MAX_COMBO_FINISHER_DAMAGE_MULTIPLIER = 1.5
MIN_DAMAGE_TAKEN_MULTIPLIER = 0.70
MIN_DASH_COOLDOWN_MULTIPLIER = 0.55
MIN_DASH_COOLDOWN = 0.25
MAX_DASH_SPEED_MULTIPLIER = 1.35
MAX_MOVE_SPEED_MULTIPLIER = 1.30
MIN_SKILL_COOLDOWN_MULTIPLIER = 0.65

# Definitions are data-only. Effect ids map to small mechanical handlers in
# systems/reward.py so config remains readable and easy to tune.
REWARD_DEFINITIONS = (
    {
        "id": "attack_damage_up",
        "display_name": "Attack Damage Up",
        "description": "+10% player attack damage.",
        "category": "offense",
        "value": 1.10,
        "max_stacks": 4,
        "effect_id": "attack_damage_up",
    },
    {
        "id": "skill_damage_up",
        "display_name": "Skill Damage Up",
        "description": "+10% skill damage.",
        "category": "offense",
        "value": 1.10,
        "max_stacks": 4,
        "effect_id": "skill_damage_up",
    },
    {
        "id": "combo_finisher_damage_up",
        "display_name": "Combo Finisher Damage Up",
        "description": "+12% combo finisher damage.",
        "category": "offense",
        "value": 1.12,
        "max_stacks": 3,
        "effect_id": "combo_finisher_damage_up",
    },
    {
        "id": "max_hp_up",
        "display_name": "Max HP Up",
        "description": "+10 max HP. Heal 10 HP now.",
        "category": "defense",
        "value": 10,
        "max_stacks": 5,
        "effect_id": "max_hp_up",
    },
    {
        "id": "damage_taken_down",
        "display_name": "Damage Taken Down",
        "description": "-8% incoming damage.",
        "category": "defense",
        "value": 0.92,
        "max_stacks": 4,
        "effect_id": "damage_taken_down",
    },
    {
        "id": "dash_cooldown_down",
        "display_name": "Dash Cooldown Down",
        "description": "-10% dash cooldown.",
        "category": "mobility",
        "value": 0.90,
        "max_stacks": 4,
        "effect_id": "dash_cooldown_down",
    },
    {
        "id": "dash_distance_up",
        "display_name": "Dash Distance Up",
        "description": "+8% dash distance.",
        "category": "mobility",
        "value": 1.08,
        "max_stacks": 4,
        "effect_id": "dash_distance_up",
    },
    {
        "id": "move_speed_up",
        "display_name": "Move Speed Up",
        "description": "+5% move speed.",
        "category": "mobility",
        "value": 1.05,
        "max_stacks": 4,
        "effect_id": "move_speed_up",
    },
    {
        "id": "skill_cooldown_down",
        "display_name": "Skill Cooldown Down",
        "description": "-8% skill cooldown.",
        "category": "resource",
        "value": 0.92,
        "max_stacks": 4,
        "effect_id": "skill_cooldown_down",
    },
    {
        "id": "heal_after_room_clear",
        "display_name": "Heal After Room Clear",
        "description": "Heal 8 HP after each room clear.",
        "category": "utility",
        "value": 8,
        "max_stacks": 3,
        "effect_id": "heal_after_room_clear",
    },
    {
        "id": "small_heal_now",
        "display_name": "Small Heal Now",
        "description": "Heal 18 HP immediately.",
        "category": "utility",
        "value": 18,
        "max_stacks": 3,
        "effect_id": "small_heal_now",
    },
)
