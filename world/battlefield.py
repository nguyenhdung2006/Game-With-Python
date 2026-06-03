"""Battlefield arena drawing.

The world package owns environment visuals so main.py does not become a large
pile of drawing code as the game grows.
"""

import pygame

from settings import (
    CRACK,
    GROUND,
    GROUND_DARK,
    GROUND_Y,
    HEIGHT,
    SKY_BOTTOM,
    SKY_TOP,
    WIDTH,
)

_ARENA_BACKGROUND = None


def draw_vertical_gradient(surface, top_color, bottom_color):
    """Draw a simple dramatic sky gradient with pygame lines."""
    for y in range(HEIGHT):
        blend = y / HEIGHT
        r = int(top_color[0] * (1 - blend) + bottom_color[0] * blend)
        g = int(top_color[1] * (1 - blend) + bottom_color[1] * blend)
        b = int(top_color[2] * (1 - blend) + bottom_color[2] * blend)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_background_ruins(surface):
    """Draw distant battlefield rocks and broken pillars using shapes only."""
    pygame.draw.polygon(surface, (24, 24, 33), [(0, 520), (150, 360), (330, 520)])
    pygame.draw.polygon(surface, (30, 28, 37), [(260, 520), (470, 320), (690, 520)])
    pygame.draw.polygon(surface, (20, 23, 31), [(820, 520), (1040, 335), (1280, 520)])

    pillar_color = (49, 46, 52)
    pillar_shadow = (30, 29, 36)

    pygame.draw.rect(surface, pillar_shadow, (105, 290, 58, 250))
    pygame.draw.polygon(surface, pillar_color, [(95, 290), (172, 270), (162, 540), (105, 540)])
    pygame.draw.line(surface, (24, 24, 30), (104, 350), (162, 338), 5)
    pygame.draw.line(surface, (24, 24, 30), (103, 430), (160, 418), 5)

    pygame.draw.rect(surface, pillar_shadow, (965, 230, 75, 310))
    pygame.draw.polygon(surface, pillar_color, [(956, 235), (1048, 215), (1037, 540), (965, 540)])
    pygame.draw.line(surface, (24, 24, 30), (965, 320), (1042, 304), 6)
    pygame.draw.line(surface, (24, 24, 30), (962, 435), (1038, 420), 6)

    pygame.draw.circle(surface, (43, 41, 47), (260, 548), 36)
    pygame.draw.circle(surface, (35, 34, 39), (310, 552), 24)
    pygame.draw.circle(surface, (52, 48, 52), (1125, 552), 42)
    pygame.draw.circle(surface, (39, 37, 43), (1180, 557), 28)


def draw_ground(surface):
    """Draw the arena platform and cracked floor."""
    ground_rect = pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y)
    pygame.draw.rect(surface, GROUND, ground_rect)
    pygame.draw.rect(surface, GROUND_DARK, (0, GROUND_Y, WIDTH, 18))

    pygame.draw.polygon(
        surface,
        (49, 43, 43),
        [
            (0, 558),
            (130, 548),
            (285, 560),
            (440, 550),
            (630, 564),
            (790, 552),
            (980, 561),
            (1130, 550),
            (1280, 558),
            (1280, 590),
            (0, 590),
        ],
    )

    cracks = [
        [(110, 610), (170, 590), (220, 605), (285, 585)],
        [(390, 655), (430, 615), (500, 625), (555, 600)],
        [(720, 600), (770, 630), (835, 615), (900, 650)],
        [(1010, 590), (1060, 612), (1105, 604), (1170, 635)],
        [(610, 690), (650, 665), (700, 675)],
    ]

    for crack in cracks:
        pygame.draw.lines(surface, CRACK, False, crack, 4)

    pygame.draw.polygon(surface, (86, 77, 72), [(80, 675), (180, 660), (225, 700), (115, 710)])
    pygame.draw.polygon(surface, (62, 56, 55), [(960, 665), (1080, 646), (1160, 690), (1005, 710)])


def draw_arena(surface):
    """Draw the complete battlefield scene."""
    surface.blit(get_arena_background(), (0, 0))


def get_arena_background():
    """Build the fixed battlefield once, then reuse it at high frame rates."""
    global _ARENA_BACKGROUND
    if _ARENA_BACKGROUND is not None:
        return _ARENA_BACKGROUND

    background = pygame.Surface((WIDTH, HEIGHT))
    draw_vertical_gradient(background, SKY_TOP, SKY_BOTTOM)

    pygame.draw.circle(background, (98, 34, 44), (650, 150), 70)
    pygame.draw.circle(background, (42, 36, 48), (680, 130), 68)

    draw_background_ruins(background)
    draw_ground(background)
    _ARENA_BACKGROUND = background
    return _ARENA_BACKGROUND
