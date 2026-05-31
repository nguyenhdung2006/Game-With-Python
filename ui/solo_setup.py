"""Solo pre-fight HP setup sliders."""

import pygame

from settings import HEIGHT, WHITE, WIDTH


BG = (12, 14, 24)
PANEL = (28, 31, 44)
ACCENT = (130, 220, 255)
BOSS_ACCENT = (255, 160, 115)
MUTED = (185, 192, 206)
SLIDER_LEFT = WIDTH // 2 - 260
SLIDER_WIDTH = 520
SLIDER_HEIGHT = 10
SLIDER_Y = (290, 410)


def draw_solo_setup(surface, player_hp, boss_hp, selected_slider, slider_specs):
    """Draw a compact Solo setup screen with two adjustable HP sliders."""
    surface.fill(BG)
    draw_center_text(surface, "SOLO / VERSUS SETUP", 118, 58, ACCENT)
    draw_center_text(surface, "Adjust match durability", 180, 34, WHITE)

    values = (player_hp, boss_hp)
    labels = ("PLAYER HP", "BOSS HP")
    colors = (ACCENT, BOSS_ACCENT)
    for index, (label, value, color, spec) in enumerate(zip(labels, values, colors, slider_specs)):
        draw_slider(surface, index, label, value, color, spec, index == selected_slider)

    draw_center_text(surface, "Up / Down selects. A / D or Left / Right adjusts.", HEIGHT - 118, 26, MUTED)
    draw_center_text(surface, "Enter starts the fight. Esc returns to Mode Select.", HEIGHT - 78, 28, WHITE)


def draw_slider(surface, index, label, value, color, spec, selected):
    """Draw one fixed-size HP slider."""
    minimum, maximum, _ = spec
    y = SLIDER_Y[index]
    panel_rect = pygame.Rect(SLIDER_LEFT - 28, y - 56, SLIDER_WIDTH + 56, 104)
    pygame.draw.rect(surface, PANEL, panel_rect, border_radius=6)
    pygame.draw.rect(surface, color if selected else MUTED, panel_rect, 2, border_radius=6)

    font = pygame.font.Font(None, 32)
    value_font = pygame.font.Font(None, 38)
    surface.blit(font.render(label, True, color), (SLIDER_LEFT, y - 42))
    value_surface = value_font.render(str(value), True, WHITE)
    surface.blit(value_surface, (SLIDER_LEFT + SLIDER_WIDTH - value_surface.get_width(), y - 44))

    track_rect = pygame.Rect(SLIDER_LEFT, y + 6, SLIDER_WIDTH, SLIDER_HEIGHT)
    pygame.draw.rect(surface, (60, 66, 82), track_rect, border_radius=5)
    ratio = (value - minimum) / (maximum - minimum)
    fill_rect = pygame.Rect(track_rect.left, track_rect.top, round(track_rect.width * ratio), track_rect.height)
    pygame.draw.rect(surface, color, fill_rect, border_radius=5)
    handle_x = track_rect.left + round(track_rect.width * ratio)
    pygame.draw.circle(surface, WHITE, (handle_x, track_rect.centery), 10)
    pygame.draw.circle(surface, color, (handle_x, track_rect.centery), 10, 3)


def slider_index_at(position):
    """Return the clicked slider index, allowing a comfortable vertical target."""
    x, y = position
    if not SLIDER_LEFT - 16 <= x <= SLIDER_LEFT + SLIDER_WIDTH + 16:
        return None
    for index, slider_y in enumerate(SLIDER_Y):
        if slider_y - 12 <= y <= slider_y + 28:
            return index
    return None


def value_from_slider_x(x, spec):
    """Convert a pointer x coordinate into a clamped stepped slider value."""
    minimum, maximum, step = spec
    ratio = max(0.0, min(1.0, (x - SLIDER_LEFT) / SLIDER_WIDTH))
    raw_value = minimum + ratio * (maximum - minimum)
    stepped_value = round((raw_value - minimum) / step) * step + minimum
    return max(minimum, min(maximum, stepped_value))


def draw_center_text(surface, text, center_y, size, color):
    """Draw one centered setup label."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, center_y)))
