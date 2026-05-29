"""Enemy reaction and punish-window drawing helpers."""

import pygame

from settings import ENEMY_STATE_STAGGER


def draw_enemy_recovery_feedback(surface, enemy):
    """Draw subtle punish-window and recovery readability effects."""
    if enemy.recovery_flash_timer <= 0 and enemy.punish_window_timer <= 0:
        return

    if enemy.punish_window_timer > 0:
        outline_rect = enemy.rect.inflate(10, 10)
        pulse = int(enemy.punish_window_timer * 14) % 2 == 0
        alpha = 55 if pulse else 32
        punish_surface = pygame.Surface((outline_rect.width, outline_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            punish_surface,
            (*enemy.punish_outline_color, alpha),
            punish_surface.get_rect(),
            border_radius=8,
        )
        surface.blit(punish_surface, outline_rect.topleft)
        pygame.draw.rect(surface, enemy.punish_outline_color, outline_rect, 2, border_radius=8)

    if enemy.recovery_flash_timer > 0:
        flash_alpha = 42 if enemy.state == ENEMY_STATE_STAGGER else 28
        flash_surface = pygame.Surface((enemy.rect.width, enemy.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            flash_surface,
            (*enemy.recovery_tint_color, flash_alpha),
            flash_surface.get_rect(),
            border_radius=6,
        )
        surface.blit(flash_surface, enemy.rect.topleft)


def draw_enemy_stagger_feedback(surface, enemy):
    """Draw stronger stagger emphasis while the enemy is clearly vulnerable."""
    if enemy.stagger_emphasis_timer <= 0:
        return

    pulse = int(enemy.stagger_emphasis_timer * 16) % 2 == 0
    radius = 16 if pulse else 13
    center = (enemy.rect.centerx, enemy.rect.top - 10)
    alpha = 95 if pulse else 65

    stagger_surface = pygame.Surface((44, 44), pygame.SRCALPHA)
    pygame.draw.circle(
        stagger_surface,
        (*enemy.stagger_emphasis_color, alpha),
        (22, 22),
        radius,
        3,
    )
    pygame.draw.circle(
        stagger_surface,
        (*enemy.stagger_emphasis_color, alpha // 2),
        (22, 22),
        5,
    )
    surface.blit(stagger_surface, (center[0] - 22, center[1] - 22))


def get_enemy_reaction_offset(enemy):
    """Return a small temporary recoil offset for hit readability."""
    if enemy.reaction_recoil_timer <= 0 or enemy.reaction_recoil_offset <= 0:
        return 0

    return -enemy.reaction_recoil_offset if enemy.knockback_velocity_x >= 0 else enemy.reaction_recoil_offset
