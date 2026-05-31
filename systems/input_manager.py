"""Keyboard action mapping helpers for future configurable controls."""

import pygame

from config.input_config import DEFAULT_KEY_BINDINGS, KEY_BINDING_LABELS


class InputManager:
    """Resolve persisted binding names into Pygame key constants."""

    def __init__(self, preferences=None):
        self.preferences = preferences if preferences is not None else {}
        self.bindings = {}
        self.key_codes = {}
        self.load_bindings(self.preferences.get("key_bindings"))

    def load_bindings(self, bindings=None):
        """Load known JSON-safe bindings and fall back per action."""
        normalized = normalize_key_bindings(bindings)
        self.bindings.clear()
        self.bindings.update(normalized)
        self.key_codes = {
            action: pygame.key.key_code(key_name)
            for action, key_name in self.bindings.items()
        }
        return self.bindings

    def is_pressed(self, action, keys=None):
        """Return True while one action's configured key is held."""
        key_code = self.key_codes.get(action)
        if key_code is None:
            return False
        pressed_keys = pygame.key.get_pressed() if keys is None else keys
        return bool(pressed_keys[key_code])

    def was_pressed(self, action, events):
        """Return True if one action appeared in a KEYDOWN event collection."""
        return any(self.event_matches(action, event) for event in events)

    def event_matches(self, action, event):
        """Return True when one event presses an action's configured key."""
        return event.type == pygame.KEYDOWN and event.key == self.key_codes.get(action)

    def get_binding_label(self, action):
        """Return a compact human-readable label for UI."""
        key_name = self.bindings.get(action, "")
        return KEY_BINDING_LABELS.get(key_name, key_name.upper())


def normalize_key_bindings(bindings):
    """Keep only valid known key names and fill missing actions safely."""
    normalized = DEFAULT_KEY_BINDINGS.copy()
    if not isinstance(bindings, dict):
        return normalized

    for action, default_key_name in DEFAULT_KEY_BINDINGS.items():
        key_name = bindings.get(action, default_key_name)
        if not isinstance(key_name, str):
            continue
        try:
            pygame.key.key_code(key_name)
        except ValueError:
            continue
        normalized[action] = key_name
    return normalized
