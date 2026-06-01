"""Prototype Dungeon enemy sprite-sheet metadata for validation and rendering."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPRITE_ROOT = PROJECT_ROOT / "assets" / "sprites"


def animation(filename, frame_count, frame_speed, hold_last=False):
    """Return one horizontal sprite-strip definition."""
    return {
        "filename": filename,
        "frame_count": frame_count,
        "frame_speed": frame_speed,
        "hold_last": hold_last,
    }


def directional_animation(filename, frame_count, frame_speed, hold_last=False):
    """Return one four-direction sheet definition using its side-facing row."""
    return {
        **animation(filename, frame_count, frame_speed, hold_last),
        "sheet_rows": 4,
        "sheet_row": 2,
    }


# These sheets remain prototype/test inputs. Gameplay hitboxes stay independent
# from their presentation scale so final animation decisions can happen later.
ENEMY_SPRITE_CONFIGS = {
    "orc": {
        "enemy_id": "orc",
        "root_folder": SPRITE_ROOT / "enemies" / "basic" / "Orc with shadows",
        "frame_width": 100,
        "frame_height": 100,
        "render_scale": 4,
        "feet_anchor": (54, 60),
        "animations": {
            "idle": animation("Orc-Idle.png", 6, 0.14),
            "walk": animation("Orc-Walk.png", 8, 0.10),
            "attack_01": animation("Orc-Attack01.png", 6, 0.10),
            "attack_02": animation("Orc-Attack02.png", 6, 0.10),
            "hurt": animation("Orc-Hurt.png", 4, 0.10),
            "death": animation("Orc-Death.png", 4, 0.14, hold_last=True),
        },
    },
    "soldier": {
        "enemy_id": "soldier",
        "root_folder": SPRITE_ROOT / "player" / "Soldier with shadows",
        "frame_width": 100,
        "frame_height": 100,
        "render_scale": 4,
        "feet_anchor": (50, 60),
        "animations": {
            "idle": animation("Soldier-Idle.png", 6, 0.14),
            "walk": animation("Soldier-Walk.png", 8, 0.10),
            "attack_01": animation("Soldier-Attack01.png", 6, 0.10),
            "attack_02": animation("Soldier-Attack02.png", 6, 0.10),
            "attack_03": animation("Soldier-Attack03.png", 9, 0.10),
            "hurt": animation("Soldier-Hurt.png", 4, 0.10),
            "death": animation("Soldier-Death.png", 4, 0.14, hold_last=True),
        },
    },
    "slime": {
        "enemy_id": "slime",
        "root_folder": SPRITE_ROOT / "enemies" / "basic" / "Strips",
        "frame_width": 32,
        "frame_height": 32,
        "render_scale": 3,
        "feet_anchor": (16, 27),
        "animations": {
            "idle": animation("idle_strip.png", 4, 0.14),
            "walk": animation("move_strip.png", 4, 0.11),
            "attack": animation("attack_strip.png", 4, 0.11),
            "death": animation("death_strip.png", 6, 0.14, hold_last=True),
        },
    },
    "orc2": {
        "enemy_id": "orc2",
        "root_folder": SPRITE_ROOT / "enemies" / "basic" / "Orc_level" / "Orc2",
        "frame_width": 64,
        "frame_height": 64,
        "render_scale": 2,
        "feet_anchor": (32, 56),
        "animations": {
            "idle": directional_animation("Orc2_idle/orc2_idle_full.png", 4, 0.14),
            "walk": directional_animation("Orc2_walk/orc2_walk_full.png", 6, 0.10),
            "attack": directional_animation("Orc2_attack/orc2_attack_full.png", 8, 0.10),
            "hurt": directional_animation("Orc2_hurt/orc2_hurt_full.png", 6, 0.10),
            "death": directional_animation("Orc2_death/orc2_death_full.png", 8, 0.14, hold_last=True),
        },
    },
    "orc3": {
        "enemy_id": "orc3",
        "root_folder": SPRITE_ROOT / "enemies" / "basic" / "Orc_level" / "Orc3",
        "frame_width": 64,
        "frame_height": 64,
        "render_scale": 2,
        "feet_anchor": (32, 56),
        "animations": {
            "idle": directional_animation("orc3_idle/orc3_idle_full.png", 4, 0.14),
            "walk": directional_animation("orc3_walk/orc3_walk_full.png", 6, 0.10),
            "attack": directional_animation("orc3_attack/orc3_attack_full.png", 8, 0.10),
            "hurt": directional_animation("orc3_hurt/orc3_hurt_full.png", 6, 0.10),
            "death": directional_animation("orc3_death/orc3_death_full.png", 8, 0.14, hold_last=True),
        },
    },
}
