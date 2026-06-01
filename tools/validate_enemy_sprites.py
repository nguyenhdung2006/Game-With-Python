"""Validate prototype Dungeon enemy sprite strips without changing gameplay."""

from pathlib import Path
import argparse
import os
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from config.enemy_sprite_config import ENEMY_SPRITE_CONFIGS


def cut_sheet_frames(surface, frame_width, frame_height, frame_count=None, sheet_row=0):
    """Cut one horizontal row of a sheet into copied frame surfaces."""
    if frame_width <= 0 or frame_height <= 0 or surface.get_height() < frame_height:
        return []
    if sheet_row < 0 or (sheet_row + 1) * frame_height > surface.get_height():
        return []
    available_frames = surface.get_width() // frame_width
    frame_total = available_frames if frame_count is None else min(frame_count, available_frames)
    return [
        surface.subsurface((index * frame_width, sheet_row * frame_height, frame_width, frame_height)).copy()
        for index in range(frame_total)
    ]


def validate_sprite_config(sprite_config):
    """Return a non-throwing validation report for one configured enemy."""
    frame_width = sprite_config.get("frame_width", 0)
    frame_height = sprite_config.get("frame_height", 0)
    report = {
        "enemy_id": sprite_config.get("enemy_id", "unknown"),
        "root_folder": Path(sprite_config.get("root_folder", "")),
        "animations": [],
        "valid": True,
    }

    if frame_width <= 0 or frame_height <= 0:
        report["valid"] = False
        report["animations"].append(
            {
                "animation": "config",
                "status": "INVALID",
                "details": "frame width and height must be positive",
            }
        )
        return report

    for animation_name, animation_config in sprite_config.get("animations", {}).items():
        frame_count = animation_config.get("frame_count", 0)
        sheet_path = report["root_folder"] / animation_config.get("filename", "")
        result = {
            "animation": animation_name,
            "path": sheet_path,
            "expected_frames": frame_count,
            "status": "OK",
            "details": "",
        }
        if not sheet_path.is_file():
            result["status"] = "MISSING"
            result["details"] = f"file not found: {sheet_path}"
        elif frame_count <= 0:
            result["status"] = "INVALID"
            result["details"] = "expected frame count must be positive"
        else:
            try:
                sheet = pygame.image.load(str(sheet_path))
                sheet_width, sheet_height = sheet.get_size()
                sheet_rows = animation_config.get("sheet_rows", 1)
                sheet_row = animation_config.get("sheet_row", 0)
                expected_width = frame_count * frame_width
                expected_height = sheet_rows * frame_height
                if sheet_width != expected_width:
                    result["status"] = "WIDTH_MISMATCH"
                    result["details"] = f"expected width {expected_width}, found {sheet_width}"
                elif sheet_height != expected_height:
                    result["status"] = "HEIGHT_MISMATCH"
                    result["details"] = f"expected height {expected_height}, found {sheet_height}"
                elif not 0 <= sheet_row < sheet_rows:
                    result["status"] = "ROW_MISMATCH"
                    result["details"] = f"sheet row {sheet_row} is outside {sheet_rows} rows"
                else:
                    result["details"] = (
                        f"{frame_count} frames at {frame_width}x{frame_height}, "
                        f"row {sheet_row + 1}/{sheet_rows}"
                    )
            except (OSError, pygame.error) as error:
                result["status"] = "LOAD_ERROR"
                result["details"] = str(error)

        if result["status"] != "OK":
            report["valid"] = False
        report["animations"].append(result)

    if not sprite_config.get("animations"):
        report["valid"] = False
        report["animations"].append(
            {
                "animation": "config",
                "status": "INVALID",
                "details": "no animations configured",
            }
        )
    return report


def validate_enemy_sprites(configs=None):
    """Return reports for all supplied prototype enemy configs."""
    configs = ENEMY_SPRITE_CONFIGS if configs is None else configs
    return [validate_sprite_config(config) for config in configs.values()]


def print_report(reports):
    """Print a compact console report suitable for manual and CI checks."""
    valid_count = 0
    animation_count = 0
    print("Dungeon enemy sprite validation")
    print("=" * 32)
    for report in reports:
        status = "PASS" if report["valid"] else "FAIL"
        print(f"[{status}] {report['enemy_id']}: {report['root_folder']}")
        if report["valid"]:
            valid_count += 1
        for animation in report["animations"]:
            animation_count += 1
            print(
                f"  [{animation['status']}] {animation['animation']}: "
                f"{animation['details']}"
            )

    print("-" * 32)
    print(f"Summary: {valid_count}/{len(reports)} enemies valid, {animation_count} animation strips checked")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "enemy_id",
        nargs="?",
        choices=sorted(ENEMY_SPRITE_CONFIGS),
        help="validate one configured enemy only",
    )
    args = parser.parse_args()
    configs = ENEMY_SPRITE_CONFIGS
    if args.enemy_id:
        configs = {args.enemy_id: ENEMY_SPRITE_CONFIGS[args.enemy_id]}
    reports = validate_enemy_sprites(configs)
    print_report(reports)
    return 0 if all(report["valid"] for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
