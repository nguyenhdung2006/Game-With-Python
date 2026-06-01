"""Fixed placeholder dungeon layouts for gameplay-flow validation.

These layouts define structure and spawn anchors only. Final room art, map
identity, lore, and procedural generation require later review and approval.
"""

LAYOUT_START = "START"
LAYOUT_ENCOUNTER = "ENCOUNTER"
LAYOUT_ELITE_BOSS = "ELITE_BOSS"
LAYOUT_CLEAR = "CLEAR"

# Compatibility fallback for encounters created without an explicit layout.
DEFAULT_ENEMY_SPAWN_RIGHT_START = 760
DEFAULT_ENEMY_SPAWN_LEFT_START = 160
DEFAULT_ENEMY_SPAWN_SPACING = 170
DEFAULT_ENEMY_SPAWN_RIGHT_MARGIN = 90

# Enemy spawn points use floor anchors so different enemy heights still rest
# on the shared arena floor without layout-specific enemy logic.
DUNGEON_ROOM_LAYOUTS = (
    {
        "layout_id": "room_1_start",
        "label": "ROOM 1 - START",
        "layout_type": LAYOUT_START,
        "room_type": "ENCOUNTER",
        "room_bounds": (36, 176, 1208, 364),
        "arena_bounds": (72, 1208),
        "player_spawn": (180, 422),
        "enemy_spawn_points_right": ((760, 540), (930, 540), (1100, 540)),
        "enemy_spawn_points_left": ((160, 540), (330, 540), (500, 540)),
        "exit_position": (1162, 452),
        "torch_positions": ((116, 346), (380, 322), (900, 322), (1164, 346)),
        "decor_props": (
            ("crate", 132, 532),
            ("crate", 188, 532),
            ("bones_1", 302, 536),
            ("chain", 448, 354),
            ("shield", 520, 360),
            ("sword", 570, 360),
            ("chain", 832, 354),
            ("bones_2", 1038, 536),
            ("vase", 1090, 534),
        ),
    },
    {
        "layout_id": "room_2_encounter",
        "label": "ROOM 2 - ENCOUNTER",
        "layout_type": LAYOUT_ENCOUNTER,
        "room_type": "ENCOUNTER",
        "room_bounds": (52, 164, 1176, 376),
        "arena_bounds": (88, 1192),
        "player_spawn": (196, 422),
        "enemy_spawn_points_right": ((748, 540), (918, 540), (1088, 540)),
        "enemy_spawn_points_left": ((176, 540), (346, 540), (516, 540)),
        "exit_position": (1146, 452),
        "torch_positions": ((132, 340), (432, 316), (848, 316), (1148, 340)),
        "decor_props": (
            ("bookshelf_tall", 156, 520),
            ("bookshelf", 218, 520),
            ("painting", 318, 328),
            ("table_long", 450, 528),
            ("chair", 530, 528),
            ("scroll", 592, 520),
            ("painting_small", 968, 330),
            ("vase", 1044, 532),
            ("vase_broken", 1092, 532),
        ),
    },
    {
        "layout_id": "room_3_elite",
        "label": "ROOM 3 - ELITE",
        "layout_type": LAYOUT_ELITE_BOSS,
        "room_type": "BOSS_ENCOUNTER",
        "room_bounds": (68, 148, 1144, 392),
        "arena_bounds": (104, 1176),
        "player_spawn": (212, 422),
        "enemy_spawn_points_right": ((820, 540),),
        "enemy_spawn_points_left": ((386, 540),),
        "exit_position": (1130, 452),
        "torch_positions": ((152, 334), (426, 304), (854, 304), (1128, 334)),
        "decor_props": (
            ("flag", 262, 382),
            ("coffin", 350, 528),
            ("bones_1", 444, 536),
            ("throne", 640, 526),
            ("bones_2", 832, 536),
            ("coffin", 930, 528),
            ("flag", 1018, 382),
        ),
    },
)

DUNGEON_CLEAR_LAYOUT = {
    "layout_id": "dungeon_clear",
    "label": "DUNGEON CLEAR",
    "layout_type": LAYOUT_CLEAR,
    "room_type": "DUNGEON_CLEAR",
    "room_bounds": (68, 148, 1144, 392),
    "arena_bounds": (104, 1176),
    "player_spawn": (212, 422),
    "enemy_spawn_points_right": (),
    "enemy_spawn_points_left": (),
    "exit_position": (1130, 452),
    "torch_positions": ((152, 334), (426, 304), (854, 304), (1128, 334)),
    "decor_props": (
        ("flag", 262, 382),
        ("bones_1", 444, 536),
        ("throne", 640, 526),
        ("chest_open", 776, 528),
        ("bones_2", 832, 536),
        ("flag", 1018, 382),
    ),
}
