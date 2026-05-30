"""Dungeon run status and clear-summary UI helpers."""

import pygame

from managers.room_state import ROOM_BOSS_ENCOUNTER, ROOM_DUNGEON_CLEAR, ROOM_ENCOUNTER
from settings import HEIGHT, WHITE, WIDTH


PANEL = (18, 22, 34)
PANEL_BORDER = (88, 114, 146)
ACCENT = (130, 220, 255)
CLEAR_COLOR = (255, 240, 180)
MUTED = (190, 198, 212)


def draw_dungeon_hud(surface, room_manager, reward_manager, player, skill_manager=None):
    """Draw compact run status during Dungeon Mode."""
    lines = [
        f"Room: {room_manager.room_number()} / {room_manager.total_rooms()}",
        f"Type: {format_room_type(room_manager.current_room_type())}",
        f"Rewards: {reward_manager.chosen_reward_count()}",
    ]
    lines.extend(get_stat_lines(player))
    if skill_manager is not None:
        lines.extend(get_skill_lines(skill_manager))
    draw_text_panel(surface, lines, 24, 98, 310)

    reward_names = reward_manager.chosen_reward_display_names()
    if reward_names:
        reward_lines = ["Rewards:"]
        reward_lines.extend(f"- {name}" for name in reward_names[-3:])
        draw_text_panel(surface, reward_lines, WIDTH - 292, 176, 268)


def draw_dungeon_clear_summary(surface, room_manager, reward_manager, player):
    """Draw final dungeon clear summary with run rewards and stat modifiers."""
    title_font = pygame.font.Font(None, 58)
    text_font = pygame.font.Font(None, 30)
    small_font = pygame.font.Font(None, 26)

    panel_rect = pygame.Rect(WIDTH // 2 - 330, 150, 660, 390)
    pygame.draw.rect(surface, PANEL, panel_rect, border_radius=8)
    pygame.draw.rect(surface, CLEAR_COLOR, panel_rect, 2, border_radius=8)

    title = title_font.render("Dungeon Cleared", True, CLEAR_COLOR)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, panel_rect.top + 50)))

    y = panel_rect.top + 104
    lines = [
        f"Rooms Cleared: {room_manager.cleared_room_count()} / {room_manager.total_rooms()}",
        f"Rewards Chosen: {reward_manager.chosen_reward_count()}",
    ]
    for line in lines:
        rendered = text_font.render(line, True, WHITE)
        surface.blit(rendered, (panel_rect.left + 44, y))
        y += 34

    reward_names = reward_manager.chosen_reward_display_names()
    reward_header = text_font.render("Selected Rewards:", True, ACCENT)
    surface.blit(reward_header, (panel_rect.left + 44, y + 8))
    y += 48

    if reward_names:
        for reward_name in reward_names:
            rendered = small_font.render(f"- {reward_name}", True, MUTED)
            surface.blit(rendered, (panel_rect.left + 64, y))
            y += 28
    else:
        rendered = small_font.render("- None", True, MUTED)
        surface.blit(rendered, (panel_rect.left + 64, y))
        y += 28

    stat_header = text_font.render("Final Modifiers:", True, ACCENT)
    surface.blit(stat_header, (panel_rect.left + 360, panel_rect.top + 104))
    stat_y = panel_rect.top + 148
    for stat_line in get_stat_lines(player):
        rendered = small_font.render(stat_line, True, MUTED)
        surface.blit(rendered, (panel_rect.left + 380, stat_y))
        stat_y += 30

    prompt = small_font.render("Esc to return to menu", True, MUTED)
    surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, panel_rect.bottom - 36)))


def get_stat_lines(player):
    """Return safe mechanical stat modifier display lines."""
    return [
        f"Damage: x{getattr(player, 'damage_multiplier', 1.0):.2f}",
        f"Dash CD: x{getattr(player, 'dash_cooldown_multiplier', 1.0):.2f}",
        f"Max HP Bonus: +{getattr(player, 'max_health_bonus', 0)}",
    ]


def get_skill_lines(skill_manager):
    """Return compact mechanical skill slot status lines."""
    lines = ["Skills:"]
    for status in skill_manager.get_slot_statuses():
        lines.append(f"Skill {status['slot']}: {status['status']}")
    return lines


def format_room_type(room_type):
    """Return readable labels for dungeon HUD room types."""
    if room_type == ROOM_ENCOUNTER:
        return "ENCOUNTER"
    if room_type == ROOM_BOSS_ENCOUNTER:
        return "BOSS"
    if room_type == ROOM_DUNGEON_CLEAR:
        return "DUNGEON_CLEAR"
    return room_type


def draw_text_panel(surface, lines, x, y, width):
    """Draw a simple text panel sized to its lines."""
    font = pygame.font.Font(None, 25)
    line_height = 24
    panel_height = 18 + line_height * len(lines)
    panel_rect = pygame.Rect(x, y, width, panel_height)

    pygame.draw.rect(surface, PANEL, panel_rect, border_radius=6)
    pygame.draw.rect(surface, PANEL_BORDER, panel_rect, 2, border_radius=6)

    text_y = y + 10
    for index, line in enumerate(lines):
        color = ACCENT if index == 0 else WHITE
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x + 14, text_y))
        text_y += line_height
