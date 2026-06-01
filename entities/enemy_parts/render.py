"""Base enemy drawing helpers."""

import pygame

from settings import ENEMY_STATE_ATTACK, ENEMY_STATE_STAGGER, ENEMY_STATE_TELEGRAPH, WHITE
from systems.combat import create_enemy_attack_hitbox
from systems.effects import choose_flash_color, draw_enemy_attack_rectangle, draw_enemy_warning
from systems.pressure_indicator import draw_active_aggressor_indicator, draw_pressure_indicator
from systems.reaction_feedback import (
    draw_enemy_recovery_feedback,
    draw_enemy_stagger_feedback,
    get_enemy_reaction_offset,
)
from systems.sprite_loader import draw_entity_sprite
from entities.enemy_parts.render_state import get_enemy_visual_state


def draw(enemy, surface):
    """Draw the enemy and its current telegraph or attack effect."""
    draw_rect = enemy.rect.copy()
    draw_rect.x += get_enemy_reaction_offset(enemy)

    if enemy.defeated:
        color = enemy.defeated_color
    elif enemy.state == ENEMY_STATE_STAGGER:
        color = enemy.stagger_emphasis_color
    else:
        color = choose_flash_color(enemy.body_color, enemy.hurt_color, enemy.hurt_flash_timer)

    visual_state = get_enemy_visual_state(enemy)
    dungeon_sprite_renderer = getattr(enemy, "dungeon_sprite_renderer", None)
    sprite_drawn = False
    if dungeon_sprite_renderer is not None:
        sprite_drawn = dungeon_sprite_renderer.draw(surface, enemy, draw_rect, visual_state)
    if not sprite_drawn:
        sprite_drawn = draw_entity_sprite(surface, enemy, draw_rect, visual_state)

    if enemy.hurt_flash_timer > 0 and not enemy.defeated:
        recoil_rect = draw_rect.copy()
        recoil_rect.x -= 6 if enemy.knockback_velocity_x > 0 else -6
        pygame.draw.rect(surface, enemy.recoil_outline_color, recoil_rect, 3)

    if not sprite_drawn:
        pygame.draw.rect(surface, color, draw_rect)
        pygame.draw.rect(surface, WHITE, draw_rect, 3)

    draw_enemy_recovery_feedback(surface, enemy)
    draw_active_aggressor_indicator(surface, enemy)
    draw_pressure_indicator(surface, enemy)

    if enemy.state == ENEMY_STATE_STAGGER:
        spark_center = (draw_rect.centerx, draw_rect.top - 12)
        pygame.draw.circle(surface, WHITE, spark_center, 10, 2)
        pygame.draw.line(surface, WHITE, (spark_center[0] - 14, spark_center[1]), (spark_center[0] + 14, spark_center[1]), 2)
        pygame.draw.line(surface, WHITE, (spark_center[0], spark_center[1] - 14), (spark_center[0], spark_center[1] + 14), 2)
        draw_enemy_stagger_feedback(surface, enemy)

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
