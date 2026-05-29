"""Base enemy drawing helpers."""

import pygame

from settings import ENEMY_STATE_ATTACK, ENEMY_STATE_STAGGER, ENEMY_STATE_TELEGRAPH, WHITE
from systems.combat import create_enemy_attack_hitbox
from systems.effects import choose_flash_color, draw_enemy_attack_rectangle, draw_enemy_warning


def draw(enemy, surface):
    """Draw the enemy and its current telegraph or attack effect."""
    if enemy.defeated:
        color = enemy.defeated_color
    elif enemy.state == ENEMY_STATE_STAGGER:
        color = (255, 245, 185)
    else:
        color = choose_flash_color(enemy.body_color, enemy.hurt_color, enemy.hurt_flash_timer)

    if enemy.hurt_flash_timer > 0 and not enemy.defeated:
        recoil_rect = enemy.rect.copy()
        recoil_rect.x -= 6 if enemy.knockback_velocity_x > 0 else -6
        pygame.draw.rect(surface, enemy.recoil_outline_color, recoil_rect, 3)

    pygame.draw.rect(surface, color, enemy.rect)
    pygame.draw.rect(surface, WHITE, enemy.rect, 3)

    if enemy.state == ENEMY_STATE_STAGGER:
        spark_center = (enemy.rect.centerx, enemy.rect.top - 12)
        pygame.draw.circle(surface, WHITE, spark_center, 10, 2)
        pygame.draw.line(surface, WHITE, (spark_center[0] - 14, spark_center[1]), (spark_center[0] + 14, spark_center[1]), 2)
        pygame.draw.line(surface, WHITE, (spark_center[0], spark_center[1] - 14), (spark_center[0], spark_center[1] + 14), 2)

    attack_rect = create_enemy_attack_hitbox(enemy)

    if enemy.state == ENEMY_STATE_TELEGRAPH:
        draw_enemy_warning(
            surface,
            attack_rect,
            enemy.telegraph_color,
            enemy.telegraph_timer,
            enemy.telegraph_pulse_speed,
        )
    elif enemy.state == ENEMY_STATE_ATTACK:
        draw_enemy_attack_rectangle(surface, attack_rect, enemy.attack_color)
