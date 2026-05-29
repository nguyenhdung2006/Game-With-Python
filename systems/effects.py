"""Visual effect helpers.

Effects live outside entities so future particles, flashes, and trails can be
shared by the player, enemies, bosses, and the battlefield.
"""

import pygame
import random


class CombatImpact:
    """Tracks hitstop and camera shake after successful hits.

    Hitstop briefly pauses gameplay movement without freezing the app window.
    Camera shake offsets the rendered arena for a few frames to sell impact.
    """

    def __init__(self):
        self.hitstop_timer = 0
        self.camera_shake_timer = 0
        self.camera_shake_strength = 0

    def start_hit_impact(self, attack_data):
        """Start hitstop and shake using the current combo hit's feel values."""
        self.hitstop_timer = max(self.hitstop_timer, attack_data["hitstop"])
        self.camera_shake_timer = max(self.camera_shake_timer, attack_data["shake_duration"])
        self.camera_shake_strength = max(self.camera_shake_strength, attack_data["shake_strength"])

    def update(self, dt):
        """Count down impact timers with delta time."""
        if self.hitstop_timer > 0:
            self.hitstop_timer = max(0, self.hitstop_timer - dt)

        if self.camera_shake_timer > 0:
            self.camera_shake_timer = max(0, self.camera_shake_timer - dt)

            if self.camera_shake_timer == 0:
                self.camera_shake_strength = 0

    def is_hitstop_active(self):
        """Return True while player and enemy updates should be paused."""
        return self.hitstop_timer > 0

    def get_camera_offset(self):
        """Return a small random render offset while camera shake is active."""
        if self.camera_shake_timer <= 0 or self.camera_shake_strength <= 0:
            return 0, 0

        strength = self.camera_shake_strength
        return random.randint(-strength, strength), random.randint(-strength, strength)


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
    """Draw a layered slash placeholder for the active combo hitbox."""
    if hitbox is None:
        return

    alpha = 80 + combo_step * 20
    attack_surface = pygame.Surface((hitbox.width, hitbox.height), pygame.SRCALPHA)
    attack_surface.fill((*color, alpha // 2))
    inner_rect = attack_surface.get_rect().inflate(-12, -12)
    pygame.draw.rect(attack_surface, (*color, alpha), inner_rect, border_radius=4)
    surface.blit(attack_surface, hitbox.topleft)
    pygame.draw.rect(surface, color, hitbox, 2 + combo_step)

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


def draw_enemy_warning(surface, rect, color, pulse_timer=0):
    """Draw a warning box before the enemy attack becomes active."""
    # Clear telegraphs make combat readable and give the player time to react.
    pulse_on = int(pulse_timer * 14) % 2 == 0
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


def choose_flash_color(base_color, flash_color, flash_timer):
    """Use a flash color while an entity's hurt flash timer is active."""
    if flash_timer > 0:
        return flash_color

    return base_color


def create_particles_placeholder():
    """Placeholder for future particle systems."""
    return []
