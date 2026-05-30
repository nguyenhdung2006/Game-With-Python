"""Player-side recovery, risk, and payoff drawing helpers."""

import pygame


def get_player_draw_rect(player):
    """Return a draw-only body rect with subtle squash/recoil readability."""
    draw_rect = player.rect.copy()
    draw_rect.x += player.get_reaction_offset()

    if player.landing_feedback_timer > 0:
        progress = player.landing_feedback_timer / max(player.hard_landing_feedback_duration, 0.001)
        compress = max(2, int(player.landing_compress_pixels * min(1, progress)))
        draw_rect = draw_rect.inflate(compress // 2, -compress)
        draw_rect.bottom = player.rect.bottom
    elif player.whiff_feedback_timer > 0:
        lean = max(2, int(5 * player.whiff_feedback_timer / max(player.whiff_feedback_duration, 0.001)))
        draw_rect.x += player.facing * lean
        draw_rect.width += lean
    elif player.state_settle_timer > 0:
        settle = int(3 * player.state_settle_timer / max(player.state_settle_duration, 0.001))
        draw_rect.y += settle
        draw_rect.height -= settle

    return draw_rect


def draw_player_recovery_feedback(surface, player, draw_rect):
    """Draw subtle unsafe and recovery cues around the player body."""
    if player.recovery_flash_timer > 0:
        flash_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            flash_surface,
            (*player.recovery_tint_color, 34),
            flash_surface.get_rect(),
            border_radius=6,
        )
        surface.blit(flash_surface, draw_rect.topleft)

    if player.unsafe_timer > 0:
        pulse = int(player.unsafe_timer * 16) % 2 == 0
        outline_rect = draw_rect.inflate(8 if pulse else 5, 8 if pulse else 5)
        alpha = 50 if pulse else 30
        outline_surface = pygame.Surface((outline_rect.width, outline_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            outline_surface,
            (*player.unsafe_outline_color, alpha),
            outline_surface.get_rect(),
            border_radius=8,
        )
        surface.blit(outline_surface, outline_rect.topleft)
        pygame.draw.rect(surface, player.unsafe_outline_color, outline_rect, 2, border_radius=8)

    if player.whiff_feedback_timer > 0:
        _draw_overextended_marker(surface, player, draw_rect)


def draw_player_guard_stress(surface, player, draw_rect):
    """Draw extra pressure readability after blocked hits."""
    if player.guard_stress_timer <= 0:
        return

    pulse = int(player.guard_stress_timer * 18) % 2 == 0
    ring_rect = draw_rect.inflate(18 if pulse else 12, 14 if pulse else 10)
    alpha = 70 if pulse else 45
    ring_surface = pygame.Surface((ring_rect.width, ring_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(
        ring_surface,
        (*player.guard_stress_color, alpha),
        ring_surface.get_rect(),
        width=4,
        border_radius=10,
    )
    surface.blit(ring_surface, ring_rect.topleft)


def draw_player_payoff_feedback(surface, player, draw_rect):
    """Draw short pulses for successful defense and heavy payoff moments."""
    if player.payoff_timer <= 0 and player.attack_hit_payoff_timer <= 0:
        return

    timer = max(player.payoff_timer, player.attack_hit_payoff_timer)
    pulse = int(timer * 20) % 2 == 0
    radius = 18 if pulse else 14
    alpha = 90 if pulse else 55
    center = (draw_rect.centerx, draw_rect.top - 12)

    payoff_surface = pygame.Surface((52, 52), pygame.SRCALPHA)
    pygame.draw.circle(payoff_surface, (*player.payoff_color, alpha), (26, 26), radius, 3)
    pygame.draw.circle(payoff_surface, (*player.payoff_color, alpha // 2), (26, 26), 5)
    surface.blit(payoff_surface, (center[0] - 26, center[1] - 26))


def _draw_overextended_marker(surface, player, draw_rect):
    marker_length = 18
    x = draw_rect.right + 4 if player.facing == 1 else draw_rect.left - marker_length - 4
    y = draw_rect.centery + 6
    start = (x, y)
    end = (x + marker_length * player.facing, y - 8)
    pygame.draw.line(surface, player.unsafe_outline_color, start, end, 3)
