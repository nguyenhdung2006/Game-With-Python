"""Attack and telegraph drawing helpers."""

import pygame


def draw_attack_rectangle(surface, hitbox, color, combo_step, is_counter=False):
    """Draw a layered slash placeholder for the active player hitbox."""
    if hitbox is None:
        return

    alpha = 150 if is_counter else 80 + combo_step * 20
    attack_surface = pygame.Surface((hitbox.width, hitbox.height), pygame.SRCALPHA)
    attack_surface.fill((*color, alpha // 2))
    inner_rect = attack_surface.get_rect().inflate(-12, -12)
    pygame.draw.rect(attack_surface, (*color, alpha), inner_rect, border_radius=4)
    surface.blit(attack_surface, hitbox.topleft)
    pygame.draw.rect(surface, color, hitbox, 5 if is_counter else 2 + combo_step)

    if is_counter:
        glow_rect = hitbox.inflate(18, 18)
        glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*color, 70), glow_surface.get_rect(), border_radius=10)
        surface.blit(glow_surface, glow_rect.topleft)
        pygame.draw.line(surface, color, (hitbox.left + 8, hitbox.top + 8), (hitbox.right - 8, hitbox.bottom - 8), 10)
        pygame.draw.line(surface, (255, 255, 255), (hitbox.left + 8, hitbox.bottom - 8), (hitbox.right - 8, hitbox.top + 8), 6)
        pygame.draw.line(surface, color, (hitbox.left + 14, hitbox.centery), (hitbox.right - 14, hitbox.centery), 5)
        return

    # Different slash angles make each combo hit read as a separate strike.
    if combo_step == 1:
        start_pos = (hitbox.left + 8, hitbox.centery)
        end_pos = (hitbox.right - 8, hitbox.centery)
    elif combo_step == 2:
        start_pos = (hitbox.left + 6, hitbox.bottom - 6)
        end_pos = (hitbox.right - 6, hitbox.top + 6)
    else:
        start_pos = (hitbox.left + 4, hitbox.top + 4)
        end_pos = (hitbox.right - 4, hitbox.bottom - 4)

    glow_width = 6 + combo_step * 2
    pygame.draw.line(surface, color, start_pos, end_pos, glow_width)
    pygame.draw.line(surface, color, start_pos, end_pos, 3 + combo_step)


def draw_enemy_warning(surface, rect, color, pulse_timer=0, pulse_speed=14):
    """Draw a warning box before the enemy attack becomes active."""
    # Clear telegraphs make combat readable and give the player time to react.
    pulse_on = int(pulse_timer * pulse_speed) % 2 == 0
    alpha = 95 if pulse_on else 45
    outline_width = 5 if pulse_on else 3

    warning_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    warning_surface.fill((*color, alpha))
    surface.blit(warning_surface, rect.topleft)
    pygame.draw.rect(surface, color, rect, outline_width)


def draw_enemy_attack_rectangle(surface, rect, color):
    """Draw the enemy's active attack hitbox."""
    attack_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    attack_surface.fill((*color, 105))
    surface.blit(attack_surface, rect.topleft)
    pygame.draw.rect(surface, color, rect, 4)
