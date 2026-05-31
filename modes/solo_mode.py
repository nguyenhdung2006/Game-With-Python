"""Solo / Versus 1v1 arena sandbox."""

import pygame

from config.boss_config import SOLO_BOSS_CONFIG
from config.mode_config import (
    SOLO_ATTACK_ENERGY_GAIN,
    SOLO_COMBO_BURST_ENERGY_COST,
    SOLO_ENEMY_RIGHT_OFFSET,
    SOLO_ENERGY_BG,
    SOLO_ENERGY_COLOR,
    SOLO_FINISHER_ENERGY_GAIN,
    SOLO_HURT_ENERGY_GAIN,
    SOLO_MAX_ENERGY,
    SOLO_PLAYER_ATTACK_RANGES,
    SOLO_PLAYER_SPAWN_X,
    SOLO_START_ENERGY,
)
from entities.elite_enemy import EliteEnemy
from entities.player import Player
from settings import (
    GROUND_Y,
    HEALTH_ENEMY,
    HEALTH_PLAYER,
    HEIGHT,
    PLAYER_HEIGHT,
    WHITE,
    WIDTH,
)
from systems.combat import process_enemy_attacks, process_player_attacks
from systems.effects import CombatImpact
from systems.projectile_manager import ProjectileManager
from systems.skill_manager import SkillManager
from systems.solo_combo_burst import SoloComboBurst
from systems.solo_sprite_renderer import SoloSpriteRenderer
from ui.completion_overlay import draw_completion_overlay
from ui.dungeon_hud import draw_text_panel
from ui.health_bar import draw_health_bar
from world.battlefield import draw_arena


SOLO_ACTIVE = "ACTIVE"
SOLO_VICTORY = "VICTORY"
SOLO_DEFEAT = "DEFEAT"


class SoloMode:
    """Playable single-fight arena using the shared combat foundation."""

    def __init__(self):
        self.reset_fight()

    def reset_fight(self):
        """Create a clean rematch without carrying combat or cooldown state."""
        self.player = Player(SOLO_PLAYER_SPAWN_X, GROUND_Y - PLAYER_HEIGHT)
        self.enemy = EliteEnemy(WIDTH - SOLO_ENEMY_RIGHT_OFFSET)
        self.configure_solo_boss()
        self.impact = CombatImpact()
        self.projectile_manager = ProjectileManager()
        self.skill_manager = SkillManager(self.projectile_manager)
        self.combo_burst = SoloComboBurst(energy_cost=SOLO_COMBO_BURST_ENERGY_COST)
        self.sprite_renderer = SoloSpriteRenderer()
        self.boss_skill_name = "Heavy Slash"
        self.max_energy = SOLO_MAX_ENERGY
        self.energy = SOLO_START_ENERGY
        self.attack_energy_gain = SOLO_ATTACK_ENERGY_GAIN
        self.finisher_energy_gain = SOLO_FINISHER_ENERGY_GAIN
        self.hurt_energy_gain = SOLO_HURT_ENERGY_GAIN
        self.result_state = SOLO_ACTIVE

    def handle_event(self, event):
        """Handle player combat inputs during the active duel."""
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_r and not self.is_active():
            self.reset_fight()
            return
        if not self.is_active() or self.impact.is_hitstop_active():
            return

        if event.key == pygame.K_w:
            self.player.jump()
        elif event.key == pygame.K_LSHIFT:
            self.player.start_dash()
        elif event.key == pygame.K_u:
            self.energy, _ = self.combo_burst.start(self.player, self.energy)
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
        elif event.key == pygame.K_j and not self.combo_burst.active:
            self.player.start_light_attack()

    def update(self, keys, dt):
        """Update the 1v1 fight."""
        self.impact.update(dt)
        if not self.is_active() or self.impact.is_hitstop_active():
            return

        previous_player_health = self.player.health
        self.skill_manager.update(dt)
        self.player.update(keys, dt)
        self.combo_burst.update(self.player, dt)
        self.tune_player_attack_range()
        self.enemy.update(self.player, dt)

        enemies = [self.enemy]
        self.projectile_manager.update(dt, enemies)

        player_hit_result = process_player_attacks(self.player, enemies)
        enemy_hit_results = process_enemy_attacks(enemies, self.player)

        if player_hit_result:
            self.impact.start_hit_impact(player_hit_result)
            self.gain_energy_from_player_hit()
        for enemy_hit_result in enemy_hit_results:
            self.impact.start_hit_impact(enemy_hit_result)

        if self.player.health < previous_player_health:
            self.add_energy(self.hurt_energy_gain)

        self.sprite_renderer.update(self.player, self.enemy, dt)
        self.update_result_state()

    def draw(self, screen, scene_surface):
        """Draw the arena, fighters, HUD, and win/loss overlay."""
        draw_arena(scene_surface)
        self.sprite_renderer.draw_player(scene_surface, self.player)
        self.projectile_manager.draw(scene_surface)
        self.sprite_renderer.draw_boss(scene_surface, self.enemy)

        screen.fill((0, 0, 0))
        screen.blit(scene_surface, self.impact.get_camera_offset())
        self.draw_ui(screen)

        if self.result_state == SOLO_VICTORY:
            self.draw_result(screen, "Victory")
        elif self.result_state == SOLO_DEFEAT:
            self.draw_result(screen, "Defeat")

    def draw_ui(self, screen):
        """Draw player/enemy health and skill readiness."""
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
        draw_health_bar(
            screen,
            WIDTH - 440,
            55,
            380,
            28,
            self.enemy.health,
            self.enemy.max_health,
            HEALTH_ENEMY,
            "SOLO BOSS",
        )
        self.draw_energy_bar(screen)
        draw_text_panel(screen, self.get_solo_skill_lines(), 24, 152, 360)

    def draw_result(self, screen, label):
        """Draw the end-state overlay without changing the fight underneath."""
        draw_completion_overlay(screen, label, "Rematch")

    def update_result_state(self):
        """Move to the correct terminal state once a fighter is defeated."""
        if self.player.defeated:
            self.result_state = SOLO_DEFEAT
        elif self.enemy.defeated:
            self.result_state = SOLO_VICTORY

    def is_active(self):
        """Return True while the fight is still playable."""
        return self.result_state == SOLO_ACTIVE

    def configure_solo_boss(self):
        """Tune the Solo sprite-test boss without changing Dungeon balance."""
        self.enemy.label = SOLO_BOSS_CONFIG["label"]
        self.enemy.max_health = SOLO_BOSS_CONFIG["max_health"]
        self.enemy.health = self.enemy.max_health
        self.enemy.attack_range = SOLO_BOSS_CONFIG["attack_range"]
        self.enemy.attack_start_distance = SOLO_BOSS_CONFIG["attack_start_distance"]
        self.enemy.skill_controller.skill_range = SOLO_BOSS_CONFIG["skill_range"]
        self.enemy.skill_controller.skill_height = SOLO_BOSS_CONFIG["skill_height"]
        self.enemy.skill_controller.damage = SOLO_BOSS_CONFIG["skill_damage"]

    def tune_player_attack_range(self):
        """Keep Solo gameplay hitboxes shorter than slash sprite visuals."""
        if not self.player.is_attacking or self.player.is_counter_attacking:
            return

        tuned_range = SOLO_PLAYER_ATTACK_RANGES.get(self.player.combo_step)
        if tuned_range is not None:
            self.player.attack_range = tuned_range

    def gain_energy_from_player_hit(self):
        """Reward one successful player hit with clamped energy."""
        if self.player.combo_step >= 3:
            self.add_energy(self.finisher_energy_gain)
        else:
            self.add_energy(self.attack_energy_gain)

    def add_energy(self, amount):
        """Clamp the Solo prototype energy resource."""
        self.energy = max(0, min(self.max_energy, self.energy + amount))

    def draw_energy_bar(self, screen):
        """Draw a compact energy bar beneath player health."""
        x = 60
        y = 96
        width = 300
        height = 16
        fill_width = round(width * (self.energy / self.max_energy))

        pygame.draw.rect(screen, SOLO_ENERGY_BG, (x, y, width, height))
        pygame.draw.rect(screen, SOLO_ENERGY_COLOR, (x, y, fill_width, height))
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)

        font = pygame.font.Font(None, 24)
        label = font.render(f"ENERGY {self.energy} / {self.max_energy}", True, WHITE)
        screen.blit(label, (x, y + 20))

    def get_solo_skill_lines(self):
        """Return Solo-specific skill labels without changing Dungeon bindings."""
        kamehameha = self.skill_manager.get_slot(2)
        return [
            "Skills:",
            f"U: Combo Burst {self.combo_burst.status_text(self.energy)}",
            f"I: Kamehameha {kamehameha.status_text()}",
            "O: Locked",
        ]
