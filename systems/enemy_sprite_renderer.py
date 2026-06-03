"""Lightweight Dungeon-only enemy sprite-strip playback prototype."""

from weakref import WeakKeyDictionary

import pygame

from config.enemy_sprite_config import ENEMY_SPRITE_CONFIGS
from systems.animation_timing import get_animation_dt


VISUAL_STATE_ANIMATIONS = {
    "idle": ("idle",),
    "chase": ("walk", "idle"),
    "telegraph": ("attack_01", "attack", "idle"),
    "attack": ("attack_02", "attack_01", "attack", "idle"),
    "hurt": ("hurt", "idle"),
    "stagger": ("hurt", "idle"),
    "recovery": ("idle",),
    "defeated": ("death", "idle"),
}


class EnemySpriteRenderer:
    """Cache and draw prototype sprite strips without owning gameplay state."""

    def __init__(self, sprite_configs=None, preferences=None):
        self.sprite_configs = ENEMY_SPRITE_CONFIGS if sprite_configs is None else sprite_configs
        self.preferences = preferences if preferences is not None else {}
        self.frame_cache = {}
        self.transformed_frame_cache = {}
        self.playback = WeakKeyDictionary()

    def update(self, enemy, visual_state, dt):
        """Advance one enemy's presentation frame from its current visual state."""
        sprite_id = self.get_sprite_id(enemy)
        animation_name = self.get_animation_name(sprite_id, visual_state)
        if animation_name is None:
            return
        frames = self.load_frames(sprite_id, animation_name)
        if not frames:
            return

        animation = self.sprite_configs[sprite_id]["animations"][animation_name]
        state = self.get_playback_state(enemy, animation_name)
        animation_dt = get_animation_dt(self.preferences, dt) if animation_name in {"idle", "walk", "death"} else dt
        state["elapsed"] += animation_dt
        while state["elapsed"] >= animation["frame_speed"]:
            state["elapsed"] -= animation["frame_speed"]
            if state["frame_index"] < len(frames) - 1:
                state["frame_index"] += 1
            elif not animation["hold_last"]:
                state["frame_index"] = 0

    def draw(self, surface, enemy, draw_rect, visual_state):
        """Draw one anchored prototype frame, or return False for fallback."""
        sprite_id = self.get_sprite_id(enemy)
        animation_name = self.get_animation_name(sprite_id, visual_state)
        if animation_name is None:
            return False
        frames = self.load_frames(sprite_id, animation_name)
        if not frames:
            return False

        state = self.get_playback_state(enemy, animation_name)
        frame_index = min(state["frame_index"], len(frames) - 1)
        flip_x = getattr(enemy, "facing", 1) < 0
        frame = self.get_transformed_frame(sprite_id, animation_name, frame_index, flip_x)
        config = self.sprite_configs[sprite_id]
        anchor_x, anchor_y = config["feet_anchor"]
        if flip_x:
            anchor_x = config["frame_width"] - anchor_x
        scale = config["render_scale"]
        surface.blit(
            frame,
            (
                round(draw_rect.centerx - anchor_x * scale),
                round(draw_rect.bottom - anchor_y * scale),
            ),
        )
        return True

    def get_sprite_id(self, enemy):
        """Return one configured prototype id from an opted-in archetype."""
        sprite_id = getattr(enemy, "dungeon_sprite_id", None)
        return sprite_id if sprite_id in self.sprite_configs else None

    def get_animation_name(self, sprite_id, visual_state):
        """Map mechanical states onto the first configured compatible strip."""
        if sprite_id not in self.sprite_configs:
            return None
        animations = self.sprite_configs[sprite_id]["animations"]
        candidates = VISUAL_STATE_ANIMATIONS.get(visual_state, ("idle",))
        return next((animation_name for animation_name in candidates if animation_name in animations), None)

    def get_playback_state(self, enemy, animation_name):
        """Reset presentation playback whenever the selected strip changes."""
        state = self.playback.get(enemy)
        if state is None or state["animation_name"] != animation_name:
            state = {
                "animation_name": animation_name,
                "frame_index": 0,
                "elapsed": 0.0,
            }
            self.playback[enemy] = state
        return state

    def load_frames(self, sprite_id, animation_name):
        """Load and cache one configured horizontal row safely."""
        cache_key = (sprite_id, animation_name)
        if cache_key in self.frame_cache:
            return self.frame_cache[cache_key]

        if sprite_id not in self.sprite_configs:
            return ()
        config = self.sprite_configs[sprite_id]
        animation = config["animations"].get(animation_name)
        if animation is None:
            return ()

        sheet_path = config["root_folder"] / animation["filename"]
        try:
            sheet = pygame.image.load(str(sheet_path))
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                sheet = sheet.convert_alpha()
        except (OSError, pygame.error):
            self.frame_cache[cache_key] = ()
            return ()

        frame_width = config["frame_width"]
        frame_height = config["frame_height"]
        frame_count = animation["frame_count"]
        sheet_rows = animation.get("sheet_rows", 1)
        sheet_row = animation.get("sheet_row", 0)
        if not 0 <= sheet_row < sheet_rows:
            self.frame_cache[cache_key] = ()
            return ()
        if sheet.get_size() != (frame_width * frame_count, frame_height * sheet_rows):
            self.frame_cache[cache_key] = ()
            return ()

        frames = tuple(
            sheet.subsurface(
                (index * frame_width, sheet_row * frame_height, frame_width, frame_height)
            ).copy()
            for index in range(frame_count)
        )
        self.frame_cache[cache_key] = frames
        return frames

    def get_transformed_frame(self, sprite_id, animation_name, frame_index, flip_x):
        """Cache pixel-art scale and facing transforms independently."""
        cache_key = (sprite_id, animation_name, frame_index, flip_x)
        if cache_key in self.transformed_frame_cache:
            return self.transformed_frame_cache[cache_key]

        config = self.sprite_configs[sprite_id]
        scale = config["render_scale"]
        frame = self.load_frames(sprite_id, animation_name)[frame_index]
        if flip_x:
            frame = pygame.transform.flip(frame, True, False)
        if scale != 1:
            frame = pygame.transform.scale(
                frame,
                (config["frame_width"] * scale, config["frame_height"] * scale),
            )
        self.transformed_frame_cache[cache_key] = frame
        return frame
