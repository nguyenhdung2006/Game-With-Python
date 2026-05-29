"""Defense-related visual helpers."""

import pygame


def draw_block_guard(surface, player_rect, direction, is_blocking, flash_timer, base_color, flash_color):
    """Draw a simple shield shape in front of the player while guarding."""
    if not is_blocking and flash_timer <= 0:
        return

    guard_width = 24
    guard_height = max(72, player_rect.height - 18)
    x = player_rect.right + 4 if direction == 1 else player_rect.left - guard_width - 4
    y = player_rect.centery - guard_height // 2
    guard_rect = pygame.Rect(x, y, guard_width, guard_height)

    color = flash_color if flash_timer > 0 else base_color
    alpha = 130 if flash_timer > 0 else 75

    guard_surface = pygame.Surface((guard_rect.width, guard_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(guard_surface, (*color, alpha), guard_surface.get_rect(), border_radius=8)
    surface.blit(guard_surface, guard_rect.topleft)
    pygame.draw.rect(surface, color, guard_rect, 3, border_radius=8)

    if flash_timer > 0:
        spark_y = guard_rect.centery
        spark_left = guard_rect.left if direction == 1 else guard_rect.right - 1
        pygame.draw.line(surface, flash_color, (spark_left, spark_y - 12), (spark_left + direction * 16, spark_y), 3)
        pygame.draw.line(surface, flash_color, (spark_left, spark_y + 12), (spark_left + direction * 16, spark_y), 3)


def draw_parry_guard(surface, player_rect, direction, is_parrying, flash_timer, base_color, flash_color):
    """Draw a brighter, shorter guard shape during the parry timing window."""
    if not is_parrying and flash_timer <= 0:
        return

    guard_width = 28
    guard_height = max(84, player_rect.height - 8)
    x = player_rect.right + 2 if direction == 1 else player_rect.left - guard_width - 2
    y = player_rect.centery - guard_height // 2
    guard_rect = pygame.Rect(x, y, guard_width, guard_height)

    color = flash_color if flash_timer > 0 else base_color
    alpha = 165 if is_parrying else 110

    parry_surface = pygame.Surface((guard_rect.width, guard_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(parry_surface, (*color, alpha), parry_surface.get_rect(), border_radius=10)
    surface.blit(parry_surface, guard_rect.topleft)
    pygame.draw.rect(surface, color, guard_rect, 3, border_radius=10)

    burst_center_x = guard_rect.centerx + direction * 6
    burst_center = (burst_center_x, guard_rect.centery)
    pygame.draw.circle(surface, color, burst_center, 12, 3)
    pygame.draw.line(surface, color, (burst_center[0], burst_center[1] - 18), (burst_center[0], burst_center[1] + 18), 2)
    pygame.draw.line(surface, color, (burst_center[0] - 18, burst_center[1]), (burst_center[0] + 18, burst_center[1]), 2)


def draw_dodge_overlay(surface, rect, color):
    """Draw a light tinted overlay so dodge i-frames read clearly."""
    dodge_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(dodge_surface, (*color, 130), dodge_surface.get_rect(), border_radius=6)
    surface.blit(dodge_surface, rect.topleft)


def choose_flash_color(base_color, flash_color, flash_timer):
    """Use a flash color while an entity's hurt flash timer is active."""
    if flash_timer > 0:
        return flash_color

    return base_color


def create_particles_placeholder():
    """Placeholder for future particle systems."""
    return []
