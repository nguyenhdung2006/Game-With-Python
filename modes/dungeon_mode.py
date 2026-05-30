"""Dungeon / Wave mode wrapper around the existing combat encounter."""

import pygame

from entities.player import Player
from managers.encounter_manager import EncounterManager
from managers.room_manager import RoomManager
from managers.room_state import ROOM_BOSS_PLACEHOLDER, ROOM_ENCOUNTER
from settings import GROUND_Y, HEALTH_PLAYER, PLAYER_HEIGHT
from systems.combat import process_enemy_attacks, process_player_attacks
from systems.effects import CombatImpact
from systems.reward_manager import RewardManager
from systems.render_layers import draw_combat_scene
from ui.dungeon_hud import draw_dungeon_clear_summary, draw_dungeon_hud
from ui.health_bar import draw_health_bar
from ui.reward_select import draw_reward_select
from ui.room_banner import (
    draw_boss_placeholder,
    draw_room_cleared,
)
from world.battlefield import draw_arena


class DungeonMode:
    """Own the current wave-combat loop so main.py can route between screens."""

    def __init__(self):
        self.player = Player(180, GROUND_Y - PLAYER_HEIGHT)
        self.room_manager = RoomManager()
        self.encounter_manager = None
        self.impact = CombatImpact()
        self.reward_manager = RewardManager()
        self.enter_current_room()

    def handle_event(self, event):
        """Handle room progression and combat inputs for dungeon mode."""
        if event.type != pygame.KEYDOWN:
            return

        if self.room_manager.is_reward_active():
            self.handle_reward_input(event.key)
            return

        if event.key == pygame.K_RETURN:
            self.handle_continue()
            return

        if not self.is_active_encounter_room() or self.impact.is_hitstop_active():
            return

        if event.key == pygame.K_w:
            self.player.jump()
        elif event.key == pygame.K_LSHIFT:
            self.player.start_dash()
        elif event.key == pygame.K_k:
            self.player.start_guard()
        elif event.key == pygame.K_l:
            dodge_result = self.player.start_dodge()
            if dodge_result:
                self.impact.start_hit_impact(dodge_result)
        elif event.key == pygame.K_j:
            self.player.start_light_attack()

    def update(self, keys, dt):
        """Update the active dungeon room."""
        self.impact.update(dt)
        if not self.is_active_encounter_room():
            return

        if self.impact.is_hitstop_active():
            return

        self.player.update(keys, dt)
        self.encounter_manager.update(self.player, dt)
        active_enemies = self.encounter_manager.get_enemies()

        player_hit_result = process_player_attacks(self.player, active_enemies)
        enemy_hit_results = process_enemy_attacks(active_enemies, self.player)

        if player_hit_result:
            self.impact.start_hit_impact(player_hit_result)
        for enemy_hit_result in enemy_hit_results:
            self.impact.start_hit_impact(enemy_hit_result)

        if self.encounter_manager.encounter_cleared:
            self.start_reward_selection()

    def draw(self, screen, scene_surface):
        """Draw the active dungeon room and progression UI."""
        if self.encounter_manager is not None:
            draw_combat_scene(scene_surface, self.player, self.encounter_manager, draw_arena)
        else:
            draw_arena(scene_surface)

        screen.fill((0, 0, 0))
        screen.blit(scene_surface, self.impact.get_camera_offset())

        if self.encounter_manager is not None:
            self.draw_combat_ui(screen)

        if not self.room_manager.is_dungeon_complete():
            draw_dungeon_hud(screen, self.room_manager, self.reward_manager, self.player)

        if self.room_manager.is_room_cleared():
            draw_room_cleared(screen)
        elif self.room_manager.is_reward_active():
            draw_reward_select(screen, self.reward_manager)
        elif self.room_manager.is_dungeon_complete():
            draw_dungeon_clear_summary(screen, self.room_manager, self.reward_manager, self.player)
        elif self.room_manager.current_room_type() == ROOM_BOSS_PLACEHOLDER:
            draw_boss_placeholder(screen)

    def handle_continue(self):
        """Advance room flow from clear and placeholder states."""
        if self.room_manager.is_room_cleared():
            self.start_reward_selection()
            return

        if self.room_manager.current_room_type() == ROOM_BOSS_PLACEHOLDER:
            self.room_manager.advance_room()
            self.enter_current_room()

    def handle_reward_input(self, key):
        """Navigate and confirm room reward selection."""
        if key in (pygame.K_a, pygame.K_LEFT):
            self.reward_manager.select_previous()
        elif key in (pygame.K_d, pygame.K_RIGHT):
            self.reward_manager.select_next()
        elif key == pygame.K_RETURN:
            applied_reward = self.reward_manager.apply_selected(self.player)
            if applied_reward is None:
                return
            self.room_manager.advance_room()
            self.enter_current_room()

    def start_reward_selection(self):
        """Move an encounter clear into the reward selection state."""
        self.room_manager.mark_room_cleared()
        self.room_manager.start_reward()
        if not self.reward_manager.has_options():
            self.reward_manager.generate_options()

    def enter_current_room(self):
        """Initialize combat systems for the current room type."""
        self.impact = CombatImpact()

        if self.room_manager.current_room_type() == ROOM_ENCOUNTER:
            self.encounter_manager = EncounterManager()
        else:
            self.encounter_manager = None

    def is_active_encounter_room(self):
        """Return True only while an encounter room is actively running."""
        return (
            self.room_manager.is_room_active()
            and self.room_manager.current_room_type() == ROOM_ENCOUNTER
            and self.encounter_manager is not None
        )

    def draw_combat_ui(self, screen):
        """Draw persistent player and encounter UI for active combat rooms."""
        draw_health_bar(
            screen,
            60,
            55,
            420,
            28,
            self.player.health,
            self.player.max_health,
            HEALTH_PLAYER,
            "PLAYER",
        )
        self.encounter_manager.draw_ui(screen)
