"""Visual effect helpers.

Effects live outside entities so future particles, flashes, and trails can be
shared by the player, enemies, bosses, and the battlefield.
"""

import pygame


def create_afterimage(rect, lifetime):
    """Create one transparent rectangle copy for a dash trail."""
    return {
        "rect": rect.copy(),
        "timer": lifetime,
    }


def update_timed_effects(effects, dt):
    """Count down effect timers and remove expired effects."""
    for effect in effects:
        effect["timer"] -= dt

    return [effect for effect in effects if effect["timer"] > 0]


def draw_rect_afterimages(surface, afterimages, size, lifetime, color):
    """Draw fading rectangle afterimages."""
    width, height = size

    for afterimage in afterimages:
        fade_amount = afterimage["timer"] / lifetime
        alpha = int(120 * fade_amount)

        trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        trail_surface.fill((*color, alpha))
        surface.blit(trail_surface, afterimage["rect"].topleft)


def draw_attack_rectangle(surface, hitbox, color, combo_step):
    """Draw the active sword hitbox as a transparent rectangle."""
    if hitbox is None:
        return

    alpha = 80 + combo_step * 20
    attack_surface = pygame.Surface((hitbox.width, hitbox.height), pygame.SRCALPHA)
    attack_surface.fill((*color, alpha))
    surface.blit(attack_surface, hitbox.topleft)
    pygame.draw.rect(surface, color, hitbox, 2 + combo_step)

    # A diagonal line makes each combo step feel more like a slash than a box.
    if combo_step == 1:
        start_pos = hitbox.midleft
        end_pos = hitbox.midright
    elif combo_step == 2:
        start_pos = hitbox.bottomleft
        end_pos = hitbox.topright
    else:
        start_pos = hitbox.topleft
        end_pos = hitbox.bottomright

    pygame.draw.line(surface, color, start_pos, end_pos, 3 + combo_step)


def choose_flash_color(base_color, flash_color, flash_timer):
    """Use a flash color while an entity's hurt flash timer is active."""
    if flash_timer > 0:
        return flash_color

    return base_color


def create_particles_placeholder():
    """Placeholder for future particle systems."""
    return []
