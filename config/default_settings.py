"""Safe local preference defaults for the prototype settings foundation."""

from config.input_config import DEFAULT_KEY_BINDINGS


DEFAULT_SETTINGS = {
    "master_volume": 1.0,
    "sfx_volume": 1.0,
    "music_volume": 1.0,
    "target_fps": 120,
    "animation_speed": 0.8,
    "screen_shake_enabled": True,
    "camera_shake_strength": 1.0,
    "reduce_motion_enabled": False,
    "show_controls_hint": True,
    "fullscreen_enabled": False,
    "key_bindings": DEFAULT_KEY_BINDINGS.copy(),
}

# Volume settings remain useful even when optional audio assets are absent.
SETTINGS_MENU_ITEMS = (
    {"key": "master_volume", "label": "Master Volume", "kind": "number", "step": 0.1},
    {"key": "sfx_volume", "label": "SFX Volume", "kind": "number", "step": 0.1},
    {"key": "music_volume", "label": "Music Volume", "kind": "number", "step": 0.1},
    {
        "key": "target_fps",
        "label": "Target FPS",
        "kind": "choice",
        "options": (60, 120, 144, 240),
    },
    {
        "key": "animation_speed",
        "label": "Animation Speed",
        "kind": "choice",
        "options": (0.65, 0.8, 1.0, 1.15),
    },
    {"key": "screen_shake_enabled", "label": "Screen Shake", "kind": "toggle"},
    {"key": "camera_shake_strength", "label": "Camera Shake Strength", "kind": "number", "step": 0.1},
    {"key": "reduce_motion_enabled", "label": "Reduce Motion", "kind": "toggle"},
    {"key": "show_controls_hint", "label": "Controls Hint", "kind": "toggle"},
    {"key": "fullscreen_enabled", "label": "Fullscreen", "kind": "toggle"},
)
