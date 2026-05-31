"""Shared readable controls overlay for Solo and Dungeon modes."""

import pygame

from settings import HEIGHT, WHITE, WIDTH


DIM_COLOR = (0, 0, 0, 178)
PANEL = (18, 22, 34)
MUTED = (190, 198, 212)
ACCENT = (255, 214, 115)


def draw_controls_overlay(surface, mode_name, input_manager=None):
    """Dim the current screen and draw mode-relevant input help."""
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill(DIM_COLOR)
    surface.blit(dim, (0, 0))

    panel = pygame.Rect(WIDTH // 2 - 420, HEIGHT // 2 - 280, 840, 560)
    pygame.draw.rect(surface, PANEL, panel, border_radius=8)
    pygame.draw.rect(surface, WHITE, panel, 2, border_radius=8)

    title_font = pygame.font.Font(None, 60)
    text_font = pygame.font.Font(None, 29)
    title = title_font.render("Controls", True, WHITE)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, panel.top + 54)))

    columns = get_controls_columns(mode_name, input_manager)
    for column_index, lines in enumerate(columns):
        x = panel.left + 58 + column_index * 400
        for line_index, line in enumerate(lines):
            if not line:
                continue
            color = ACCENT if line.isupper() else MUTED
            rendered = text_font.render(line, True, color)
            surface.blit(rendered, (x, panel.top + 104 + line_index * 32))


def draw_controls_hint(surface, input_manager=None):
    """Draw the optional compact reminder for pause and controls help."""
    font = pygame.font.Font(None, 24)
    pause = binding_label(input_manager, "pause", "P")
    help_key = binding_label(input_manager, "help", "H")
    rendered = font.render(f"{pause}: Pause   {help_key}: Controls", True, MUTED)
    surface.blit(rendered, (WIDTH - rendered.get_width() - 18, HEIGHT - rendered.get_height() - 14))


def get_controls_columns(mode_name, input_manager):
    """Build mode help from the active binding labels."""
    label = lambda action, fallback: binding_label(input_manager, action, fallback)
    shared_column = (
        "GLOBAL",
        f"{label('back', 'Esc')}  Return to Mode Select",
        f"{label('pause', 'P')}    Pause / resume",
        f"{label('help', 'H')}    Hide controls",
        "",
        "COMBAT",
        f"{label('move_left', 'A')}/{label('move_right', 'D')}  Move",
        f"{label('jump', 'W')}    Jump",
        f"{label('dash', 'Shift')} Dash",
        f"{label('attack', 'J')}    Light combo",
        f"{label('guard', 'K')}    Guard / parry",
        f"{label('dodge', 'L')}    Dodge",
    )
    if mode_name == "solo":
        mode_column = (
            "SOLO SKILLS",
            f"{label('skill_1', 'U')}    Combo Burst",
            f"{label('skill_2', 'I')}    Kamehameha",
            f"{label('skill_3', 'O')}    Locked",
            "",
            "FLOW",
            f"{label('retry', 'R')}    Rematch on end screen",
            f"{label('retry', 'R')}    Restart while paused",
            "",
            "SETUP",
            "Up/Down  Select HP slider",
            f"{label('move_left', 'A')}/{label('move_right', 'D')}      Adjust HP",
            f"{label('confirm', 'Enter')}    Start fight",
        )
    else:
        mode_column = (
            "DUNGEON SKILLS",
            f"{label('skill_1', 'U')}    Ki Blast",
            f"{label('skill_2', 'I')}    Kamehameha",
            f"{label('skill_3', 'O')}    Locked",
            "",
            "FLOW",
            f"{label('confirm', 'Enter')} Continue / confirm",
            f"{label('move_left', 'A')}/{label('move_right', 'D')}   Select reward",
            f"{label('retry', 'R')}     Retry on end screen",
            f"{label('retry', 'R')}     Restart while paused",
        )
    return shared_column, mode_column


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
