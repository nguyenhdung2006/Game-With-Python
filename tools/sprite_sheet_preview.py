"""Open a small manual preview window for configured prototype enemy sheets."""

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
from tools.validate_enemy_sprites import cut_sheet_frames, validate_sprite_config


BACKGROUND = (24, 27, 34)
TEXT = (235, 239, 245)
SUBTLE_TEXT = (154, 164, 178)


def load_animation_frames(sprite_config, animation_name):
    """Load one configured animation strip for the optional manual viewer."""
    animation = sprite_config["animations"][animation_name]
    sheet = pygame.image.load(str(sprite_config["root_folder"] / animation["filename"]))
    frames = cut_sheet_frames(
        sheet,
        sprite_config["frame_width"],
        sprite_config["frame_height"],
        animation["frame_count"],
        animation.get("sheet_row", 0),
    )
    return frames, animation


def draw_text(surface, font, text, position, color=TEXT):
    """Draw one preview label."""
    surface.blit(font.render(text, True, color), position)


def run_preview(enemy_id, scale=4):
    """Preview configured strips; return False when validation blocks launch."""
    sprite_config = ENEMY_SPRITE_CONFIGS[enemy_id]
    report = validate_sprite_config(sprite_config)
    if not report["valid"]:
        print(f"Cannot preview '{enemy_id}': configured sheets did not validate.")
        return False

    pygame.init()
    window = pygame.display.set_mode((720, 560))
    pygame.display.set_caption(f"Dungeon enemy sprite preview: {enemy_id}")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    small_font = pygame.font.Font(None, 23)
    animation_names = list(sprite_config["animations"])
    animation_index = 0
    frame_index = 0
    elapsed = 0.0
    flip_x = False
    running = True
    frames, animation = load_animation_frames(sprite_config, animation_names[animation_index])

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    animation_index = (animation_index + 1) % len(animation_names)
                    frame_index = 0
                    elapsed = 0.0
                    frames, animation = load_animation_frames(sprite_config, animation_names[animation_index])
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    animation_index = (animation_index - 1) % len(animation_names)
                    frame_index = 0
                    elapsed = 0.0
                    frames, animation = load_animation_frames(sprite_config, animation_names[animation_index])
                elif event.key == pygame.K_f:
                    flip_x = not flip_x

        elapsed += dt
        if frames and elapsed >= animation["frame_speed"]:
            elapsed -= animation["frame_speed"]
            if frame_index < len(frames) - 1:
                frame_index += 1
            elif not animation["hold_last"]:
                frame_index = 0

        window.fill(BACKGROUND)
        current_name = animation_names[animation_index]
        draw_text(window, font, f"{enemy_id.upper()} / {current_name}", (24, 22))
        draw_text(window, small_font, "A/D or Left/Right: animation   F: flip   Esc/Q: exit", (24, 58), SUBTLE_TEXT)
        draw_text(
            window,
            small_font,
            f"Frame {frame_index + 1}/{len(frames)}   Speed {animation['frame_speed']:.2f}s   Flip {flip_x}",
            (24, 88),
            SUBTLE_TEXT,
        )
        if frames:
            frame = pygame.transform.flip(frames[frame_index], flip_x, False)
            frame = pygame.transform.scale(frame, (frame.get_width() * scale, frame.get_height() * scale))
            frame_rect = frame.get_rect(center=(window.get_width() // 2, 330))
            window.blit(frame, frame_rect)
        pygame.display.flip()

    pygame.quit()
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("enemy_id", choices=sorted(ENEMY_SPRITE_CONFIGS))
    parser.add_argument("--scale", type=int, default=4, choices=range(1, 6))
    args = parser.parse_args()
    return 0 if run_preview(args.enemy_id, args.scale) else 1


if __name__ == "__main__":
    raise SystemExit(main())
