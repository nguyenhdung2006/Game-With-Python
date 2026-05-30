"""Solo / Versus 1v1 arena sandbox."""

import pygame

from entities.basic_enemy import BasicEnemy
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
from ui.dungeon_hud import draw_text_panel, get_skill_lines
from ui.health_bar import draw_health_bar
from world.battlefield import draw_arena


SOLO_ACTIVE = "ACTIVE"
SOLO_VICTORY = "VICTORY"
SOLO_DEFEAT = "DEFEAT"


class SoloMode:
    """Playable single-fight arena using the shared combat foundation."""

    def __init__(self):
        self.player = Player(180, GROUND_Y - PLAYER_HEIGHT)
        self.enemy = BasicEnemy(WIDTH - 280)
        self.impact = CombatImpact()
        self.projectile_manager = ProjectileManager()
        self.skill_manager = SkillManager(self.projectile_manager)
        self.result_state = SOLO_ACTIVE

    def handle_event(self, event):
        """Handle player combat inputs during the active duel."""
        if event.type != pygame.KEYDOWN:
            return
        if not self.is_active() or self.impact.is_hitstop_active():
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
        """Update the 1v1 fight."""
        self.impact.update(dt)
        if not self.is_active() or self.impact.is_hitstop_active():
            return

        self.skill_manager.update(dt)
        self.player.update(keys, dt)
        self.enemy.update(self.player, dt)

        enemies = [self.enemy]
        self.projectile_manager.update(dt, enemies)

        player_hit_result = process_player_attacks(self.player, enemies)
        enemy_hit_results = process_enemy_attacks(enemies, self.player)

        if player_hit_result:
            self.impact.start_hit_impact(player_hit_result)
        for enemy_hit_result in enemy_hit_results:
            self.impact.start_hit_impact(enemy_hit_result)

        self.update_result_state()

    def draw(self, screen, scene_surface):
        """Draw the arena, fighters, HUD, and win/loss overlay."""
        draw_arena(scene_surface)
        self.player.draw(scene_surface)
        self.projectile_manager.draw(scene_surface)
        self.enemy.draw(scene_surface)

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
            "DUEL ENEMY",
        )
        draw_text_panel(screen, get_skill_lines(self.skill_manager), 24, 112, 330)

    def draw_result(self, screen, label):
        """Draw the end-state overlay without changing the fight underneath."""
        title_font = pygame.font.Font(None, 72)
        prompt_font = pygame.font.Font(None, 30)
        panel = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 94, 440, 188)

        pygame.draw.rect(screen, (18, 22, 34), panel, border_radius=8)
        pygame.draw.rect(screen, WHITE, panel, 2, border_radius=8)

        title = title_font.render(label, True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, panel.top + 66)))

        prompt = prompt_font.render("Esc returns to Mode Select", True, (190, 198, 212))
        screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, panel.bottom - 42)))

    def update_result_state(self):
        """Move to the correct terminal state once a fighter is defeated."""
        if self.player.defeated:
            self.result_state = SOLO_DEFEAT
        elif self.enemy.defeated:
            self.result_state = SOLO_VICTORY

    def is_active(self):
        """Return True while the fight is still playable."""
        return self.result_state == SOLO_ACTIVE
