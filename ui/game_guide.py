"""Polished gameplay guide board for menu preview and in-match help."""

import pygame

from settings import HEIGHT, WHITE, WIDTH
from ui.fonts import get_font


BG = (10, 13, 22)
DIM = (0, 0, 0, 188)
PANEL = (17, 23, 36)
CARD = (26, 35, 52)
CARD_BORDER = (75, 104, 140)
ACCENT = (130, 220, 255)
TECHNIQUE = (255, 214, 115)
MUTED = (185, 198, 218)
TIP = (145, 236, 190)


def draw_game_guide(surface, input_manager=None, overlay=False, mode_name="all"):
    """Draw the complete control guide as a menu screen or modal overlay."""
    if overlay:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill(DIM)
        surface.blit(dim, (0, 0))
    else:
        surface.fill(BG)

    panel = pygame.Rect(28, 22, WIDTH - 56, HEIGHT - 44)
    pygame.draw.rect(surface, PANEL, panel, border_radius=10)
    pygame.draw.rect(surface, ACCENT, panel, 2, border_radius=10)

    title = get_font(52).render("HOW TO PLAY", True, WHITE)
    surface.blit(title, (panel.left + 26, panel.top + 18))
    subtitle = get_font(23).render("Combat preview  |  Learn the rhythm, then build your own combo.", True, MUTED)
    surface.blit(subtitle, (panel.left + 28, panel.top + 66))

    cards = (
        ("MOVEMENT", ACCENT, movement_rows(input_manager)),
        ("MELEE & DEFENSE", (255, 182, 122), melee_rows(input_manager)),
        ("TECHNIQUES", TECHNIQUE, technique_rows(input_manager)),
        ("FLOW", (180, 168, 255), flow_rows(input_manager)),
    )
    card_width = 282
    gap = 14
    start_x = panel.left + 26
    for index, (title_text, color, rows) in enumerate(cards):
        draw_guide_card(
            surface,
            pygame.Rect(start_x + index * (card_width + gap), panel.top + 104, card_width, 344),
            title_text,
            color,
            rows,
        )

    draw_preview_flow(surface, panel, mode_name)
    footer = (
        f"{binding_label(input_manager, 'help', 'H')}: Close Guide"
        if overlay
        else f"{binding_label(input_manager, 'back', 'Esc')}: Return to Mode Select"
    )
    rendered = get_font(24).render(footer, True, WHITE)
    surface.blit(rendered, rendered.get_rect(center=(WIDTH // 2, panel.bottom - 22)))


def draw_guide_card(surface, rect, title, color, rows):
    """Draw one categorized controls card."""
    pygame.draw.rect(surface, CARD, rect, border_radius=8)
    pygame.draw.rect(surface, CARD_BORDER, rect, 2, border_radius=8)
    pygame.draw.rect(surface, color, (rect.left, rect.top, rect.width, 5), border_radius=5)
    surface.blit(get_font(25).render(title, True, color), (rect.left + 14, rect.top + 18))

    for index, (key, label, detail) in enumerate(rows):
        y = rect.top + 62 + index * 53
        draw_key_badge(surface, rect.left + 14, y, key, color)
        surface.blit(get_font(22).render(label, True, WHITE), (rect.left + 72, y + 1))
        surface.blit(get_font(18).render(detail, True, MUTED), (rect.left + 72, y + 23))


def draw_key_badge(surface, x, y, key, color):
    """Draw one compact keycap-style input badge."""
    width = max(46, get_font(20).size(key)[0] + 16)
    badge = pygame.Rect(x, y, width, 34)
    pygame.draw.rect(surface, (12, 17, 28), badge, border_radius=5)
    pygame.draw.rect(surface, color, badge, 2, border_radius=5)
    rendered = get_font(20).render(key, True, WHITE)
    surface.blit(rendered, rendered.get_rect(center=badge.center))


def draw_preview_flow(surface, panel, mode_name):
    """Draw a small game-plan strip so the guide also works as a preview board."""
    title = get_font(22).render("COMBAT RHYTHM PREVIEW", True, TIP)
    surface.blit(title, (panel.left + 28, panel.top + 470))
    steps = ("MOVE", "PARRY", "COMBO", "TECHNIQUE", "REWARD / REMATCH")
    x = panel.left + 28
    y = panel.top + 502
    for index, step in enumerate(steps):
        width = 204 if index == len(steps) - 1 else 142
        rect = pygame.Rect(x, y, width, 42)
        pygame.draw.rect(surface, (25, 48, 53), rect, border_radius=7)
        pygame.draw.rect(surface, TIP, rect, 2, border_radius=7)
        rendered = get_font(20).render(step, True, WHITE)
        surface.blit(rendered, rendered.get_rect(center=rect.center))
        x += width + 32
        if index < len(steps) - 1:
            pygame.draw.line(surface, TIP, (x - 25, rect.centery), (x - 9, rect.centery), 3)
            pygame.draw.line(surface, TIP, (x - 14, rect.centery - 5), (x - 9, rect.centery), 3)
            pygame.draw.line(surface, TIP, (x - 14, rect.centery + 5), (x - 9, rect.centery), 3)

    tip = "Solo: deal damage to charge energy." if mode_name == "solo" else "Dungeon: clear rooms, choose rewards, defeat the boss."
    if mode_name == "all":
        tip = "Tip: tap Guard for a parry; hold Guard for safer blocking."
    surface.blit(get_font(20).render(tip, True, MUTED), (panel.left + 28, panel.top + 558))


def movement_rows(input_manager):
    return (
        (binding_label(input_manager, "move_left", "A") + "/" + binding_label(input_manager, "move_right", "D"), "Move", "Control spacing"),
        (binding_label(input_manager, "jump", "W"), "Jump", "Avoid grounded pressure"),
        (binding_label(input_manager, "dash", "Shift"), "Dash", "Fast reposition"),
        (binding_label(input_manager, "dodge", "L"), "Dodge", "Short evade with i-frames"),
    )


def melee_rows(input_manager):
    return (
        (binding_label(input_manager, "attack", "J"), "Punch Combo", "Chain up to 5 hits"),
        (binding_label(input_manager, "kick", "C"), "Kick Combo", "3 hits with launch"),
        (binding_label(input_manager, "guard", "K"), "Tap: Parry", "Earn a counter window"),
        (binding_label(input_manager, "guard", "K"), "Hold: Block", "Reduce incoming damage"),
    )


def technique_rows(input_manager):
    return (
        (binding_label(input_manager, "skill_1", "U"), "Ki Blast", "Fast ranged pressure"),
        (binding_label(input_manager, "skill_2", "I"), "Kamehameha", "Grounded piercing beam"),
        (binding_label(input_manager, "skill_3", "O"), "Energy Disc", "Delayed spinning projectile"),
        ("AUTO", "Super Saiyan", "Fill SAIYAN gauge for x2 damage"),
    )


def flow_rows(input_manager):
    return (
        (binding_label(input_manager, "pause", "P"), "Pause", "Freeze the current fight"),
        (binding_label(input_manager, "help", "H"), "Guide", "Open this preview board"),
        (binding_label(input_manager, "confirm", "Enter"), "Confirm", "Start / continue / reward"),
        (binding_label(input_manager, "retry", "R"), "Restart", "Use while paused or ended"),
        (binding_label(input_manager, "back", "Esc"), "Back", "Return to Mode Select"),
    )


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
