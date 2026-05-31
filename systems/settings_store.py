"""Fault-tolerant local JSON persistence for player preferences only."""

import json
from copy import deepcopy
from pathlib import Path

from config.default_settings import DEFAULT_SETTINGS
from systems.input_manager import normalize_key_bindings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS_PATH = PROJECT_ROOT / "data" / "settings.json"


class SettingsStore:
    """Load, validate, and save local settings without owning progression."""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else DEFAULT_SETTINGS_PATH
        self.settings = deepcopy(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        """Load local settings or recreate safe defaults when input is unusable."""
        try:
            with self.path.open("r", encoding="utf-8") as settings_file:
                loaded_settings = json.load(settings_file)
            if not isinstance(loaded_settings, dict):
                raise ValueError("settings root must be an object")
        except (OSError, ValueError, json.JSONDecodeError, TypeError):
            self.reset_to_defaults()
            return self.settings

        normalized = deepcopy(DEFAULT_SETTINGS)
        for key in DEFAULT_SETTINGS:
            if key in loaded_settings:
                normalized[key] = normalize_setting(key, loaded_settings[key])
        self.settings.clear()
        self.settings.update(normalized)
        self.save()
        return self.settings

    def save(self):
        """Persist current preferences when the local folder is writable."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as settings_file:
                json.dump(self.settings, settings_file, indent=2, sort_keys=True)
                settings_file.write("\n")
            return True
        except OSError:
            return False

    def reset_to_defaults(self):
        """Replace preferences with defaults and attempt to persist them."""
        self.settings.clear()
        self.settings.update(deepcopy(DEFAULT_SETTINGS))
        self.save()
        return self.settings

    def get(self, key):
        """Read one setting using its configured default as a fallback."""
        return self.settings.get(key, DEFAULT_SETTINGS[key])

    def set(self, key, value):
        """Validate and persist one known setting."""
        if key not in DEFAULT_SETTINGS:
            raise KeyError(f"Unknown setting: {key}")
        self.settings[key] = normalize_setting(key, value)
        self.save()
        return self.settings[key]


def normalize_setting(key, value):
    """Coerce known preference values into conservative safe ranges."""
    default = DEFAULT_SETTINGS[key]
    if key == "key_bindings":
        return normalize_key_bindings(value)
    if isinstance(default, bool):
        return value if isinstance(value, bool) else default

    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return default

    if key == "camera_shake_strength":
        return round(max(0.0, min(2.0, float(value))), 1)
    return round(max(0.0, min(1.0, float(value))), 1)
