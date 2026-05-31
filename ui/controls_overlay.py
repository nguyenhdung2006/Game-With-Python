"""Shared readable controls overlay for Solo and Dungeon modes."""

import pygame

from settings import HEIGHT, WHITE, WIDTH


DIM_COLOR = (0, 0, 0, 178)
PANEL = (18, 22, 34)
MUTED = (190, 198, 212)
ACCENT = (255, 214, 115)


SOLO_COLUMNS = (
    (
        "GLOBAL",
        "Esc  Return to Mode Select",
        "P    Pause / resume",
        "H    Hide controls",
        "",
        "ARENA",
        "A/D  Move",
        "W    Jump",
        "Shift Dash",
        "J    Light combo",
        "K    Guard / parry",
        "L    Dodge",
    ),
    (
        "SOLO SKILLS",
        "U    Combo Burst",
        "I    Kamehameha",
        "O    Locked",
        "",
        "FLOW",
        "R    Rematch on end screen",
        "R    Restart while paused",
        "",
        "SETUP",
        "Up/Down  Select HP slider",
        "A/D      Adjust HP",
        "Enter    Start fight",
    ),
)

DUNGEON_COLUMNS = (
    (
        "GLOBAL",
        "Esc  Return to Mode Select",
        "P    Pause / resume",
        "H    Hide controls",
        "",
        "COMBAT",
        "A/D  Move",
        "W    Jump",
        "Shift Dash",
        "J    Light combo",
        "K    Guard / parry",
        "L    Dodge",
    ),
    (
        "DUNGEON SKILLS",
        "U    Ki Blast",
        "I    Kamehameha",
        "O    Locked",
        "",
        "FLOW",
        "Enter Continue / confirm",
        "A/D   Select reward",
        "R     Retry on end screen",
        "R     Restart while paused",
    ),
)


def draw_controls_overlay(surface, mode_name):
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

    columns = SOLO_COLUMNS if mode_name == "solo" else DUNGEON_COLUMNS
    for column_index, lines in enumerate(columns):
        x = panel.left + 58 + column_index * 400
        for line_index, line in enumerate(lines):
            if not line:
                continue
            color = ACCENT if line.isupper() else MUTED
            rendered = text_font.render(line, True, color)
            surface.blit(rendered, (x, panel.top + 104 + line_index * 32))


def draw_controls_hint(surface):
    """Draw the optional compact reminder for pause and controls help."""
    font = pygame.font.Font(None, 24)
    rendered = font.render("P: Pause   H: Controls", True, MUTED)
    surface.blit(rendered, (WIDTH - rendered.get_width() - 18, HEIGHT - rendered.get_height() - 14))
