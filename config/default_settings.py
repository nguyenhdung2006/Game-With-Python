"""Safe local preference defaults for the prototype settings foundation."""


DEFAULT_SETTINGS = {
    "master_volume": 1.0,
    "sfx_volume": 1.0,
    "music_volume": 1.0,
    "screen_shake_enabled": True,
    "camera_shake_strength": 1.0,
    "show_controls_hint": True,
    "fullscreen_enabled": False,
}

# Volume settings are stored for future audio integration. Fullscreen is a
# persisted placeholder only until display-mode switching is implemented safely.
SETTINGS_MENU_ITEMS = (
    {"key": "master_volume", "label": "Master Volume", "kind": "number", "step": 0.1},
    {"key": "sfx_volume", "label": "SFX Volume", "kind": "number", "step": 0.1},
    {"key": "music_volume", "label": "Music Volume", "kind": "number", "step": 0.1},
    {"key": "screen_shake_enabled", "label": "Screen Shake", "kind": "toggle"},
    {"key": "camera_shake_strength", "label": "Camera Shake Strength", "kind": "number", "step": 0.1},
    {"key": "show_controls_hint", "label": "Controls Hint", "kind": "toggle"},
    {"key": "fullscreen_enabled", "label": "Fullscreen (Placeholder)", "kind": "toggle"},
)
