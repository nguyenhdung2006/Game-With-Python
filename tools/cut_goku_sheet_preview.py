"""Cut manually reviewed Goku sprite rows into isolated preview frames."""

from collections import deque
from pathlib import Path
import json
import os
import stat

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.goku_sprite_config import (
    GOKU_EFFECT_DEFINITIONS,
    GOKU_KAMEHAMEHA_EFFECT_PATH,
    GOKU_PLAYER_FRAME_GROUPS,
    GOKU_SUPER_SAIYAN_KAMEHAMEHA_EFFECT_PATH,
)


GOKU_ROOT = PROJECT_ROOT / "assets" / "sprites" / "goku"
SOURCE_PATH = GOKU_ROOT / "source" / "goku_sheet.png"
FRAMES_ROOT = GOKU_ROOT / "frames"
PREVIEW_ROOT = GOKU_ROOT / "preview"
APPROVED_FRAMES_ROOT = GOKU_ROOT / "approved_player_frames"
APPROVED_PREVIEW_ROOT = GOKU_ROOT / "approved_player_preview"
APPROVED_EFFECTS_ROOT = GOKU_ROOT / "approved_effects"
REFERENCE_INDEX_PATH = GOKU_ROOT / "reference" / "frame_index.json"
MANIFEST_PATH = GOKU_ROOT / "manifest.json"

CANVAS_SIZE = (80, 80)
BACKGROUND_THRESHOLD = 218

# These neutral row labels are intentional. The user reviews identity and action
# naming before any extracted frame becomes a gameplay asset.
REVIEW_ROWS = (
    {"action_id": "base_row_01", "region": (54, 122, 710, 190), "min_component_area": 650},
    {"action_id": "base_row_03", "region": (54, 266, 676, 336), "min_component_area": 650},
    {"action_id": "base_row_05", "region": (54, 422, 548, 488), "min_component_area": 650},
    {"action_id": "base_row_06", "region": (54, 498, 778, 566), "min_component_area": 650},
)

def is_background(pixel):
    """Treat connected near-white pixels as removable sheet background."""
    red, green, blue = pixel[:3]
    return red >= BACKGROUND_THRESHOLD and green >= BACKGROUND_THRESHOLD and blue >= BACKGROUND_THRESHOLD


def find_components(image, region, min_area):
    """Return left-to-right non-background components inside one reviewed row."""
    left, top, right, bottom = region
    pixels = image.load()
    seen = set()
    components = []
    for y in range(top, bottom):
        for x in range(left, right):
            if (x, y) in seen or is_background(pixels[x, y]):
                continue
            queue = deque(((x, y),))
            seen.add((x, y))
            xs = []
            ys = []
            while queue:
                current_x, current_y = queue.popleft()
                xs.append(current_x)
                ys.append(current_y)
                for next_x, next_y in (
                    (current_x + 1, current_y),
                    (current_x - 1, current_y),
                    (current_x, current_y + 1),
                    (current_x, current_y - 1),
                ):
                    if (
                        next_x < left
                        or next_x >= right
                        or next_y < top
                        or next_y >= bottom
                        or (next_x, next_y) in seen
                        or is_background(pixels[next_x, next_y])
                    ):
                        continue
                    seen.add((next_x, next_y))
                    queue.append((next_x, next_y))
            if len(xs) >= min_area:
                components.append((min(xs), min(ys), max(xs) + 1, max(ys) + 1))
    return sorted(components)


def remove_connected_background(frame):
    """Make only border-connected sheet background transparent."""
    rgba = frame.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    queue = deque()
    seen = set()
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in seen:
            continue
        seen.add((x, y))
        if not is_background(pixels[x, y]):
            continue
        red, green, blue, _ = pixels[x, y]
        pixels[x, y] = (red, green, blue, 0)
        for next_x, next_y in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= next_x < width and 0 <= next_y < height and (next_x, next_y) not in seen:
                queue.append((next_x, next_y))
    return rgba


def normalize_component(sheet, box, canvas_size=CANVAS_SIZE):
    """Crop one character component and align it to a shared bottom-center anchor."""
    left, top, right, bottom = box
    padding = 3
    crop_box = (
        max(0, left - padding),
        max(0, top - padding),
        min(sheet.width, right + padding),
        min(sheet.height, bottom + padding),
    )
    frame = remove_connected_background(sheet.crop(crop_box))
    content_box = frame.getbbox()
    if content_box is None:
        return None, crop_box
    frame = frame.crop(content_box)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    paste_x = (canvas_size[0] - frame.width) // 2
    paste_y = canvas_size[1] - frame.height - 4
    canvas.alpha_composite(frame, (paste_x, paste_y))
    return canvas, crop_box


def make_super_saiyan_variant(frame):
    """Create a crisp powered variant from an approved base-form frame."""
    powered = frame.convert("RGBA")
    aura = Image.new("RGBA", powered.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(aura)
    content_box = powered.getbbox()
    if content_box is not None:
        left, top, right, bottom = content_box
        cx = (left + right) // 2
        draw.ellipse(
            (left - 13, top - 15, right + 13, bottom + 8),
            outline=(255, 230, 90, 92),
            width=3,
        )
        draw.polygon(
            (
                (cx, max(0, top - 21)),
                (right + 14, top + 12),
                (right + 5, bottom - 8),
                (cx, min(powered.height - 1, bottom + 12)),
                (left - 5, bottom - 8),
                (left - 14, top + 12),
            ),
            outline=(255, 196, 42, 108),
        )

    pixels = powered.load()
    width, height = powered.size
    if content_box is None:
        head_top = 0
        head_bottom = height // 2
    else:
        left, top, right, bottom = content_box
        head_top = top
        head_bottom = top + int((bottom - top) * 0.48)
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                continue
            upper_body = y < height * 0.57
            head_fill = head_top <= y <= head_bottom
            very_dark = max(red, green, blue) <= 34
            dark_fill = 34 < max(red, green, blue) < 128
            low_saturation = abs(red - green) < 36 and abs(green - blue) < 46
            if upper_body and dark_fill and low_saturation:
                shade = max(red, green, blue)
                pixels[x, y] = (
                    min(255, 178 + shade),
                    min(244, 128 + shade),
                    max(42, shade // 2),
                    alpha,
                )
            elif upper_body and very_dark and alpha > 210:
                if head_fill:
                    pixels[x, y] = (82, 62, 10, alpha)
                else:
                    pixels[x, y] = (22, 18, 8, alpha)

    aura.alpha_composite(powered)
    return aura


def create_super_saiyan_kamehameha_effect():
    """Build a brighter SSJ beam PNG from the approved base beam."""
    source_path = Path(GOKU_KAMEHAMEHA_EFFECT_PATH)
    output_path = Path(GOKU_SUPER_SAIYAN_KAMEHAMEHA_EFFECT_PATH)
    if not source_path.is_file():
        return None

    source = Image.open(source_path).convert("RGBA")
    width, height = source.size
    powered = Image.new("RGBA", source.size, (0, 0, 0, 0))
    source_pixels = source.load()
    powered_pixels = powered.load()
    for y in range(height):
        center_weight = 1 - abs((y / max(1, height - 1)) * 2 - 1)
        for x in range(width):
            red, green, blue, alpha = source_pixels[x, y]
            if alpha == 0:
                continue
            core = center_weight > 0.50
            if core:
                powered_pixels[x, y] = (
                    min(255, red + 70),
                    min(255, green + 64),
                    min(255, blue + 24),
                    min(255, alpha + 36),
                )
            else:
                powered_pixels[x, y] = (
                    min(255, red + 20),
                    min(255, green + 58),
                    min(255, blue + 76),
                    alpha,
                )

    draw = ImageDraw.Draw(powered)
    draw.line((0, height // 2, width, height // 2), fill=(120, 245, 255, 120), width=max(2, height // 5))
    draw.line((0, height // 2, width, height // 2), fill=(255, 255, 255, 235), width=max(1, height // 9))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    powered.save(output_path)
    print(f"[EFFECT] super_saiyan_kamehameha: {powered.width}x{powered.height}")
    return output_path


def save_contact_sheet(action_id, frames, preview_root=PREVIEW_ROOT):
    """Export one readable strip preview over a checkerboard background."""
    scale = 3
    margin = 12
    label_height = 28
    frame_width = max(frame.width for frame in frames)
    frame_height = max(frame.height for frame in frames)
    cell_width = frame_width * scale
    cell_height = frame_height * scale
    width = margin * 2 + cell_width * len(frames)
    height = margin * 2 + label_height + cell_height
    preview = Image.new("RGB", (width, height), (28, 32, 42))
    draw = ImageDraw.Draw(preview)
    draw.text((margin, 8), f"{action_id} / {len(frames)} frames", fill=(236, 240, 248))
    for index, frame in enumerate(frames):
        x = margin + index * cell_width
        y = margin + label_height
        for cell_y in range(0, cell_height, 12):
            for cell_x in range(0, cell_width, 12):
                color = (214, 218, 226) if (cell_x // 12 + cell_y // 12) % 2 == 0 else (180, 186, 198)
                draw.rectangle((x + cell_x, y + cell_y, x + cell_x + 11, y + cell_y + 11), fill=color)
        enlarged = frame.resize((frame.width * scale, frame.height * scale), Image.Resampling.NEAREST)
        preview.paste(enlarged, (x, y), enlarged)
    path = preview_root / f"{action_id}.png"
    preview.save(path)
    return path


def save_animation_preview(action_id, frames, preview_root=PREVIEW_ROOT):
    """Export a looping GIF so frame order can be reviewed as motion."""
    scale = 4
    frame_size = (
        max(frame.width for frame in frames) * scale,
        max(frame.height for frame in frames) * scale,
    )
    previews = []
    for frame in frames:
        background = Image.new("RGB", frame_size, (30, 34, 44))
        enlarged = frame.resize((frame.width * scale, frame.height * scale), Image.Resampling.NEAREST)
        background.paste(enlarged, (0, 0), enlarged)
        previews.append(background)
    path = preview_root / f"{action_id}.gif"
    if previews:
        previews[0].save(
            path,
            save_all=True,
            append_images=previews[1:],
            duration=110,
            loop=0,
        )
    return path


def remove_stale_generated_frames(action_folder):
    """Clear old generated PNG frames so changed mappings cannot leave leftovers."""
    for stale_frame in action_folder.glob("frame_*.png"):
        try:
            stale_frame.unlink()
        except PermissionError:
            os.chmod(stale_frame, stat.S_IWRITE)
            stale_frame.unlink()


def extract_definitions(sheet, definitions, frames_root, preview_root):
    """Cut one definition group into transparent frames and review previews."""
    frames_root.mkdir(parents=True, exist_ok=True)
    preview_root.mkdir(parents=True, exist_ok=True)
    actions = []
    for definition in definitions:
        action_id = definition["action_id"]
        components = find_components(sheet, definition["region"], definition["min_component_area"])
        action_folder = frames_root / action_id
        action_folder.mkdir(parents=True, exist_ok=True)
        frames = []
        frame_entries = []
        for index, component_box in enumerate(components):
            frame, crop_box = normalize_component(sheet, component_box)
            if frame is None:
                continue
            filename = f"frame_{index + 1:02d}.png"
            frame.save(action_folder / filename)
            frames.append(frame)
            frame_entries.append({"filename": filename, "crop_box": list(crop_box)})
        preview_path = save_contact_sheet(action_id, frames, preview_root)
        animation_preview_path = save_animation_preview(action_id, frames, preview_root)
        actions.append(
            {
                "action_id": action_id,
                "region": list(definition["region"]),
                "frame_count": len(frames),
                "frames": frame_entries,
                "preview": str(preview_path.relative_to(PROJECT_ROOT)),
                "animation_preview": str(animation_preview_path.relative_to(PROJECT_ROOT)),
            }
        )
        print(f"[OK] {action_id}: {len(frames)} frame(s)")
    return actions


def load_reference_boxes():
    """Load the numbered reference index used for explicit user selections."""
    if not REFERENCE_INDEX_PATH.is_file():
        raise FileNotFoundError(
            f"Missing numbered frame index. Run tools/annotate_goku_sheet_reference.py first: {REFERENCE_INDEX_PATH}"
        )
    index = json.loads(REFERENCE_INDEX_PATH.read_text(encoding="utf-8"))
    return {
        frame["frame_id"]: tuple(frame["box"])
        for row in index["rows"]
        for frame in row["frames"]
    }


def extract_approved_player_groups(sheet):
    """Cut only frame ids explicitly approved by the user."""
    reference_boxes = load_reference_boxes()
    APPROVED_FRAMES_ROOT.mkdir(parents=True, exist_ok=True)
    APPROVED_PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    actions = []
    for definition in GOKU_PLAYER_FRAME_GROUPS:
        action_id = definition["action_id"]
        action_folder = APPROVED_FRAMES_ROOT / action_id
        action_folder.mkdir(parents=True, exist_ok=True)
        frames = []
        frame_entries = []
        for index, frame_id in enumerate(definition["frame_ids"], start=1):
            if frame_id not in reference_boxes:
                raise KeyError(f"Approved frame id is missing from reference index: {frame_id}")
            frame_box = definition.get("frame_box_overrides", {}).get(
                frame_id,
                reference_boxes[frame_id],
            )
            frame, crop_box = normalize_component(
                sheet,
                frame_box,
                tuple(definition["canvas_size"]),
            )
            if frame is None:
                continue
            if definition.get("super_saiyan_variant"):
                frame = make_super_saiyan_variant(frame)
            filename = f"frame_{index:02d}_{frame_id}.png"
            frame.save(action_folder / filename)
            frames.append(frame)
            frame_entries.append(
                {
                    "frame_id": frame_id,
                    "filename": filename,
                    "crop_box": list(crop_box),
                }
            )
        preview_path = save_contact_sheet(action_id, frames, APPROVED_PREVIEW_ROOT)
        animation_preview_path = save_animation_preview(action_id, frames, APPROVED_PREVIEW_ROOT)
        actions.append(
            {
                "action_id": action_id,
                "frame_count": len(frames),
                "frames": frame_entries,
                "preview": str(preview_path.relative_to(PROJECT_ROOT)),
                "animation_preview": str(animation_preview_path.relative_to(PROJECT_ROOT)),
            }
        )
        print(f"[APPROVED] {action_id}: {len(frames)} frame(s)")
    return actions


def extract_approved_effects(sheet):
    """Cut the user-selected projectile and beam visuals from body frames."""
    APPROVED_EFFECTS_ROOT.mkdir(parents=True, exist_ok=True)
    effects = []
    for definition in GOKU_EFFECT_DEFINITIONS:
        effect_id = definition["effect_id"]
        output_path = Path(definition["output_path"])
        frame = remove_connected_background(sheet.crop(tuple(definition["box"])))
        content_box = frame.getbbox()
        if content_box is None:
            raise ValueError(f"Approved effect crop is empty: {effect_id}")
        frame = frame.crop(content_box)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame.save(output_path)
        effects.append(
            {
                "effect_id": effect_id,
                "box": list(definition["box"]),
                "output_path": str(output_path.relative_to(PROJECT_ROOT)),
                "size": list(frame.size),
            }
        )
        print(f"[EFFECT] {effect_id}: {frame.width}x{frame.height}")
    ssj_effect_path = create_super_saiyan_kamehameha_effect()
    if ssj_effect_path is not None:
        effects.append(
            {
                "effect_id": "super_saiyan_kamehameha",
                "source_effect_id": "kamehameha",
                "output_path": str(ssj_effect_path.relative_to(PROJECT_ROOT)),
                "size": list(Image.open(ssj_effect_path).size),
            }
        )
    return effects


def run():
    """Extract reviewed rows while keeping the original source untouched."""
    if not SOURCE_PATH.is_file():
        print(f"Missing source sheet: {SOURCE_PATH}")
        return 1

    sheet = Image.open(SOURCE_PATH).convert("RGB")
    manifest = {
        "source": str(SOURCE_PATH.relative_to(PROJECT_ROOT)),
        "source_size": list(sheet.size),
        "canvas_size": list(CANVAS_SIZE),
        "status": "USER_APPROVED_PLAYER_PROTOTYPE",
        "actions": extract_definitions(sheet, REVIEW_ROWS, FRAMES_ROOT, PREVIEW_ROOT),
        "approved_player_actions": extract_approved_player_groups(sheet),
        "approved_effects": extract_approved_effects(sheet),
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Preview folder: {PREVIEW_ROOT}")
    print(f"Approved player preview folder: {APPROVED_PREVIEW_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
