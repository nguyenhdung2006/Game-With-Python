"""Wave and encounter flow management.

This manager owns active enemies, wave spawning, and encounter progression so
main.py does not have to manually juggle enemy lists and transition rules.
"""

import pygame

from entities.basic_enemy import BasicEnemy
from entities.fast_enemy import FastEnemy
from settings import (
    ENCOUNTER_STATUS_Y,
    ENCOUNTER_WAVE_DELAY,
    ENEMY_STATE_TELEGRAPH,
    HEALTH_ENEMY,
    WHITE,
    WIDTH,
)
from ui.health_bar import draw_health_bar


class EncounterManager:
    """Spawn hardcoded waves and track when the encounter is cleared."""

    def __init__(self):
        self.wave_definitions = [
            [BasicEnemy],
            [BasicEnemy, FastEnemy],
            [FastEnemy, FastEnemy, BasicEnemy],
        ]
        self.active_enemies = []
        self.current_wave_index = -1
        self.wave_delay_timer = ENCOUNTER_WAVE_DELAY
        self.encounter_cleared = False

    def update(self, player, dt):
        """Update wave flow and all active enemies."""
        if self.encounter_cleared:
            return

        if not self.active_enemies:
            self.update_wave_progress(dt, player)
            return

        if all(enemy.defeated for enemy in self.active_enemies):
            self.wave_delay_timer = max(0, self.wave_delay_timer - dt)
            if self.wave_delay_timer == 0:
                self.active_enemies = []
            return

        leader_enemy = self.get_attack_leader(player)
        for enemy in self.active_enemies:
            allow_attack = leader_enemy is None or enemy is leader_enemy or enemy.is_attack_active()
            if enemy.state == ENEMY_STATE_TELEGRAPH:
                allow_attack = True
            enemy.update(player, dt, allow_attack=allow_attack)

    def update_wave_progress(self, dt, player):
        """Advance to the next wave after a short readable delay."""
        if self.current_wave_index >= len(self.wave_definitions) - 1:
            self.encounter_cleared = True
            return

        self.wave_delay_timer = max(0, self.wave_delay_timer - dt)
        if self.wave_delay_timer > 0:
            return

        self.current_wave_index += 1
        self.spawn_wave(self.current_wave_index, player)

    def spawn_wave(self, wave_index, player):
        """Create enemies for one wave at readable positions."""
        enemy_classes = self.wave_definitions[wave_index]
        spawn_positions = self.get_spawn_positions(len(enemy_classes), player)
        self.active_enemies = [
            enemy_class(spawn_positions[index])
            for index, enemy_class in enumerate(enemy_classes)
        ]
        self.wave_delay_timer = ENCOUNTER_WAVE_DELAY

    def get_spawn_positions(self, count, player):
        """Choose side-based spawn positions away from the player."""
        if player.rect.centerx < WIDTH // 2:
            positions = [760, 930, 1090]
        else:
            positions = [160, 330, 500]

        return positions[:count]

    def get_attack_leader(self, player):
        """Allow only one close enemy to initiate pressure at a time if possible."""
        engaged_enemies = [
            enemy
            for enemy in self.active_enemies
            if not enemy.defeated and (enemy.is_attack_active() or enemy.state == ENEMY_STATE_TELEGRAPH)
        ]
        if engaged_enemies:
            return engaged_enemies[0]

        alive_enemies = [enemy for enemy in self.active_enemies if not enemy.defeated]
        if not alive_enemies:
            return None

        return min(alive_enemies, key=lambda enemy: abs(enemy.rect.centerx - player.rect.centerx))

    def get_enemies(self):
        """Expose the active enemies for combat processing."""
        return self.active_enemies

    def draw(self, surface):
        """Draw every active enemy."""
        for enemy in self.active_enemies:
            enemy.draw(surface)

    def draw_ui(self, surface):
        """Draw wave status and enemy health bars."""
        self.draw_status_text(surface)
        self.draw_enemy_bars(surface)

    def draw_status_text(self, surface):
        """Show the current wave number or encounter-cleared state."""
        font = pygame.font.Font(None, 42)
        if self.encounter_cleared:
            text = "Encounter Cleared"
        else:
            text = f"Wave {max(1, self.current_wave_index + 1)}"

        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, ENCOUNTER_STATUS_Y))
        surface.blit(text_surface, text_rect)

    def draw_enemy_bars(self, surface):
        """Stack health bars for active enemies on the right side."""
        for index, enemy in enumerate(self.active_enemies):
            y = 38 + index * 46
            label = f"{enemy.label} {index + 1}"
            draw_health_bar(
                surface,
                760,
                y,
                360,
                24,
                enemy.health,
                enemy.max_health,
                HEALTH_ENEMY,
                label,
            )
