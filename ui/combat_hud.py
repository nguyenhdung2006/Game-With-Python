"""Shared combat HUD components for player skills and resources."""

import pygame

from settings import HEIGHT, WHITE, WIDTH
from ui.fonts import get_font


PANEL = (14, 19, 30)
PANEL_BORDER = (74, 96, 126)
CARD = (26, 34, 50)
CARD_READY = (35, 58, 76)
CARD_DISABLED = (30, 31, 40)
MUTED = (160, 174, 194)
READY = (142, 235, 190)
WARNING = (255, 184, 120)
SKILL_COLORS = ((110, 195, 255), (138, 180, 255), (255, 218, 118))
SAIYAN_COLOR = (255, 218, 86)


def draw_resource_bar(surface, x, y, width, height, value, maximum, label, fill_color, align_right=False):
    """Draw one compact labeled resource bar with shared combat styling."""
    maximum = max(1, maximum)
    value = max(0, min(value, maximum))
    ratio = value / maximum
    track = pygame.Rect(x, y, width, height)

    pygame.draw.rect(surface, PANEL, track.inflate(6, 6), border_radius=5)
    pygame.draw.rect(surface, PANEL_BORDER, track.inflate(6, 6), 1, border_radius=5)
    pygame.draw.rect(surface, (24, 31, 46), track, border_radius=3)
    if ratio > 0:
        fill = pygame.Rect(track.left, track.top, round(track.width * ratio), track.height)
        pygame.draw.rect(surface, fill_color, fill, border_radius=3)
        highlight = pygame.Rect(fill.left, fill.top, fill.width, max(2, fill.height // 3))
        pygame.draw.rect(surface, brighten(fill_color, 24), highlight, border_radius=3)

    for segment in range(1, 4):
        segment_x = track.left + round(track.width * segment / 4)
        pygame.draw.line(surface, PANEL, (segment_x, track.top + 1), (segment_x, track.bottom - 2), 1)

    rendered = get_font(21).render(f"{label}  {format_number(value)} / {format_number(maximum)}", True, WHITE)
    text_x = track.right - rendered.get_width() if align_right else track.left
    surface.blit(rendered, (text_x, track.bottom + 7))


def draw_saiyan_bar(surface, player, x=60, y=96):
    """Draw the automatic transformation resource and active damage bonus."""
    label = "SUPER SAIYAN  x2.0" if getattr(player, "is_super_saiyan", False) else "SAIYAN"
    draw_resource_bar(
        surface,
        x,
        y,
        300,
        16,
        getattr(player, "saiyan_energy", 0),
        getattr(player, "max_saiyan_energy", 100),
        label,
        SAIYAN_COLOR,
    )


def draw_skill_bar(surface, skill_manager, energy=None, energy_costs=None):
    """Draw the three player techniques as a readable bottom-center hotbar."""
    energy_costs = energy_costs if energy_costs is not None else {}
    panel_width = 700
    panel_height = 78
    panel = pygame.Rect(WIDTH // 2 - panel_width // 2, HEIGHT - panel_height - 14, panel_width, panel_height)
    pygame.draw.rect(surface, PANEL, panel, border_radius=9)
    pygame.draw.rect(surface, PANEL_BORDER, panel, 2, border_radius=9)

    title = get_font(18).render("TECHNIQUES", True, MUTED)
    surface.blit(title, (panel.left + 14, panel.top + 7))

    card_width = 216
    card_height = 43
    gap = 10
    start_x = panel.left + 14
    card_y = panel.top + 27
    for index, skill in enumerate(skill_manager.slots, start=1):
        cost = energy_costs.get(index)
        has_resource = energy is None or cost is None or energy >= cost
        draw_skill_card(
            surface,
            pygame.Rect(start_x + (index - 1) * (card_width + gap), card_y, card_width, card_height),
            skill,
            skill_manager.get_input_label(index),
            SKILL_COLORS[index - 1],
            has_resource,
            cost,
        )


def draw_skill_card(surface, rect, skill, key_label, accent, has_resource, cost):
    """Draw one technique card with cooldown and resource state."""
    is_ready = skill.unlocked and skill.current_cooldown <= 0 and has_resource
    color = CARD_READY if is_ready else CARD
    if not skill.unlocked or not has_resource:
        color = CARD_DISABLED

    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, accent if is_ready else PANEL_BORDER, rect, 2, border_radius=6)

    if skill.current_cooldown > 0 and skill.cooldown > 0:
        ratio = min(1.0, skill.current_cooldown / skill.cooldown)
        cover = pygame.Rect(rect.left, rect.top, round(rect.width * ratio), rect.height)
        cooldown_surface = pygame.Surface(cover.size, pygame.SRCALPHA)
        cooldown_surface.fill((4, 8, 16, 142))
        surface.blit(cooldown_surface, cover.topleft)

    badge = pygame.Rect(rect.left + 7, rect.top + 7, 30, 29)
    pygame.draw.rect(surface, PANEL, badge, border_radius=5)
    pygame.draw.rect(surface, accent, badge, 2, border_radius=5)
    key = get_font(20).render(key_label, True, WHITE)
    surface.blit(key, key.get_rect(center=badge.center))

    name = get_font(21).render(skill.display_name, True, WHITE)
    surface.blit(name, (rect.left + 45, rect.top + 5))
    status = get_skill_status(skill, has_resource, cost)
    status_color = READY if is_ready else WARNING if not has_resource else MUTED
    rendered_status = get_font(17).render(status, True, status_color)
    surface.blit(rendered_status, (rect.left + 46, rect.top + 25))


def get_skill_status(skill, has_resource, cost):
    """Return the concise presentation state for a technique card."""
    if not skill.unlocked:
        return "LOCKED"
    if skill.current_cooldown > 0:
        return f"COOLDOWN {skill.current_cooldown:.1f}s"
    if not has_resource:
        return f"NEED {cost} ENERGY"
    if cost is not None:
        return f"READY  |  {cost} ENERGY"
    return "READY"


def brighten(color, amount):
    """Return a slightly brighter RGB color."""
    return tuple(min(255, channel + amount) for channel in color)


def format_number(value):
    """Keep integral HUD values clean while allowing future fractional resources."""
    if int(value) == value:
        return str(int(value))
    return f"{value:.1f}"
