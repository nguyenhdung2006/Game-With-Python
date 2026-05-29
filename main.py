import os
import pygame

from entities.enemy import Enemy
from entities.player import Player
from settings import (
    ENEMY_HEIGHT,
    FPS,
    GROUND_Y,
    HEALTH_ENEMY,
    HEALTH_PLAYER,
    HEIGHT,
    PLAYER_HEIGHT,
    WIDTH,
)
from ui.health_bar import draw_health_bar
from world.battlefield import draw_arena


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Anime Stickman Combat - Phase 3")
    clock = pygame.time.Clock()

    player = Player(180, GROUND_Y - PLAYER_HEIGHT)
    enemy = Enemy(990, GROUND_Y - ENEMY_HEIGHT)

    running = True
    while running:
        # Delta time is the number of seconds since the last frame.
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                player.jump()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
                player.start_dash()

        keys = pygame.key.get_pressed()
        player.update(keys, dt)
        enemy.update(dt)

        draw_arena(screen)

        player.draw(screen)
        enemy.draw(screen)

        draw_health_bar(screen, 60, 55, 420, 28, player.health, player.max_health, HEALTH_PLAYER, "PLAYER")
        draw_health_bar(screen, 800, 55, 420, 28, enemy.health, enemy.max_health, HEALTH_ENEMY, "ENEMY")

        pygame.display.flip()

        # This lets automated checks run one frame without opening a long-lived window.
        if os.environ.get("PYGAME_AUTO_QUIT") == "1" or os.environ.get("PYGAME_PHASE1_TEST") == "1":
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
