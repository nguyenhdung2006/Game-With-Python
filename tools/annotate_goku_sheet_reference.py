"""Export a numbered Goku sheet reference for user-guided frame mapping."""

from collections import deque
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOKU_ROOT = PROJECT_ROOT / "assets" / "sprites" / "goku"
SOURCE_PATH = GOKU_ROOT / "source" / "goku_sheet.png"
REFERENCE_ROOT = GOKU_ROOT / "reference"
INDEX_PATH = REFERENCE_ROOT / "frame_index.json"
FULL_REFERENCE_PATH = REFERENCE_ROOT / "goku_sheet_numbered.png"

BACKGROUND_THRESHOLD = 218
ACTION_LEFT = 45
ACTION_RIGHT = 830
ROW_RIGHT_OVERRIDES = {
    "R15": 1040,
    "R17": 1040,
    "R21": 1040,
    "R23": 1040,
}

# Row ids are presentation references only. The user decides which ids form
# each actual animation or effect after reviewing the exported images.
ROW_BANDS = (
    ("R01", 122, 190),
    ("R02", 196, 262),
    ("R03", 266, 338),
    ("R04", 340, 408),
    ("R05", 420, 490),
    ("R06", 498, 568),
    ("R07", 586, 652),
    ("R08", 670, 736),
    ("R09", 768, 834),
    ("R10", 862, 928),
    ("R11", 938, 1020),
    ("R12", 1022, 1090),
    ("R13", 1090, 1180),
    ("R14", 1182, 1266),
    ("R15", 1274, 1370),
    ("R16", 1370, 1500),
    ("R17", 1528, 1610),
    ("R18", 1625, 1760),
    ("R19", 1760, 1830),
    ("R20", 1840, 1950),
    ("R21", 1950, 2090),
    ("R22", 2110, 2210),
    ("R23", 2228, 2310),
)

PAGE_BANDS = (
    ("01_base", 96, 934),
    ("02_skills", 922, 1510),
    ("03_lower", 1510, 2320),
)


def is_foreground(pixel):
    """Return True for non-white sheet content."""
    red, green, blue = pixel[:3]
    return red < BACKGROUND_THRESHOLD or green < BACKGROUND_THRESHOLD or blue < BACKGROUND_THRESHOLD


def find_components(image, row_id, top, bottom):
    """Return detected visual components inside one numbered sheet row."""
    pixels = image.load()
    seen = set()
    components = []
    right_bound = ROW_RIGHT_OVERRIDES.get(row_id, ACTION_RIGHT)
    for y in range(top, bottom):
        for x in range(ACTION_LEFT, right_bound):
            if (x, y) in seen or not is_foreground(pixels[x, y]):
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
                        next_x < ACTION_LEFT
                        or next_x >= right_bound
                        or next_y < top
                        or next_y >= bottom
                        or (next_x, next_y) in seen
                        or not is_foreground(pixels[next_x, next_y])
                    ):
                        continue
                    seen.add((next_x, next_y))
                    queue.append((next_x, next_y))

            left = min(xs)
            right = max(xs) + 1
            component_top = min(ys)
            component_bottom = max(ys) + 1
            width = right - left
            height = component_bottom - component_top
            area = len(xs)
            if row_id == "R21" and component_bottom <= 1975:
                continue
            if area >= 110 and width >= 8 and height >= 16:
                components.append((left, component_top, right, component_bottom, area))
    return sorted(components, key=lambda box: (box[0], box[1]))


def load_font(size):
    """Load a readable Windows font with a Pillow fallback."""
    for font_name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def label_reference(sheet, index):
    """Draw row lanes and stable ids over a scaled copy of the source."""
    scale = 2
    annotated = sheet.resize((sheet.width * scale, sheet.height * scale), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(annotated)
    label_font = load_font(16)
    row_font = load_font(18)

    for row in index["rows"]:
        top = row["top"] * scale
        bottom = row["bottom"] * scale
        draw.line((ACTION_LEFT * scale, top, ACTION_RIGHT * scale, top), fill=(35, 120, 255), width=2)
        row_label = row["row_id"]
        draw.rectangle((4, top, 82, top + 25), fill=(7, 45, 110), outline=(80, 170, 255), width=2)
        draw.text((10, top + 3), row_label, font=row_font, fill=(255, 255, 255))

        for frame in row["frames"]:
            left, frame_top, right, frame_bottom = (value * scale for value in frame["box"])
            draw.rectangle((left, frame_top, right, frame_bottom), outline=(255, 45, 45), width=2)
            label = frame["frame_id"]
            text_box = draw.textbbox((0, 0), label, font=label_font)
            label_width = text_box[2] - text_box[0] + 8
            label_height = text_box[3] - text_box[1] + 7
            label_x = left
            label_y = max(top + 1, frame_top - label_height)
            draw.rectangle(
                (label_x, label_y, label_x + label_width, label_y + label_height),
                fill=(18, 18, 22),
                outline=(255, 205, 40),
                width=1,
            )
            draw.text((label_x + 4, label_y + 2), label, font=label_font, fill=(255, 255, 255))
    return annotated


def build_index(sheet):
    """Build stable row-local ids for every detected action-canvas component."""
    rows = []
    total_frames = 0
    for row_id, top, bottom in ROW_BANDS:
        frames = []
        for frame_number, box in enumerate(find_components(sheet, row_id, top, bottom), start=1):
            left, frame_top, right, frame_bottom, area = box
            frames.append(
                {
                    "frame_id": f"{row_id}-{frame_number:02d}",
                    "box": [left, frame_top, right, frame_bottom],
                    "area": area,
                }
            )
        rows.append({"row_id": row_id, "top": top, "bottom": bottom, "frames": frames})
        total_frames += len(frames)
    return {
        "source": str(SOURCE_PATH.relative_to(PROJECT_ROOT)),
        "note": "Reference ids only. User approval defines animation grouping.",
        "rows": rows,
        "total_detected_components": total_frames,
    }


def save_pages(annotated):
    """Export readable page crops in addition to the full long sheet."""
    paths = []
    scale = 2
    for page_id, top, bottom in PAGE_BANDS:
        page = annotated.crop((0, top * scale, annotated.width, bottom * scale))
        path = REFERENCE_ROOT / f"goku_sheet_numbered_{page_id}.png"
        page.save(path)
        paths.append(path)
    return paths


def run():
    """Create full and paged numbered references without editing the source."""
    if not SOURCE_PATH.is_file():
        print(f"Missing source sheet: {SOURCE_PATH}")
        return 1

    sheet = Image.open(SOURCE_PATH).convert("RGB")
    REFERENCE_ROOT.mkdir(parents=True, exist_ok=True)
    index = build_index(sheet)
    annotated = label_reference(sheet, index)
    annotated.save(FULL_REFERENCE_PATH)
    page_paths = save_pages(annotated)
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")

    for row in index["rows"]:
        print(f"[OK] {row['row_id']}: {len(row['frames'])} detected component(s)")
    print(f"Total detected components: {index['total_detected_components']}")
    print(f"Full reference: {FULL_REFERENCE_PATH}")
    for path in page_paths:
        print(f"Page reference: {path}")
    print(f"Index: {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
