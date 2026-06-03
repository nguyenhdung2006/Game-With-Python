"""Content-forward preview board for the current playable vertical slice."""

import pygame

from settings import HEIGHT, WHITE, WIDTH
from ui.fonts import get_font


BG = (9, 12, 20)
PANEL = (17, 23, 36)
CARD = (26, 35, 52)
CARD_BORDER = (75, 104, 140)
ACCENT = (130, 220, 255)
SOLO = (255, 182, 122)
DUNGEON = (145, 236, 190)
MUTED = (185, 198, 218)
GOLD = (255, 214, 115)


def draw_game_preview(surface, input_manager=None):
    """Draw a polished overview of the prototype's strongest playable ideas."""
    surface.fill(BG)
    panel = pygame.Rect(28, 22, WIDTH - 56, HEIGHT - 44)
    pygame.draw.rect(surface, PANEL, panel, border_radius=10)
    pygame.draw.rect(surface, ACCENT, panel, 2, border_radius=10)

    surface.blit(get_font(52).render("GAME PREVIEW", True, WHITE), (panel.left + 26, panel.top + 18))
    surface.blit(
        get_font(23).render("Fast anime combat with readable defense, expressive combos, and replayable room choices.", True, MUTED),
        (panel.left + 28, panel.top + 66),
    )

    draw_mode_card(
        surface,
        pygame.Rect(panel.left + 26, panel.top + 112, 566, 166),
        "SOLO / VERSUS",
        SOLO,
        "A focused duel sandbox",
        ("Customize HP before the match", "Charge energy by trading hits", "Read boss combo patterns and punish recovery"),
    )
    draw_mode_card(
        surface,
        pygame.Rect(panel.left + 614, panel.top + 112, 566, 166),
        "DUNGEON / WAVE",
        DUNGEON,
        "A compact replayable combat run",
        ("Clear escalating enemy waves", "Choose one mechanical reward after each room", "Finish with an elite throne-room encounter"),
    )

    draw_journey(surface, pygame.Rect(panel.left + 26, panel.top + 306, 754, 246))
    draw_identity(surface, pygame.Rect(panel.left + 804, panel.top + 306, 376, 246))

    back = binding_label(input_manager, "back", "Esc")
    footer = get_font(24).render(f"{back}: Return to Mode Select", True, WHITE)
    surface.blit(footer, footer.get_rect(center=(WIDTH // 2, panel.bottom - 22)))


def draw_mode_card(surface, rect, title, accent, subtitle, rows):
    """Draw one large preview card for a playable mode."""
    pygame.draw.rect(surface, CARD, rect, border_radius=8)
    pygame.draw.rect(surface, accent, rect, 2, border_radius=8)
    pygame.draw.rect(surface, accent, (rect.left, rect.top, rect.width, 5), border_radius=5)
    surface.blit(get_font(30).render(title, True, accent), (rect.left + 16, rect.top + 18))
    surface.blit(get_font(22).render(subtitle, True, WHITE), (rect.left + 16, rect.top + 52))
    for index, row in enumerate(rows):
        y = rect.top + 88 + index * 23
        pygame.draw.circle(surface, accent, (rect.left + 22, y + 7), 4)
        surface.blit(get_font(19).render(row, True, MUTED), (rect.left + 36, y))


def draw_journey(surface, rect):
    """Draw a small dungeon journey timeline with authored room identity."""
    pygame.draw.rect(surface, CARD, rect, border_radius=8)
    pygame.draw.rect(surface, CARD_BORDER, rect, 2, border_radius=8)
    surface.blit(get_font(25).render("DUNGEON JOURNEY", True, DUNGEON), (rect.left + 16, rect.top + 16))
    surface.blit(get_font(19).render("Three rooms, three moods, one escalating run.", True, MUTED), (rect.left + 16, rect.top + 48))

    rooms = (
        ("01", "RUINED GATE", "Learn the rhythm", ACCENT),
        ("02", "FORGOTTEN ARCHIVE", "Pressure rises", GOLD),
        ("03", "ASHEN THRONE", "Elite showdown", SOLO),
    )
    x = rect.left + 18
    y = rect.top + 92
    for index, (number, title, subtitle, accent) in enumerate(rooms):
        card = pygame.Rect(x, y, 220, 112)
        pygame.draw.rect(surface, (20, 28, 43), card, border_radius=7)
        pygame.draw.rect(surface, accent, card, 2, border_radius=7)
        surface.blit(get_font(22).render(number, True, accent), (card.left + 12, card.top + 11))
        surface.blit(get_font(21).render(title, True, WHITE), (card.left + 12, card.top + 43))
        surface.blit(get_font(18).render(subtitle, True, MUTED), (card.left + 12, card.top + 75))
        x += 244
        if index < len(rooms) - 1:
            pygame.draw.line(surface, DUNGEON, (x - 20, card.centery), (x - 6, card.centery), 3)


def draw_identity(surface, rect):
    """Draw the design pillars currently visible in the prototype."""
    pygame.draw.rect(surface, CARD, rect, border_radius=8)
    pygame.draw.rect(surface, CARD_BORDER, rect, 2, border_radius=8)
    surface.blit(get_font(25).render("COMBAT IDENTITY", True, GOLD), (rect.left + 16, rect.top + 16))
    rows = (
        ("TAP COMBOS", "Only play the hits you press"),
        ("READ & REACT", "Parry, block, dodge, counter"),
        ("POWER BURST", "Fill SAIYAN gauge for x2 damage"),
        ("ROOM ATMOSPHERE", "Layered dungeon mood + torchlight"),
        ("PRESENTATION", "120 FPS + reduced-motion option"),
    )
    for index, (title, detail) in enumerate(rows):
        y = rect.top + 57 + index * 36
        surface.blit(get_font(19).render(title, True, WHITE), (rect.left + 16, y))
        surface.blit(get_font(16).render(detail, True, MUTED), (rect.left + 16, y + 18))


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
