"""Presentation-only animation pacing helpers."""


def get_animation_dt(preferences, dt):
    """Scale visual playback without changing combat simulation time."""
    if not preferences:
        return dt
    speed = preferences.get("animation_speed", 1.0)
    if not isinstance(speed, (int, float)) or isinstance(speed, bool):
        return dt
    return dt * max(0.25, min(2.0, float(speed)))
