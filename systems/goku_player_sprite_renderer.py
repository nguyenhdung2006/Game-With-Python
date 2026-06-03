"""User-approved Goku sprite playback with conservative unmapped fallbacks."""

from pathlib import Path
import json
import re
from weakref import WeakKeyDictionary

import pygame

from config.goku_sprite_config import (
    GOKU_KI_BLAST_ACTION_IDS,
    GOKU_PLAYER_ANIMATION_CONFIG,
    GOKU_PLAYER_RENDER_SCALE,
)
from systems.animation_timing import get_animation_dt


BOTTOM_OFFSET = 4
PACEABLE_ACTIONS = {"walk", "run", "jump", "guard"}


class GokuPlayerSpriteRenderer:
    """Cache and draw only the Goku frame groups approved by the user."""

    def __init__(self, asset_root=None, preferences=None):
        if asset_root is None:
            asset_root = (
                Path(__file__).resolve().parents[1]
                / "assets"
                / "sprites"
                / "goku"
                / "approved_player_frames"
            )
        self.asset_root = Path(asset_root)
        self.preferences = preferences if preferences is not None else {}
        self.manifest_frames = self.load_manifest_frames()
        self.frames = {
            action_id: self.load_animation(action_id)
            for action_id in GOKU_PLAYER_ANIMATION_CONFIG
        }
        self.transformed_frame_cache = {}
        self.playback = WeakKeyDictionary()

    def update(self, player, visual_state, dt, action_override=None):
        """Advance presentation playback without changing gameplay timers."""
        action_id = self.resolve_action(visual_state, action_override)
        frames = self.frames.get(action_id, ())
        if not frames:
            return

        playback = self.get_playback(player)
        if playback["action_id"] != action_id:
            playback.update(action_id=action_id, frame_index=0, timer=0.0)
            return

        settings = GOKU_PLAYER_ANIMATION_CONFIG[action_id]
        animation_dt = get_animation_dt(self.preferences, dt) if action_id in PACEABLE_ACTIONS else dt
        playback["timer"] += animation_dt
        while playback["timer"] >= settings["frame_delay"]:
            playback["timer"] -= settings["frame_delay"]
            if settings["loop"]:
                playback["frame_index"] = (playback["frame_index"] + 1) % len(frames)
            else:
                playback["frame_index"] = min(playback["frame_index"] + 1, len(frames) - 1)

    def draw(self, surface, player, draw_rect, visual_state, action_override=None):
        """Draw the selected Goku frame and return its positioned rect."""
        action_id = self.resolve_action(visual_state, action_override)
        frames = self.frames.get(action_id, ())
        if not frames:
            return None

        playback = self.get_playback(player)
        if playback["action_id"] != action_id:
            playback.update(action_id=action_id, frame_index=0, timer=0.0)
        frame_index = playback["frame_index"] % len(frames)
        frame = self.get_transformed_frame(action_id, frame_index, player.facing < 0)
        frame_rect = frame.get_rect(midbottom=(draw_rect.centerx, draw_rect.bottom + BOTTOM_OFFSET))
        surface.blit(frame, frame_rect)
        return frame_rect

    def get_transformed_frame(self, action_id, frame_index, flip_x):
        """Reuse left-facing frame transforms at high render rates."""
        cache_key = (action_id, frame_index, flip_x)
        if cache_key not in self.transformed_frame_cache:
            frame = self.frames[action_id][frame_index]
            self.transformed_frame_cache[cache_key] = (
                pygame.transform.flip(frame, True, False) if flip_x else frame
            )
        return self.transformed_frame_cache[cache_key]

    def resolve_action(self, visual_state, action_override=None):
        """Map current mechanics onto approved groups only."""
        if action_override in self.frames and self.frames[action_override]:
            return action_override

        candidates = {
            "skill_1": (GOKU_KI_BLAST_ACTION_IDS[0], "idle_hold"),
            "skill_2": ("skill_2", "idle_hold"),
            "super_saiyan_skill_2": ("super_saiyan_skill_2", "skill_2", "super_saiyan_idle"),
            "skill_3": ("skill_3", "idle_hold"),
            "punch_1": ("attack_punch_1", "idle_hold"),
            "punch_2": ("attack_punch_2", "idle_hold"),
            "punch_3": ("attack_punch_3", "idle_hold"),
            "punch_4": ("attack_punch_4", "idle_hold"),
            "punch_5": ("attack_punch_5", "idle_hold"),
            "super_saiyan_punch_1": ("super_saiyan_punch_1", "attack_punch_1", "super_saiyan_idle"),
            "super_saiyan_punch_2": ("super_saiyan_punch_2", "attack_punch_2", "super_saiyan_idle"),
            "super_saiyan_punch_3": ("super_saiyan_punch_3", "attack_punch_3", "super_saiyan_idle"),
            "super_saiyan_punch_4": ("super_saiyan_punch_4", "attack_punch_4", "super_saiyan_idle"),
            "super_saiyan_punch_5": ("super_saiyan_punch_5", "attack_punch_5", "super_saiyan_idle"),
            "punch_recovery": ("punch_recovery", "idle_hold"),
            "kick_1": ("kick_1", "idle_hold"),
            "kick_2": ("kick_2", "idle_hold"),
            "kick_3": ("kick_3", "idle_hold"),
            "super_saiyan_kick_1": ("super_saiyan_kick_1", "kick_1", "super_saiyan_idle"),
            "super_saiyan_kick_2": ("super_saiyan_kick_2", "kick_2", "super_saiyan_idle"),
            "super_saiyan_kick_3": ("super_saiyan_kick_3", "kick_3", "super_saiyan_idle"),
            "kick_recovery_1": ("kick_recovery_1", "idle_hold"),
            "counter": ("kick_3", "idle_hold"),
            "hurt": ("hurt_1", "idle_hold"),
            "hurt_1": ("hurt_1", "idle_hold"),
            "hurt_2": ("hurt_2", "hurt_1", "idle_hold"),
            "hurt_3": ("hurt_3", "hurt_2", "hurt_1", "idle_hold"),
            "hurt_4": ("hurt_4", "hurt_3", "hurt_2", "hurt_1", "idle_hold"),
            "defeated": ("defeated", "hurt_4", "idle_hold"),
            "block": ("guard", "idle_hold"),
            "parry": ("guard", "idle_hold"),
            "dash": ("run", "walk", "idle_hold"),
            "dodge": ("run", "walk", "idle_hold"),
            "jump": ("jump", "idle_hold"),
            "fall": ("jump", "idle_hold"),
            "run": ("walk", "idle_hold"),
        }.get(visual_state)
        if candidates is None and visual_state in self.frames and self.frames[visual_state]:
            return visual_state
        if candidates is None:
            candidates = ("idle_hold",)
        for action_id in candidates:
            if self.frames.get(action_id):
                return action_id
        return "idle_hold"

    def get_playback(self, player):
        """Return one playback cursor per player instance."""
        if player not in self.playback:
            self.playback[player] = {"action_id": None, "frame_index": 0, "timer": 0.0}
        return self.playback[player]

    def has_frames(self):
        """Return True when the basic approved fallback loaded."""
        return bool(self.frames.get("idle_hold"))

    def load_manifest_frames(self):
        """Return runtime frame filenames listed in the generated Goku manifest."""
        manifest_path = self.asset_root.parent / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return {
            action["action_id"]: tuple(
                frame["filename"]
                for frame in action.get("frames", ())
                if "filename" in frame
            )
            for action in manifest.get("approved_player_actions", ())
        }

    def load_animation(self, action_id):
        """Load naturally sorted generated frames with crisp pixel scaling."""
        try:
            action_folder = self.asset_root / action_id
            manifest_filenames = self.manifest_frames.get(action_id)
            if manifest_filenames:
                paths = [
                    action_folder / filename
                    for filename in manifest_filenames
                    if (action_folder / filename).is_file()
                ]
            else:
                paths = sorted(action_folder.glob("frame_*.png"), key=self.natural_sort_key)
            return [self.load_scaled_image(path) for path in paths]
        except (OSError, pygame.error):
            return []

    def load_scaled_image(self, path):
        """Load one transparent generated frame."""
        image = pygame.image.load(str(path)).convert_alpha()
        width = max(1, round(image.get_width() * GOKU_PLAYER_RENDER_SCALE))
        height = max(1, round(image.get_height() * GOKU_PLAYER_RENDER_SCALE))
        return pygame.transform.scale(image, (width, height))

    @staticmethod
    def natural_sort_key(path):
        """Sort generated frame names numerically."""
        return tuple(
            (1, int(part)) if part.isdigit() else (0, part)
            for part in re.split(r"(\d+)", path.name.lower())
        )
