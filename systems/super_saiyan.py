"""Super Saiyan gauge, burst damage, and lightweight aura presentation."""

import pygame

from config.player_config import (
    SUPER_SAIYAN_COLOR,
    SUPER_SAIYAN_DAMAGE_MULTIPLIER,
    SUPER_SAIYAN_DEALT_DAMAGE_GAIN,
    SUPER_SAIYAN_DURATION,
    SUPER_SAIYAN_GLOW_COLOR,
    SUPER_SAIYAN_HURT_DAMAGE_GAIN,
    SUPER_SAIYAN_MAX_ENERGY,
    SUPER_SAIYAN_TRANSFORM_DURATION,
)


def initialize_super_saiyan_state(player):
    """Create a separate transformation resource without replacing skill energy."""
    player.saiyan_energy = 0.0
    player.max_saiyan_energy = SUPER_SAIYAN_MAX_ENERGY
    player.is_super_saiyan = False
    player.super_saiyan_transform_timer = 0.0
    player.super_saiyan_damage_multiplier = SUPER_SAIYAN_DAMAGE_MULTIPLIER


def add_saiyan_energy(player, amount):
    """Charge toward an automatic transformation while the player is in base form."""
    if player.defeated or player.is_super_saiyan or amount <= 0:
        return player.saiyan_energy

    player.saiyan_energy = min(player.max_saiyan_energy, player.saiyan_energy + amount)
    if player.saiyan_energy >= player.max_saiyan_energy:
        start_super_saiyan(player)
    return player.saiyan_energy


def register_outgoing_damage(player, amount):
    """Reward active offense with the larger share of Saiyan gauge gain."""
    return add_saiyan_energy(player, amount * SUPER_SAIYAN_DEALT_DAMAGE_GAIN)


def register_incoming_damage(player, amount):
    """Let a pressured player build toward a comeback without rewarding passivity."""
    return add_saiyan_energy(player, amount * SUPER_SAIYAN_HURT_DAMAGE_GAIN)


def start_super_saiyan(player):
    """Enter the timed form, cleanly interrupt stale actions, and play R22."""
    if player.defeated or player.is_super_saiyan:
        return False

    from entities.player_parts.defense import interrupt_actions_for_damage

    interrupt_actions_for_damage(player)
    player.skill_visual_state = None
    player.skill_visual_timer = 0
    player.is_super_saiyan = True
    player.saiyan_energy = player.max_saiyan_energy
    player.super_saiyan_transform_timer = SUPER_SAIYAN_TRANSFORM_DURATION
    player.invulnerability_timer = max(player.invulnerability_timer, SUPER_SAIYAN_TRANSFORM_DURATION)
    return True


def update_super_saiyan(player, dt):
    """Hold the transformation animation, then drain the finite power burst."""
    if not player.is_super_saiyan:
        return

    if player.super_saiyan_transform_timer > 0:
        player.super_saiyan_transform_timer = max(0.0, player.super_saiyan_transform_timer - dt)
        return

    drain_per_second = player.max_saiyan_energy / SUPER_SAIYAN_DURATION
    player.saiyan_energy = max(0.0, player.saiyan_energy - drain_per_second * dt)
    if player.saiyan_energy == 0:
        player.is_super_saiyan = False


def is_transforming(player):
    """Return True while the automatic R22 power-up should lock combat input."""
    return player.is_super_saiyan and player.super_saiyan_transform_timer > 0


def get_outgoing_damage_multiplier(player):
    """Combine reward progression with the temporary form multiplier."""
    multiplier = getattr(player, "damage_multiplier", 1.0)
    if getattr(player, "is_super_saiyan", False):
        multiplier *= getattr(player, "super_saiyan_damage_multiplier", SUPER_SAIYAN_DAMAGE_MULTIPLIER)
    return multiplier


def draw_super_saiyan_aura(surface, draw_rect, player):
    """Draw a subtle gold aura behind unchanged attack animations during the form."""
    if not getattr(player, "is_super_saiyan", False):
        return

    width = max(86, draw_rect.width + 40)
    height = max(148, draw_rect.height + 42)
    aura = pygame.Surface((width, height), pygame.SRCALPHA)
    center = (width // 2, height // 2 + 6)
    pygame.draw.ellipse(aura, (*SUPER_SAIYAN_COLOR, 32), (12, 16, width - 24, height - 20))
    pygame.draw.ellipse(aura, (*SUPER_SAIYAN_GLOW_COLOR, 54), (24, 28, width - 48, height - 42), 4)
    pygame.draw.polygon(
        aura,
        (*SUPER_SAIYAN_COLOR, 58),
        (
            (center[0], 0),
            (center[0] + 14, 34),
            (width - 8, 16),
            (width - 28, 62),
            (width - 2, height - 30),
            (center[0], height - 4),
            (2, height - 30),
            (28, 62),
            (8, 16),
            (center[0] - 14, 34),
        ),
        3,
    )
    surface.blit(aura, aura.get_rect(midbottom=(draw_rect.centerx, draw_rect.bottom + 10)))
