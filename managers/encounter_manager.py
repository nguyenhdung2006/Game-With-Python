"""Wave and encounter flow management.

This manager owns wave definitions, active enemies, and progression, while a
small director helper owns pacing and pressure presentation.
"""

from config.dungeon_layout_config import (
    DEFAULT_ENEMY_SPAWN_LEFT_START,
    DEFAULT_ENEMY_SPAWN_RIGHT_MARGIN,
    DEFAULT_ENEMY_SPAWN_RIGHT_START,
    DEFAULT_ENEMY_SPAWN_SPACING,
)
from managers.encounter_director import EncounterDirector
from managers.encounter_profiles import WAVE_PROFILES
from settings import ENCOUNTER_WAVE_DELAY, ENEMY_STATE_TELEGRAPH, GROUND_Y, HEALTH_ENEMY, WIDTH
from systems.enemy_spacing import apply_enemy_spacing
from ui.health_bar import draw_health_bar


class EncounterManager:
    """Spawn hardcoded waves and track when the encounter is cleared."""

    def __init__(self, wave_definitions=None, room_layout=None, audio_manager=None):
        self.wave_definitions = WAVE_PROFILES if wave_definitions is None else wave_definitions
        self.room_layout = room_layout
        self.audio_manager = audio_manager
        self.active_enemies = []
        self.current_wave_index = -1
        self.wave_delay_timer = ENCOUNTER_WAVE_DELAY
        self.encounter_cleared = False
        self.wave_clear_pending = False
        self.director = EncounterDirector()

    def update(self, player, dt):
        """Update wave flow and all active enemies."""
        self.director.update(dt, self.active_enemies)

        if self.encounter_cleared:
            return

        if not self.active_enemies:
            self.update_wave_progress(dt, player)
            return

        if all(enemy.defeated for enemy in self.active_enemies):
            if not self.wave_clear_pending:
                self.wave_clear_pending = True
                self.wave_delay_timer = ENCOUNTER_WAVE_DELAY
                self.director.start_recovery_window(
                    self.current_wave_index < len(self.wave_definitions) - 1
                )

            self.wave_delay_timer = max(0, self.wave_delay_timer - dt)
            if self.wave_delay_timer == 0:
                if self.current_wave_index >= len(self.wave_definitions) - 1:
                    self.encounter_cleared = True
                    self.director.mark_encounter_cleared()
                self.active_enemies = []
                self.wave_clear_pending = False
            return

        leader_enemy = self.director.get_attack_leader(self.active_enemies, player)
        for enemy in self.active_enemies:
            allow_attack = enemy is leader_enemy or enemy.is_attack_active()
            if enemy.state == ENEMY_STATE_TELEGRAPH:
                allow_attack = True
            enemy.update(player, dt, allow_attack=allow_attack)

        apply_enemy_spacing(self.active_enemies, player, leader_enemy, dt, self.get_current_wave_profile())

    def update_wave_progress(self, dt, player):
        """Advance to the next wave after a short readable delay."""
        if self.encounter_cleared:
            return

        self.wave_delay_timer = max(0, self.wave_delay_timer - dt)
        if self.wave_delay_timer > 0:
            return

        self.current_wave_index += 1
        self.spawn_wave(self.current_wave_index, player)

    def spawn_wave(self, wave_index, player):
        """Create enemies for one wave at readable positions."""
        wave_profile = self.wave_definitions[wave_index]
        enemy_classes = wave_profile["enemies"]
        spawn_positions = self.get_spawn_positions(len(enemy_classes), player)
        self.active_enemies = []
        spawn_from_right = spawn_positions[0][0] >= player.rect.centerx

        for index, enemy_class in enumerate(enemy_classes):
            spawn_x, spawn_floor_y = spawn_positions[index]
            enemy = enemy_class(spawn_x)
            enemy.audio_manager = self.audio_manager
            enemy.rect.bottom = spawn_floor_y
            self.configure_enemy_entrance(
                enemy,
                index,
                spawn_from_right,
                wave_profile,
            )
            self.active_enemies.append(enemy)

        self.wave_delay_timer = ENCOUNTER_WAVE_DELAY
        self.wave_clear_pending = False
        self.director.start_wave(wave_index + 1, wave_profile)

    def get_spawn_positions(self, count, player):
        """Choose configured room anchors away from the player."""
        if self.room_layout is not None:
            positions = self.room_layout.enemy_spawn_points_for_player(player.rect.centerx)
            if len(positions) >= count:
                return positions[:count]

        if player.rect.centerx < WIDTH // 2:
            positions = self.build_side_spawn_positions(
                count,
                DEFAULT_ENEMY_SPAWN_RIGHT_START,
                DEFAULT_ENEMY_SPAWN_SPACING,
                WIDTH - DEFAULT_ENEMY_SPAWN_RIGHT_MARGIN,
            )
        else:
            positions = self.build_side_spawn_positions(
                count,
                DEFAULT_ENEMY_SPAWN_LEFT_START,
                DEFAULT_ENEMY_SPAWN_SPACING,
                WIDTH - DEFAULT_ENEMY_SPAWN_RIGHT_MARGIN,
            )

        return tuple((x, GROUND_Y) for x in positions[:count])

    def build_side_spawn_positions(self, count, start_x, spacing, max_x):
        """Return enough clamped spawn positions for larger future waves."""
        positions = []
        for index in range(count):
            positions.append(min(max_x, start_x + spacing * index))
        return positions

    def configure_enemy_entrance(self, enemy, index, spawn_from_right, wave_profile):
        """Apply small staggered entrance timing so waves feel less robotic."""
        enemy.spawn_target_x = enemy.rect.x
        enemy.entrance_delay_timer = wave_profile["spawn_stagger"] * index
        enemy.entrance_pause_timer = wave_profile["entrance_pause"] + (0.03 * index)
        enemy.entrance_move_speed = wave_profile["entrance_move_speed"]

        offset = wave_profile["entrance_offset"] + (index * 12)
        left_bound, right_bound = self.get_arena_bounds()
        if spawn_from_right:
            enemy.x = min(right_bound - enemy.width, enemy.spawn_target_x + offset)
        else:
            enemy.x = max(left_bound, enemy.spawn_target_x - offset)
        enemy.rect.x = round(enemy.x)

    def get_arena_bounds(self):
        """Return room-specific bounds with a full-screen fallback."""
        if self.room_layout is None:
            return 0, WIDTH
        return self.room_layout.arena_bounds

    def get_current_wave_profile(self):
        """Return the active wave's spacing/pacing profile."""
        if self.current_wave_index < 0 or self.current_wave_index >= len(self.wave_definitions):
            return self.wave_definitions[0]

        return self.wave_definitions[self.current_wave_index]

    def get_enemies(self):
        """Expose the active enemies for combat processing."""
        return self.active_enemies

    def draw(self, surface):
        """Draw every active enemy."""
        for enemy in self.active_enemies:
            enemy.draw(surface)

    def draw_ui(self, surface):
        """Draw wave status and enemy health bars."""
        self.director.draw(surface, self.current_wave_index + 1)
        self.draw_enemy_bars(surface)

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
