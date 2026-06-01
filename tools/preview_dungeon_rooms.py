"""Render a contact sheet of the fixed Dungeon room presentation."""

from pathlib import Path
import os
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from managers.dungeon_layout import DungeonLayoutManager
from settings import HEIGHT, WIDTH
from systems.enemy_sprite_renderer import EnemySpriteRenderer
from world.dungeon_decor import DungeonDecorRenderer
from world.dungeon_room import draw_dungeon_room
from entities.basic_enemy import BasicEnemy
from entities.fast_enemy import FastEnemy
from entities.orc_level_enemy import OrcLevel2Enemy, OrcLevel3Enemy
from entities.slime_enemy import SlimeEnemy


OUTPUT_PATH = PROJECT_ROOT / "dungeon-room-preview.png"
PREVIEW_SIZE = (WIDTH // 2, HEIGHT // 2)
ROOM_ENEMY_SAMPLES = (
    ((SlimeEnemy, 380), (BasicEnemy, 820)),
    ((FastEnemy, 460), (OrcLevel2Enemy, 860)),
    ((OrcLevel3Enemy, 820),),
    (),
)


def run():
    """Render every fixed room, including the open-door clear state."""
    pygame.init()
    try:
        pygame.display.set_mode((1, 1))
        layouts = DungeonLayoutManager()
        room_layouts = (*layouts.room_layouts, layouts.clear_layout)
        sheet = pygame.Surface((PREVIEW_SIZE[0] * 2, PREVIEW_SIZE[1] * 2))
        decor_renderer = DungeonDecorRenderer()
        enemy_renderer = EnemySpriteRenderer()
        for index, layout in enumerate(room_layouts):
            room_surface = pygame.Surface((WIDTH, HEIGHT))
            show_exit = index == len(room_layouts) - 1
            draw_dungeon_room(
                room_surface,
                layout,
                show_exit=show_exit,
                decor_renderer=decor_renderer,
            )
            for enemy_class, x in ROOM_ENEMY_SAMPLES[index]:
                enemy = enemy_class(x)
                enemy.rect.bottom = 540
                enemy_renderer.draw(room_surface, enemy, enemy.rect, "idle")
            preview = pygame.transform.scale(room_surface, PREVIEW_SIZE)
            x = PREVIEW_SIZE[0] * (index % 2)
            y = PREVIEW_SIZE[1] * (index // 2)
            sheet.blit(preview, (x, y))
        pygame.image.save(sheet, str(OUTPUT_PATH))
    finally:
        pygame.quit()

    print(f"Saved Dungeon contact sheet: {OUTPUT_PATH}")


if __name__ == "__main__":
    run()
