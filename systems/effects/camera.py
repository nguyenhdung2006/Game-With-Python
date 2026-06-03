"""Camera and hit-impact helpers."""

import random

from config.default_settings import DEFAULT_SETTINGS


class CombatImpact:
    """Tracks hitstop and camera shake after successful hits.

    Hitstop briefly pauses gameplay movement without freezing the app window.
    Camera shake offsets the rendered arena for a few frames to sell impact.
    """

    def __init__(self, preferences=None):
        self.preferences = preferences if preferences is not None else DEFAULT_SETTINGS
        self.hitstop_timer = 0
        self.camera_shake_timer = 0
        self.camera_shake_strength = 0

    def start_hit_impact(self, attack_data):
        """Start hitstop and shake using the current attack's feel values."""
        self.hitstop_timer = max(self.hitstop_timer, attack_data["hitstop"])
        if (
            not self.preferences.get("screen_shake_enabled", True)
            or self.preferences.get("reduce_motion_enabled", False)
        ):
            return

        strength_multiplier = self.preferences.get("camera_shake_strength", 1.0)
        self.camera_shake_timer = max(self.camera_shake_timer, attack_data["shake_duration"])
        self.camera_shake_strength = max(
            self.camera_shake_strength,
            round(attack_data["shake_strength"] * strength_multiplier),
        )

    def update(self, dt):
        """Count down impact timers with delta time."""
        if self.hitstop_timer > 0:
            self.hitstop_timer = max(0, self.hitstop_timer - dt)

        if self.camera_shake_timer > 0:
            self.camera_shake_timer = max(0, self.camera_shake_timer - dt)

            if self.camera_shake_timer == 0:
                self.camera_shake_strength = 0

    def is_hitstop_active(self):
        """Return True while player and enemy updates should be paused."""
        return self.hitstop_timer > 0

    def get_camera_offset(self):
        """Return a small random render offset while camera shake is active."""
        if self.camera_shake_timer <= 0 or self.camera_shake_strength <= 0:
            return 0, 0

        strength = self.camera_shake_strength
        return random.randint(-strength, strength), random.randint(-strength, strength)
