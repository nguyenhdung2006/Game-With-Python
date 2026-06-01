"""Prototype Dungeon enemy sprite-sheet metadata for validation tools only."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPRITE_ROOT = PROJECT_ROOT / "assets" / "sprites"


def animation(filename, frame_count, frame_speed, hold_last=False):
    """Return one horizontal 100x100 sprite-strip definition."""
    return {
        "filename": filename,
        "frame_count": frame_count,
        "frame_speed": frame_speed,
        "hold_last": hold_last,
    }


# These sheets are prototype/test inputs only. Dungeon rendering continues to
# use the current fallback visuals until the user approves sprite integration.
ENEMY_SPRITE_CONFIGS = {
    "orc": {
        "enemy_id": "orc",
        "root_folder": SPRITE_ROOT / "enemies" / "basic" / "Orc with shadows",
        "frame_width": 100,
        "frame_height": 100,
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
}
