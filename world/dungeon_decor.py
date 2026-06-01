"""Cached prototype Dungeon decor assembled from user-provided pixel assets."""

from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPRITE_ROOT = PROJECT_ROOT / "assets" / "sprites"
FREE_STATIC_ROOT = SPRITE_ROOT / "Free" / "Decor" / "Static" / "32x32"
UI_ROOT = SPRITE_ROOT / "ui"

PROP_PATHS = {
    "bones_1": UI_ROOT / "Static" / "bones1.png",
    "bones_2": UI_ROOT / "Static" / "bones2.png",
    "bookshelf": FREE_STATIC_ROOT / "Book shelf 01 2x.png",
    "bookshelf_tall": FREE_STATIC_ROOT / "Book shelf 02 2x.png",
    "chain": FREE_STATIC_ROOT / "Wall Chain 01 2x.png",
    "chair": FREE_STATIC_ROOT / "Chair02 2x.png",
    "chest_open": UI_ROOT / "Static" / "bronze_chest_open.png",
    "coffin": FREE_STATIC_ROOT / "Coffin2x.png",
    "crate": FREE_STATIC_ROOT / "Crate 02 2x.png",
    "flag": FREE_STATIC_ROOT / "Flag Red Big2x.png",
    "painting": FREE_STATIC_ROOT / "Paiting Big2x.png",
    "painting_small": FREE_STATIC_ROOT / "Paiting 1 2x.png",
    "scroll": FREE_STATIC_ROOT / "Scroll2x.png",
    "shield": FREE_STATIC_ROOT / "Shield2x.png",
    "sword": FREE_STATIC_ROOT / "Sword2x.png",
    "table_long": FREE_STATIC_ROOT / "Table Long2x.png",
    "throne": FREE_STATIC_ROOT / "Throne2x.png",
    "vase": FREE_STATIC_ROOT / "Vase Grey2x.png",
    "vase_broken": FREE_STATIC_ROOT / "Vase Grey Broken2x.png",
}
TORCH_PATHS = tuple(UI_ROOT / "Torch" / f"{index:02d}.png" for index in range(3))
DOOR_PATHS = {
    False: UI_ROOT / "Static" / "Front_Door_Closed.png",
    True: UI_ROOT / "Static" / "Front_Door_Open.png",
}


class DungeonDecorRenderer:
    """Draw optional room dressing while keeping combat geometry unchanged."""

    def __init__(self, scale=2, torch_frame_duration=0.16):
        self.scale = scale
        self.torch_frame_duration = torch_frame_duration
        self.torch_frame_index = 0
        self.torch_elapsed = 0.0
        self.image_cache = {}

    def update(self, dt):
        """Advance ambient torch playback only while Dungeon gameplay updates."""
        self.torch_elapsed += dt
        while self.torch_elapsed >= self.torch_frame_duration:
            self.torch_elapsed -= self.torch_frame_duration
            self.torch_frame_index = (self.torch_frame_index + 1) % len(TORCH_PATHS)

    def draw(self, surface, layout, show_exit=False):
        """Draw configured background props and return whether the door loaded."""
        if layout is None:
            return False

        for prop_id, x, y in layout.decor_props:
            self.draw_prop(surface, prop_id, (x, y))
        torch = self.load_image(TORCH_PATHS[self.torch_frame_index])
        if torch is not None:
            for position in layout.torch_positions:
                self.blit_midbottom(surface, torch, position)
        return self.draw_door(surface, layout.exit_position, show_exit)

    def draw_prop(self, surface, prop_id, position):
        """Draw one optional prop without failing the room if its file is absent."""
        path = PROP_PATHS.get(prop_id)
        image = self.load_image(path)
        if image is not None:
            self.blit_midbottom(surface, image, position)

    def draw_door(self, surface, position, show_exit):
        """Draw the current exit door state when its isolated asset is available."""
        if position is None:
            return False
        image = self.load_image(DOOR_PATHS[show_exit])
        if image is None:
            return False
        x, _ = position
        self.blit_midbottom(surface, image, (x + image.get_width() // 2, 540))
        return True

    def load_image(self, path):
        """Load and nearest-scale one pixel-art image with a safe missing fallback."""
        if path is None:
            return None
        cache_key = str(path)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        try:
            image = pygame.image.load(str(path))
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                image = image.convert_alpha()
            if self.scale != 1:
                image = pygame.transform.scale(
                    image,
                    (image.get_width() * self.scale, image.get_height() * self.scale),
                )
        except (OSError, pygame.error):
            image = None
        self.image_cache[cache_key] = image
        return image

    @staticmethod
    def blit_midbottom(surface, image, position):
        """Anchor decor predictably to a wall or floor marker."""
        surface.blit(image, image.get_rect(midbottom=position))
