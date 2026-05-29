import os
import pygame


# Window size for the game.
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Basic colors used by the arena and characters.
SKY_TOP = (12, 14, 26)
SKY_BOTTOM = (42, 36, 48)
GROUND = (70, 62, 58)
GROUND_DARK = (34, 31, 32)
CRACK = (18, 18, 22)
PLAYER_COLOR = (76, 180, 255)
ENEMY_COLOR = (225, 70, 74)
HEALTH_BG = (35, 35, 40)
HEALTH_PLAYER = (60, 220, 120)
HEALTH_ENEMY = (230, 60, 70)
WHITE = (235, 235, 240)


class Player:
    """A very simple player object for Phase 1."""

    def __init__(self, x, y):
        self.width = 54
        self.height = 118
        self.speed = 360
        self.health = 100
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def handle_input(self, keys, dt):
        """Move left and right with A/D using delta time."""
        if keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_d]:
            self.rect.x += self.speed * dt

        # Keep the player inside the visible arena.
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)

    def draw(self, surface):
        """Draw the placeholder rectangle player."""
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)


def draw_vertical_gradient(surface, top_color, bottom_color):
    """Draw a simple dramatic sky gradient with pygame lines."""
    for y in range(SCREEN_HEIGHT):
        blend = y / SCREEN_HEIGHT
        r = int(top_color[0] * (1 - blend) + bottom_color[0] * blend)
        g = int(top_color[1] * (1 - blend) + bottom_color[1] * blend)
        b = int(top_color[2] * (1 - blend) + bottom_color[2] * blend)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))


def draw_background_ruins(surface):
    """Draw distant battlefield rocks and broken pillars using shapes only."""
    # Far mountain/rock silhouettes.
    pygame.draw.polygon(surface, (24, 24, 33), [(0, 520), (150, 360), (330, 520)])
    pygame.draw.polygon(surface, (30, 28, 37), [(260, 520), (470, 320), (690, 520)])
    pygame.draw.polygon(surface, (20, 23, 31), [(820, 520), (1040, 335), (1280, 520)])

    # Broken pillars in the background.
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

    # Rubble piles.
    pygame.draw.circle(surface, (43, 41, 47), (260, 548), 36)
    pygame.draw.circle(surface, (35, 34, 39), (310, 552), 24)
    pygame.draw.circle(surface, (52, 48, 52), (1125, 552), 42)
    pygame.draw.circle(surface, (39, 37, 43), (1180, 557), 28)


def draw_ground(surface):
    """Draw the arena platform and cracked floor."""
    ground_rect = pygame.Rect(0, 540, SCREEN_WIDTH, 180)
    pygame.draw.rect(surface, GROUND, ground_rect)
    pygame.draw.rect(surface, GROUND_DARK, (0, 540, SCREEN_WIDTH, 18))

    # Uneven top edge shadow to make the platform feel less flat.
    pygame.draw.polygon(
        surface,
        (49, 43, 43),
        [(0, 558), (130, 548), (285, 560), (440, 550), (630, 564),
         (790, 552), (980, 561), (1130, 550), (1280, 558), (1280, 590), (0, 590)],
    )

    # Cracks on the battlefield floor.
    cracks = [
        [(110, 610), (170, 590), (220, 605), (285, 585)],
        [(390, 655), (430, 615), (500, 625), (555, 600)],
        [(720, 600), (770, 630), (835, 615), (900, 650)],
        [(1010, 590), (1060, 612), (1105, 604), (1170, 635)],
        [(610, 690), (650, 665), (700, 675)],
    ]

    for crack in cracks:
        pygame.draw.lines(surface, CRACK, False, crack, 4)

    # Small broken stone slabs.
    pygame.draw.polygon(surface, (86, 77, 72), [(80, 675), (180, 660), (225, 700), (115, 710)])
    pygame.draw.polygon(surface, (62, 56, 55), [(960, 665), (1080, 646), (1160, 690), (1005, 710)])


def draw_health_bar(surface, x, y, width, height, health, fill_color, label):
    """Draw a simple health bar with a label."""
    health = max(0, min(health, 100))
    fill_width = int(width * (health / 100))

    pygame.draw.rect(surface, HEALTH_BG, (x, y, width, height))
    pygame.draw.rect(surface, fill_color, (x, y, fill_width, height))
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 3)

    font = pygame.font.Font(None, 32)
    text = font.render(label, True, WHITE)
    surface.blit(text, (x, y - 32))


def draw_arena(surface):
    """Draw the complete Phase 1 battlefield scene."""
    draw_vertical_gradient(surface, SKY_TOP, SKY_BOTTOM)

    # Red moon/sun shape for drama.
    pygame.draw.circle(surface, (98, 34, 44), (650, 150), 70)
    pygame.draw.circle(surface, (42, 36, 48), (680, 130), 68)

    draw_background_ruins(surface)
    draw_ground(surface)


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Anime Stickman Combat - Phase 1")
    clock = pygame.time.Clock()

    player = Player(180, 540 - 118)
    enemy = pygame.Rect(990, 540 - 118, 54, 118)
    enemy_health = 100

    running = True
    while running:
        # Delta time is the number of seconds since the last frame.
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys, dt)

        draw_arena(screen)

        player.draw(screen)
        pygame.draw.rect(screen, ENEMY_COLOR, enemy)
        pygame.draw.rect(screen, WHITE, enemy, 3)

        draw_health_bar(screen, 60, 55, 420, 28, player.health, HEALTH_PLAYER, "PLAYER")
        draw_health_bar(screen, 800, 55, 420, 28, enemy_health, HEALTH_ENEMY, "ENEMY")

        pygame.display.flip()

        # This lets automated checks run one frame without opening a long-lived window.
        if os.environ.get("PYGAME_PHASE1_TEST") == "1":
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
