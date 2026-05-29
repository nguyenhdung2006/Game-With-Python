import os
import pygame

from entities.enemy import Enemy
from entities.player import Player
from systems.combat import process_enemy_attack, process_player_attack
from systems.effects import CombatImpact
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
    pygame.display.set_caption("Anime Stickman Combat - Phase 7")
    clock = pygame.time.Clock()
    scene_surface = pygame.Surface((WIDTH, HEIGHT))

    player = Player(180, GROUND_Y - PLAYER_HEIGHT)
    enemy = Enemy(990, GROUND_Y - ENEMY_HEIGHT)
    impact = CombatImpact()

    running = True
    while running:
        # Delta time is the number of seconds since the last frame.
        dt = clock.tick(FPS) / 1000
        impact.update(dt)
        hitstop_active = impact.is_hitstop_active()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if hitstop_active:
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                player.jump()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
                player.start_dash()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                player.start_light_attack()

        keys = pygame.key.get_pressed()
        if not hitstop_active:
            player.update(keys, dt)
            enemy.update(player, dt)
            player_hit_result = process_player_attack(player, enemy)
            enemy_hit_result = process_enemy_attack(enemy, player)

            if player_hit_result:
                impact.start_hit_impact(player_hit_result)
            if enemy_hit_result:
                impact.start_hit_impact(enemy_hit_result)

        draw_arena(scene_surface)

        player.draw(scene_surface)
        enemy.draw(scene_surface)

        screen.fill((0, 0, 0))
        camera_offset = impact.get_camera_offset()
        screen.blit(scene_surface, camera_offset)

        draw_health_bar(screen, 60, 55, 420, 28, player.health, player.max_health, HEALTH_PLAYER, "PLAYER")
        draw_health_bar(screen, 800, 55, 420, 28, enemy.health, enemy.max_health, HEALTH_ENEMY, "ENEMY")

        pygame.display.flip()

        # This lets automated checks run one frame without opening a long-lived window.
        if os.environ.get("PYGAME_AUTO_QUIT") == "1" or os.environ.get("PYGAME_PHASE1_TEST") == "1":
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
