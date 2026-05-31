"""Solo / Versus 1v1 arena sandbox."""

import pygame

from config.boss_config import SOLO_BOSS_CONFIG
from config.mode_config import (
    SOLO_BOSS_ENERGY_COLOR,
    SOLO_COMBO_BURST_ENERGY_COST,
    SOLO_DEALT_HIT_ENERGY_GAIN,
    SOLO_ENEMY_RIGHT_OFFSET,
    SOLO_ENERGY_BG,
    SOLO_ENERGY_COLOR,
    SOLO_HURT_ENERGY_GAIN,
    SOLO_KAMEHAMEHA_ENERGY_COST,
    SOLO_MAX_ENERGY,
    SOLO_PLAYER_ATTACK_RANGES,
    SOLO_PLAYER_SPAWN_X,
    SOLO_SETUP_BOSS_HP_MAX,
    SOLO_SETUP_BOSS_HP_MIN,
    SOLO_SETUP_BOSS_HP_STEP,
    SOLO_SETUP_PLAYER_HP_MAX,
    SOLO_SETUP_PLAYER_HP_MIN,
    SOLO_SETUP_PLAYER_HP_STEP,
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
from systems.solo_boss_combo_controller import SoloBossComboController
from systems.solo_combo_burst import SoloComboBurst
from systems.solo_sprite_renderer import SoloSpriteRenderer
from ui.completion_overlay import draw_completion_overlay
from ui.controls_overlay import draw_controls_overlay
from ui.dungeon_hud import draw_text_panel
from ui.health_bar import draw_health_bar
from ui.pause_overlay import draw_pause_overlay
from ui.solo_setup import draw_solo_setup, slider_index_at, value_from_slider_x
from world.battlefield import draw_arena


SOLO_SETUP = "SETUP"
SOLO_ACTIVE = "ACTIVE"
SOLO_VICTORY = "VICTORY"
SOLO_DEFEAT = "DEFEAT"


class SoloMode:
    """Playable single-fight arena using the shared combat foundation."""

    def __init__(self):
        self.setup_player_hp = SOLO_SETUP_PLAYER_HP_MIN
        self.setup_boss_hp = SOLO_SETUP_BOSS_HP_MIN
        self.setup_selected_slider = 0
        self.setup_dragging_slider = None
        self.reset_fight(show_setup=True)

    def reset_fight(self, show_setup=False):
        """Create a clean rematch without carrying combat or cooldown state."""
        self.player = Player(SOLO_PLAYER_SPAWN_X, GROUND_Y - PLAYER_HEIGHT)
        self.player.max_health = self.setup_player_hp
        self.player.health = self.player.max_health
        self.enemy = EliteEnemy(WIDTH - SOLO_ENEMY_RIGHT_OFFSET)
        self.configure_solo_boss()
        self.impact = CombatImpact()
        self.projectile_manager = ProjectileManager()
        self.skill_manager = SkillManager(self.projectile_manager)
        self.combo_burst = SoloComboBurst(energy_cost=SOLO_COMBO_BURST_ENERGY_COST)
        self.sprite_renderer = SoloSpriteRenderer()
        self.max_energy = SOLO_MAX_ENERGY
        self.energy = SOLO_START_ENERGY
        self.dealt_hit_energy_gain = SOLO_DEALT_HIT_ENERGY_GAIN
        self.hurt_energy_gain = SOLO_HURT_ENERGY_GAIN
        self.paused = False
        self.controls_visible = False
        self.result_state = SOLO_SETUP if show_setup else SOLO_ACTIVE

    def handle_event(self, event):
        """Handle player combat inputs during the active duel."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                self.controls_visible = not self.controls_visible
                return
            if self.controls_visible:
                return
            if event.key == pygame.K_p and self.can_pause():
                self.paused = not self.paused
                return
            if self.paused:
                if event.key == pygame.K_r:
                    self.reset_fight()
                return

        if self.is_setup():
            self.handle_setup_event(event)
            return
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
            self.try_use_kamehameha()
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
        if self.is_gameplay_frozen():
            return

        self.impact.update(dt)
        if not self.is_active() or self.impact.is_hitstop_active():
            return

        previous_player_health = self.player.health
        previous_enemy_health = self.enemy.health
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
        for enemy_hit_result in enemy_hit_results:
            self.impact.start_hit_impact(enemy_hit_result)

        self.apply_energy_from_health_changes(previous_player_health, previous_enemy_health)

        self.sprite_renderer.update(self.player, self.enemy, dt)
        self.update_result_state()

    def draw(self, screen, scene_surface):
        """Draw the arena, fighters, HUD, and win/loss overlay."""
        if self.is_setup():
            draw_solo_setup(
                screen,
                self.setup_player_hp,
                self.setup_boss_hp,
                self.setup_selected_slider,
                self.setup_slider_specs(),
            )
            self.draw_qol_overlays(screen)
            return

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

        self.draw_qol_overlays(screen)

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
        self.draw_boss_energy_bar(screen)
        self.draw_player_status_feedback(screen)
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

    def is_setup(self):
        """Return True while Solo is waiting for pre-fight HP confirmation."""
        return self.result_state == SOLO_SETUP

    def can_pause(self):
        """Allow pause only while the Solo duel is actively running."""
        return self.is_active()

    def is_gameplay_frozen(self):
        """Freeze all gameplay timers while a modal QoL overlay is open."""
        return self.paused or self.controls_visible

    def draw_qol_overlays(self, screen):
        """Draw pause first so the controls panel can sit above it when requested."""
        if self.paused:
            draw_pause_overlay(screen, "Restart Fight")
        if self.controls_visible:
            draw_controls_overlay(screen, "solo")

    def configure_solo_boss(self):
        """Tune the Solo sprite-test boss without changing Dungeon balance."""
        self.enemy.label = SOLO_BOSS_CONFIG["label"]
        self.enemy.max_health = self.setup_boss_hp
        self.enemy.health = self.enemy.max_health
        self.enemy.attack_range = SOLO_BOSS_CONFIG["attack_range"]
        self.enemy.attack_start_distance = SOLO_BOSS_CONFIG["attack_start_distance"]
        self.enemy.skill_controller = SoloBossComboController()
        self.enemy.max_energy = self.enemy.skill_controller.max_energy
        self.enemy.energy = self.enemy.skill_controller.start_energy

    def tune_player_attack_range(self):
        """Keep Solo gameplay hitboxes shorter than slash sprite visuals."""
        if not self.player.is_attacking or self.player.is_counter_attacking:
            return

        tuned_range = SOLO_PLAYER_ATTACK_RANGES.get(self.player.combo_step)
        if tuned_range is not None:
            self.player.attack_range = tuned_range

    def add_energy(self, amount):
        """Clamp the Solo prototype energy resource."""
        self.energy = max(0, min(self.max_energy, self.energy + amount))

    def add_boss_energy(self, amount):
        """Clamp the Solo boss energy resource."""
        self.enemy.energy = max(0, min(self.enemy.max_energy, self.enemy.energy + amount))

    def apply_energy_from_health_changes(self, previous_player_health, previous_enemy_health):
        """Gain three times more energy for landing damage than receiving it."""
        if self.enemy.health < previous_enemy_health:
            self.add_energy(self.dealt_hit_energy_gain)
            self.add_boss_energy(self.enemy.skill_controller.hurt_energy_gain)
        if self.player.health < previous_player_health:
            self.add_energy(self.hurt_energy_gain)
            self.add_boss_energy(self.enemy.skill_controller.dealt_hit_energy_gain)

    def try_use_kamehameha(self):
        """Spend Solo energy only when Kamehameha successfully starts."""
        if self.energy < SOLO_KAMEHAMEHA_ENERGY_COST:
            return False
        if not self.skill_manager.use_slot(2, self.player):
            return False
        self.energy -= SOLO_KAMEHAMEHA_ENERGY_COST
        return True

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

    def draw_boss_energy_bar(self, screen):
        """Draw the Solo boss energy resource beneath its health bar."""
        x = WIDTH - 360
        y = 96
        width = 300
        height = 16
        fill_width = round(width * (self.enemy.energy / self.enemy.max_energy))

        pygame.draw.rect(screen, SOLO_ENERGY_BG, (x, y, width, height))
        pygame.draw.rect(screen, SOLO_BOSS_ENERGY_COLOR, (x, y, fill_width, height))
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)

        font = pygame.font.Font(None, 24)
        label = font.render(f"BOSS ENERGY {self.enemy.energy} / {self.enemy.max_energy}", True, WHITE)
        screen.blit(label, (x, y + 20))

    def draw_player_status_feedback(self, screen):
        """Draw small readable timers for temporary Solo-only control effects."""
        statuses = []
        if self.player.stun_timer > 0:
            statuses.append(("STUNNED", self.player.stun_timer, (255, 214, 115)))
        if self.player.skill_lock_timer > 0:
            statuses.append(("SKILL LOCKED", self.player.skill_lock_timer, (255, 160, 115)))

        if not statuses:
            return

        font = pygame.font.Font(None, 28)
        for index, (label, timer, color) in enumerate(statuses):
            x = 60
            y = 286 + index * 34
            width = 180
            fill_width = round(width * min(1.0, timer / 2.0))
            rendered = font.render(f"{label} {timer:.1f}s", True, color)
            screen.blit(rendered, (x, y))
            pygame.draw.rect(screen, SOLO_ENERGY_BG, (x, y + 22, width, 5))
            pygame.draw.rect(screen, color, (x, y + 22, fill_width, 5))

    def get_solo_skill_lines(self):
        """Return Solo-specific skill labels without changing Dungeon bindings."""
        kamehameha = self.skill_manager.get_slot(2)
        return [
            "Skills:",
            f"U: Combo Burst {self.combo_burst.status_text(self.energy)}",
            f"I: Kamehameha {kamehameha.status_text()} Cost {SOLO_KAMEHAMEHA_ENERGY_COST}",
            "O: Locked",
        ]

    def setup_slider_specs(self):
        """Return player and boss HP slider ranges."""
        return (
            (SOLO_SETUP_PLAYER_HP_MIN, SOLO_SETUP_PLAYER_HP_MAX, SOLO_SETUP_PLAYER_HP_STEP),
            (SOLO_SETUP_BOSS_HP_MIN, SOLO_SETUP_BOSS_HP_MAX, SOLO_SETUP_BOSS_HP_STEP),
        )

    def handle_setup_event(self, event):
        """Handle keyboard and pointer interaction for pre-fight HP sliders."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.setup_selected_slider = (self.setup_selected_slider - 1) % 2
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.setup_selected_slider = (self.setup_selected_slider + 1) % 2
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                self.adjust_setup_slider(-1)
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.adjust_setup_slider(1)
            elif event.key == pygame.K_RETURN:
                self.reset_fight()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            slider_index = slider_index_at(event.pos)
            if slider_index is not None:
                self.setup_dragging_slider = slider_index
                self.setup_selected_slider = slider_index
                self.set_setup_slider_from_pointer(slider_index, event.pos[0])
        elif event.type == pygame.MOUSEMOTION and self.setup_dragging_slider is not None:
            self.set_setup_slider_from_pointer(self.setup_dragging_slider, event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.setup_dragging_slider = None

    def adjust_setup_slider(self, direction):
        """Move the selected setup slider by one configured step."""
        specs = self.setup_slider_specs()
        minimum, maximum, step = specs[self.setup_selected_slider]
        if self.setup_selected_slider == 0:
            self.setup_player_hp = max(minimum, min(maximum, self.setup_player_hp + direction * step))
        else:
            self.setup_boss_hp = max(minimum, min(maximum, self.setup_boss_hp + direction * step))

    def set_setup_slider_from_pointer(self, slider_index, pointer_x):
        """Apply one pointer position to the selected HP slider."""
        value = value_from_slider_x(pointer_x, self.setup_slider_specs()[slider_index])
        if slider_index == 0:
            self.setup_player_hp = value
        else:
            self.setup_boss_hp = value
