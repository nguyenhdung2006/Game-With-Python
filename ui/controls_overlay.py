"""Shared readable controls overlay for Solo and Dungeon modes."""

from settings import HEIGHT, WIDTH
from ui.fonts import get_font
from ui.game_guide import draw_game_guide


MUTED = (190, 198, 212)


def draw_controls_overlay(surface, mode_name, input_manager=None):
    """Dim the current screen and draw mode-relevant input help."""
    draw_game_guide(surface, input_manager, overlay=True, mode_name=mode_name)


def draw_controls_hint(surface, input_manager=None):
    """Draw the optional compact reminder for pause and controls help."""
    font = get_font(24)
    pause = binding_label(input_manager, "pause", "P")
    help_key = binding_label(input_manager, "help", "H")
    rendered = font.render(f"{pause}: Pause   {help_key}: Controls", True, MUTED)
    surface.blit(rendered, (WIDTH - rendered.get_width() - 18, HEIGHT - rendered.get_height() - 14))


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
