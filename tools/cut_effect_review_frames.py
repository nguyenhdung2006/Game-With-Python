"""Cut newly dropped effect atlases into review-only frame folders."""

from pathlib import Path
import json
import os
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


EFFECT_ROOT = PROJECT_ROOT / "assets" / "sprites" / "effects"
OUTPUT_ROOT = EFFECT_ROOT / "review_frames"
SHEETS = {
    "fire_animation": {
        "filename": "fire_animation.png",
        "frame_width": 44,
        "frame_height": 48,
        "skip_empty": False,
    },
    "fire_animation2": {
        "filename": "fire_animation2.png",
        "frame_width": 32,
        "frame_height": 32,
        "skip_empty": False,
    },
    "objects": {
        "filename": "Objects.png",
        "frame_width": 16,
        "frame_height": 16,
        "skip_empty": True,
    },
}


def cut_sheet(sheet_id, config):
    """Save every reviewable cell and return a manifest entry."""
    source_path = EFFECT_ROOT / config["filename"]
    entry = {
        "sheet_id": sheet_id,
        "source": str(source_path.relative_to(PROJECT_ROOT)),
        "status": "OK",
        "saved_frames": [],
        "empty_cells_skipped": 0,
    }
    if not source_path.is_file():
        entry["status"] = "MISSING"
        return entry

    try:
        sheet = pygame.image.load(str(source_path))
    except (OSError, pygame.error) as error:
        entry["status"] = "LOAD_ERROR"
        entry["error"] = str(error)
        return entry

    frame_width = config["frame_width"]
    frame_height = config["frame_height"]
    sheet_width, sheet_height = sheet.get_size()
    if sheet_width % frame_width or sheet_height % frame_height:
        entry["status"] = "GRID_MISMATCH"
        entry["size"] = [sheet_width, sheet_height]
        return entry

    columns = sheet_width // frame_width
    rows = sheet_height // frame_height
    entry["size"] = [sheet_width, sheet_height]
    entry["grid"] = [columns, rows]
    entry["cell_size"] = [frame_width, frame_height]
    output_folder = OUTPUT_ROOT / sheet_id
    output_folder.mkdir(parents=True, exist_ok=True)

    for row in range(rows):
        for column in range(columns):
            frame = sheet.subsurface(
                (column * frame_width, row * frame_height, frame_width, frame_height)
            ).copy()
            if config["skip_empty"] and not frame.get_bounding_rect(min_alpha=1):
                entry["empty_cells_skipped"] += 1
                continue
            filename = f"frame_r{row + 1:02d}_c{column + 1:02d}.png"
            pygame.image.save(frame, str(output_folder / filename))
            entry["saved_frames"].append(filename)
    return entry


def run():
    """Cut all configured sheets and write a compact review manifest."""
    pygame.init()
    try:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        manifest = [cut_sheet(sheet_id, config) for sheet_id, config in SHEETS.items()]
        manifest_path = OUTPUT_ROOT / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    finally:
        pygame.quit()

    for entry in manifest:
        print(
            f"[{entry['status']}] {entry['sheet_id']}: "
            f"{len(entry['saved_frames'])} frame(s), "
            f"{entry['empty_cells_skipped']} empty cell(s) skipped"
        )
    print(f"Manifest: {manifest_path}")
    return 0 if all(entry["status"] == "OK" for entry in manifest) else 1


if __name__ == "__main__":
    raise SystemExit(run())
