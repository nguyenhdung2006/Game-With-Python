"""User-approved Goku prototype sprite mappings.

Only frame groups explicitly selected by the user belong here. Unmapped sheet
rows remain review-only until the user defines their gameplay purpose.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOKU_EFFECTS_ROOT = PROJECT_ROOT / "assets" / "sprites" / "goku" / "approved_effects"
GOKU_KI_BLAST_EFFECT_PATH = GOKU_EFFECTS_ROOT / "ki_blast.png"
GOKU_KAMEHAMEHA_EFFECT_PATH = GOKU_EFFECTS_ROOT / "kamehameha.png"
GOKU_SUPER_SAIYAN_KAMEHAMEHA_EFFECT_PATH = GOKU_EFFECTS_ROOT / "super_saiyan_kamehameha.png"
GOKU_ENERGY_DISC_EFFECT_PATHS = (
    GOKU_EFFECTS_ROOT / "energy_disc_1.png",
    GOKU_EFFECTS_ROOT / "energy_disc_2.png",
)
GOKU_PROJECTILE_IMPACT_EFFECT_PATHS = (
    GOKU_EFFECTS_ROOT / "projectile_impact_1.png",
    GOKU_EFFECTS_ROOT / "projectile_impact_2.png",
)

GOKU_PLAYER_RENDER_SCALE = 1.6
GOKU_KI_BLAST_ACTION_IDS = (
    "skill_1_shot_1",
    "skill_1_shot_2",
    "skill_1_shot_3",
)

GOKU_PLAYER_FRAME_GROUPS = (
    {
        "action_id": "intro_entry",
        "frame_ids": ("R01-01", "R01-02", "R01-03", "R01-04"),
        "frame_delay": 0.36,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "fight_ready",
        "frame_ids": ("R01-05", "R01-06", "R01-07", "R01-08"),
        "frame_delay": 0.14,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "idle_hold",
        "frame_ids": ("R01-08",),
        "frame_delay": 0.14,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "victory",
        "frame_ids": ("R01-09",),
        "frame_delay": 0.18,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "walk",
        "frame_ids": ("R03-01", "R03-02", "R03-03", "R03-04"),
        "frame_delay": 0.14,
        "loop": True,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "run",
        "frame_ids": ("R03-05", "R03-06", "R03-07", "R03-08"),
        "frame_delay": 0.10,
        "loop": True,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "jump",
        "frame_ids": ("R04-01", "R04-02", "R04-03", "R04-04", "R04-05", "R04-06"),
        "frame_delay": 0.10,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "guard",
        "frame_ids": ("R05-01", "R05-02", "R05-03", "R05-04"),
        "frame_delay": 0.12,
        "loop": True,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "attack_punch_1",
        "frame_ids": ("R06-01", "R06-02", "R06-03"),
        "frame_delay": 0.047,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_punch_1",
        "frame_ids": ("R06-01", "R06-02", "R06-03"),
        "frame_delay": 0.047,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "attack_punch_2",
        "frame_ids": ("R06-04", "R06-05"),
        "frame_delay": 0.080,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_punch_2",
        "frame_ids": ("R06-04", "R06-05"),
        "frame_delay": 0.080,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "attack_punch_3",
        "frame_ids": ("R06-06", "R06-07", "R06-08", "R06-09"),
        "frame_delay": 0.055,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_punch_3",
        "frame_ids": ("R06-06", "R06-07", "R06-08", "R06-09"),
        "frame_delay": 0.055,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "attack_punch_4",
        "frame_ids": ("R06-10", "R06-11", "R06-12"),
        "frame_delay": 0.060,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_punch_4",
        "frame_ids": ("R06-10", "R06-11", "R06-12"),
        "frame_delay": 0.060,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "attack_punch_5",
        "frame_ids": ("R06-13", "R06-14"),
        "frame_delay": 0.090,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_punch_5",
        "frame_ids": ("R06-13", "R06-14"),
        "frame_delay": 0.090,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "punch_recovery",
        "frame_ids": ("R02-01", "R02-02"),
        "frame_delay": 0.080,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "kick_1",
        "frame_ids": ("R07-01", "R07-02", "R07-03"),
        "frame_delay": 0.047,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_kick_1",
        "frame_ids": ("R07-01", "R07-02", "R07-03"),
        "frame_delay": 0.047,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "kick_2",
        "frame_ids": ("R07-04", "R07-05", "R07-06"),
        "frame_delay": 0.053,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_kick_2",
        "frame_ids": ("R07-04", "R07-05", "R07-06"),
        "frame_delay": 0.053,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "kick_3",
        "frame_ids": ("R07-06", "R07-07", "R07-08", "R07-09", "R07-10"),
        "frame_delay": 0.044,
        "loop": False,
        "canvas_size": (96, 80),
    },
    {
        "action_id": "super_saiyan_kick_3",
        "frame_ids": ("R07-06", "R07-07", "R07-08", "R07-09", "R07-10"),
        "frame_delay": 0.044,
        "loop": False,
        "canvas_size": (112, 96),
        "super_saiyan_variant": True,
    },
    {
        "action_id": "kick_recovery_1",
        "frame_ids": ("R04-07", "R04-08"),
        "frame_delay": 0.080,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "hurt_1",
        "frame_ids": ("R09-01", "R09-02"),
        "frame_delay": 0.07,
        "loop": False,
        "canvas_size": (112, 80),
    },
    {
        "action_id": "hurt_2",
        "frame_ids": ("R09-03",),
        "frame_delay": 0.07,
        "loop": False,
        "canvas_size": (112, 80),
    },
    {
        "action_id": "hurt_3",
        "frame_ids": ("R09-04",),
        "frame_delay": 0.07,
        "loop": False,
        "canvas_size": (112, 80),
    },
    {
        "action_id": "hurt_4",
        "frame_ids": ("R09-05",),
        "frame_delay": 0.07,
        "loop": False,
        "canvas_size": (112, 80),
    },
    {
        "action_id": "defeated",
        "frame_ids": ("R09-06", "R09-07"),
        "frame_delay": 0.12,
        "loop": False,
        "canvas_size": (112, 80),
    },
    {
        "action_id": "skill_1_shot_1",
        "frame_ids": ("R10-01", "R10-02"),
        "frame_delay": 0.09,
        "loop": False,
        "canvas_size": (80, 80),
    },
    {
        "action_id": "skill_1_shot_2",
        "frame_ids": ("R10-03", "R10-04"),
        "frame_delay": 0.09,
        "loop": False,
        "canvas_size": (80, 80),
        "frame_box_overrides": {
            "R10-04": (235, 871, 272, 921),
        },
    },
    {
        "action_id": "skill_1_shot_3",
        "frame_ids": ("R10-05", "R10-06"),
        "frame_delay": 0.09,
        "loop": False,
        "canvas_size": (80, 80),
        "frame_box_overrides": {
            "R10-06": (382, 871, 419, 922),
        },
    },
    {
        "action_id": "skill_2",
        "frame_ids": (
            "R11-01",
            "R11-02",
            "R11-03",
            "R11-04",
            "R11-05",
            "R11-06",
            "R11-07",
            "R11-08",
            "R11-09",
        ),
        "frame_delay": 0.14,
        "loop": False,
        "canvas_size": (88, 84),
    },
    {
        "action_id": "super_saiyan_skill_2",
        "frame_ids": (
            "R21-08",
            "R21-09",
            "R21-10",
            "R21-09",
            "R21-10",
        ),
        "frame_delay": 0.18,
        "loop": False,
        "canvas_size": (112, 96),
    },
    {
        "action_id": "skill_3",
        "frame_ids": ("R12-01", "R12-02", "R12-03", "R12-04"),
        "frame_delay": 0.12,
        "loop": False,
        "canvas_size": (88, 84),
    },
    {
        "action_id": "super_saiyan_transform",
        "frame_ids": (
            "R22-01",
            "R22-02",
            "R22-03",
            "R22-04",
            "R22-05",
            "R22-06",
            "R22-07",
            "R22-08",
            "R22-09",
            "R22-10",
        ),
        "frame_delay": 0.095,
        "loop": False,
        "canvas_size": (96, 96),
    },
    {
        "action_id": "super_saiyan_idle",
        "frame_ids": ("R22-11",),
        "frame_delay": 0.14,
        "loop": True,
        "canvas_size": (96, 96),
    },
)

GOKU_PLAYER_ANIMATION_CONFIG = {
    definition["action_id"]: definition
    for definition in GOKU_PLAYER_FRAME_GROUPS
}

# These explicit boxes isolate only effects that the user selected from the
# original sheet. They stay separate from body animation frames at runtime.
GOKU_EFFECT_DEFINITIONS = (
    {
        "effect_id": "ki_blast",
        "box": (288, 879, 322, 913),
        "output_path": GOKU_KI_BLAST_EFFECT_PATH,
    },
    {
        "effect_id": "kamehameha",
        "box": (514, 938, 749, 1022),
        "output_path": GOKU_KAMEHAMEHA_EFFECT_PATH,
    },
    {
        "effect_id": "energy_disc_1",
        "box": (306, 1046, 376, 1078),
        "output_path": GOKU_ENERGY_DISC_EFFECT_PATHS[0],
    },
    {
        "effect_id": "energy_disc_2",
        "box": (373, 1046, 438, 1078),
        "output_path": GOKU_ENERGY_DISC_EFFECT_PATHS[1],
    },
    {
        "effect_id": "projectile_impact_1",
        "box": (165, 1128, 203, 1166),
        "output_path": GOKU_PROJECTILE_IMPACT_EFFECT_PATHS[0],
    },
    {
        "effect_id": "projectile_impact_2",
        "box": (201, 1125, 251, 1174),
        "output_path": GOKU_PROJECTILE_IMPACT_EFFECT_PATHS[1],
    },
)
