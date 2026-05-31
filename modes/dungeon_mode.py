"""Dungeon / Wave mode wrapper around the existing combat encounter."""

import pygame

from entities.player import Player
from managers.encounter_manager import EncounterManager
from managers.encounter_profiles import BOSS_ROOM_PROFILES
from managers.room_manager import RoomManager
from managers.room_state import ROOM_BOSS_ENCOUNTER, ROOM_ENCOUNTER
from settings import HEALTH_PLAYER
from systems.combat import process_enemy_attacks, process_player_attacks
from systems.effects import CombatImpact
from systems.projectile_manager import ProjectileManager
from systems.reward_manager import RewardManager
from systems.render_layers import draw_combat_scene
from systems.skill_manager import SkillManager
from ui.completion_overlay import draw_completion_overlay
from ui.dungeon_hud import draw_dungeon_clear_summary, draw_dungeon_hud
from ui.health_bar import draw_health_bar
from ui.reward_select import draw_reward_select
from ui.room_banner import draw_room_cleared
from world.dungeon_room import draw_dungeon_room


class DungeonMode:
    """Own the current wave-combat loop so main.py can route between screens."""

    def __init__(self):
        self.reset_run()

    def reset_run(self):
        """Create a clean dungeon run without carrying terminal combat state."""
        self.room_manager = RoomManager()
        self.player = Player(*self.room_manager.current_layout().player_spawn)
        self.encounter_manager = None
        self.impact = CombatImpact()
        self.projectile_manager = ProjectileManager()
        self.skill_manager = SkillManager(self.projectile_manager)
        self.reward_manager = RewardManager()
        self.enter_current_room()

    def handle_event(self, event):
        """Handle room progression and combat inputs for dungeon mode."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_r and (
            self.room_manager.is_dungeon_defeated() or self.room_manager.is_dungeon_complete()
        ):
            self.reset_run()
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
        elif event.key == pygame.K_u:
            self.skill_manager.use_slot(1, self.player)
        elif event.key == pygame.K_i:
            self.skill_manager.use_slot(2, self.player)
        elif event.key == pygame.K_o:
            self.skill_manager.use_slot(3, self.player)
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

        self.skill_manager.update(dt)
        self.player.update(keys, dt)
        self.encounter_manager.update(self.player, dt)
        active_enemies = self.encounter_manager.get_enemies()
        self.projectile_manager.update(dt, active_enemies)

        player_hit_result = process_player_attacks(self.player, active_enemies)
        enemy_hit_results = process_enemy_attacks(active_enemies, self.player)

        if player_hit_result:
            self.impact.start_hit_impact(player_hit_result)
        for enemy_hit_result in enemy_hit_results:
            self.impact.start_hit_impact(enemy_hit_result)

        if self.player.defeated:
            self.complete_dungeon_defeat()
            return

        if self.encounter_manager.encounter_cleared:
            self.complete_current_encounter_room()

    def draw(self, screen, scene_surface):
        """Draw the active dungeon room and progression UI."""
        if self.encounter_manager is not None:
            draw_combat_scene(
                scene_surface,
                self.player,
                self.encounter_manager,
                self.draw_room_world,
                self.projectile_manager,
            )
        else:
            self.draw_room_world(scene_surface)

        screen.fill((0, 0, 0))
        screen.blit(scene_surface, self.impact.get_camera_offset())

        if self.encounter_manager is not None:
            self.draw_combat_ui(screen)

        if not self.room_manager.is_dungeon_complete():
            draw_dungeon_hud(
                screen,
                self.room_manager,
                self.reward_manager,
                self.player,
                self.skill_manager,
            )

        if self.room_manager.is_room_cleared():
            draw_room_cleared(screen)
        elif self.room_manager.is_reward_active():
            draw_reward_select(screen, self.reward_manager)
        elif self.room_manager.is_dungeon_complete():
            draw_dungeon_clear_summary(screen, self.room_manager, self.reward_manager, self.player)
        elif self.room_manager.is_dungeon_defeated():
            draw_completion_overlay(screen, "Defeat", "Retry Run")

    def handle_continue(self):
        """Advance room flow from clear states."""
        if self.room_manager.is_room_cleared():
            self.start_reward_selection()

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
        self.room_manager.start_reward()
        if not self.reward_manager.has_options():
            self.reward_manager.generate_options()

    def complete_current_encounter_room(self):
        """Resolve normal and boss room clears without changing combat rules."""
        self.reward_manager.apply_room_clear_effects(self.player)

        if self.room_manager.current_room_type() == ROOM_BOSS_ENCOUNTER:
            self.room_manager.advance_room()
            self.enter_current_room()
            return

        self.room_manager.mark_room_cleared()
        self.stop_current_combat()

    def complete_dungeon_defeat(self):
        """Stop combat and expose retry after the player is defeated."""
        self.room_manager.mark_dungeon_defeated()
        self.stop_current_combat()

    def stop_current_combat(self):
        """Discard transient combat objects before a non-combat flow state."""
        self.projectile_manager.clear()
        self.skill_manager.reset_cooldowns()
        self.encounter_manager = None

    def enter_current_room(self):
        """Initialize combat systems for the current room type."""
        self.impact = CombatImpact()
        self.projectile_manager.clear()
        self.place_player_at_current_layout_spawn()
        room_layout = self.room_manager.current_layout()

        if self.room_manager.current_room_type() == ROOM_ENCOUNTER:
            self.encounter_manager = EncounterManager(room_layout=room_layout)
        elif self.room_manager.current_room_type() == ROOM_BOSS_ENCOUNTER:
            self.encounter_manager = EncounterManager(BOSS_ROOM_PROFILES, room_layout=room_layout)
        else:
            self.encounter_manager = None

    def place_player_at_current_layout_spawn(self):
        """Move the existing run player onto the current layout spawn point."""
        spawn_x, spawn_y = self.room_manager.current_layout().player_spawn
        self.player.x = float(spawn_x)
        self.player.y = float(spawn_y)
        self.player.rect.topleft = (spawn_x, spawn_y)
        self.player.velocity_y = 0
        self.player.knockback_velocity_x = 0
        self.player.grounded = True
        self.player.dash_trail = []

    def draw_room_world(self, surface):
        """Draw the current fixed room layout with a clear-state exit marker."""
        show_exit = self.room_manager.is_room_cleared() or self.room_manager.is_reward_active()
        draw_dungeon_room(surface, self.room_manager.current_layout(), show_exit=show_exit)

    def is_active_encounter_room(self):
        """Return True only while an encounter room is actively running."""
        return (
            self.room_manager.is_room_active()
            and self.room_manager.current_room_type() in {ROOM_ENCOUNTER, ROOM_BOSS_ENCOUNTER}
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
