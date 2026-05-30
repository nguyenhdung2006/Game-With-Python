"""Dungeon / Wave mode wrapper around the existing combat encounter."""

import pygame

from entities.player import Player
from managers.encounter_manager import EncounterManager
from settings import GROUND_Y, HEALTH_PLAYER, PLAYER_HEIGHT
from systems.combat import process_enemy_attacks, process_player_attacks
from systems.effects import CombatImpact
from systems.render_layers import draw_combat_scene
from ui.health_bar import draw_health_bar
from world.battlefield import draw_arena


class DungeonMode:
    """Own the current wave-combat loop so main.py can route between screens."""

    def __init__(self):
        self.player = Player(180, GROUND_Y - PLAYER_HEIGHT)
        self.encounter_manager = EncounterManager()
        self.impact = CombatImpact()

    def handle_event(self, event):
        """Handle combat inputs for the playable dungeon mode."""
        if self.impact.is_hitstop_active() or event.type != pygame.KEYDOWN:
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
        """Update combat only when hitstop is not holding action frames."""
        self.impact.update(dt)
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

    def draw(self, screen, scene_surface):
        """Draw the combat scene and combat UI."""
        draw_combat_scene(scene_surface, self.player, self.encounter_manager, draw_arena)

        screen.fill((0, 0, 0))
        screen.blit(scene_surface, self.impact.get_camera_offset())

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
