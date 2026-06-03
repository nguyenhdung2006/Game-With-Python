"""Player drawing helpers."""

import pygame

from settings import (
    PLAYER_COLOR,
    PLAYER_DEFEATED_COLOR,
    PLAYER_HURT_COLOR,
    PLAYER_INVULNERABLE_COLOR,
    WHITE,
)
from systems.effects import (
    choose_flash_color,
    draw_attack_rectangle,
    draw_block_guard,
    draw_counter_ready_glow,
    draw_dodge_overlay,
    draw_parry_guard,
    draw_rect_afterimages,
)
from systems.player_feedback import (
    draw_player_guard_stress,
    draw_player_payoff_feedback,
    draw_player_recovery_feedback,
    get_player_draw_rect,
)
from systems.sprite_loader import draw_entity_sprite
from systems.super_saiyan import draw_super_saiyan_aura
from entities.player_parts.render_state import get_player_visual_state


def draw(player, surface):
    """Draw the dash trail, combat effects, and placeholder rectangle player."""
    draw_rect_afterimages(
        surface,
        player.dash_trail,
        (player.width, player.height),
        player.trail_lifetime,
        PLAYER_COLOR,
    )
    draw_counter_ready_glow(surface, player.rect, player.counter_window_timer, player.counter_ready_color)
    draw_attack_rectangle(
        surface,
        player.get_attack_hitbox(),
        player.attack_color,
        player.combo_step,
        player.is_counter_attacking,
    )
    draw_block_guard(
        surface,
        player.rect,
        player.block_direction,
        player.is_blocking,
        player.block_flash_timer,
        player.block_color,
        player.block_flash_color,
    )
    draw_parry_guard(
        surface,
        player.rect,
        player.block_direction,
        player.is_parrying,
        player.successful_parry_timer,
        player.parry_color,
        player.parry_flash_color,
    )
    draw_rect = get_player_draw_rect(player)
    draw_super_saiyan_aura(surface, draw_rect, player)

    visual_state = get_player_visual_state(player)
    sprite_renderer = getattr(player, "player_sprite_renderer", None)
    sprite_drawn = (
        sprite_renderer.draw(surface, player, draw_rect, visual_state)
        if sprite_renderer is not None
        else None
    )
    if sprite_drawn is None:
        sprite_drawn = draw_entity_sprite(surface, player, draw_rect, visual_state)
    if not sprite_drawn:
        color = PLAYER_COLOR
        if player.defeated:
            color = PLAYER_DEFEATED_COLOR
        elif player.invulnerability_timer > 0:
            # Blinking during i-frames makes temporary safety visible to the player.
            blink_on = int(player.invulnerability_timer * 20) % 2 == 0
            color = PLAYER_INVULNERABLE_COLOR if blink_on else PLAYER_COLOR

        color = choose_flash_color(color, PLAYER_HURT_COLOR, player.hurt_flash_timer)
        pygame.draw.rect(surface, color, draw_rect)
        pygame.draw.rect(surface, WHITE, draw_rect, 3)

    if player.is_dodging or player.dodge_invulnerability_timer > 0:
        draw_dodge_overlay(surface, draw_rect, player.dodge_color)

    draw_player_recovery_feedback(surface, player, draw_rect)
    draw_player_guard_stress(surface, player, draw_rect)
    draw_player_payoff_feedback(surface, player, draw_rect)
