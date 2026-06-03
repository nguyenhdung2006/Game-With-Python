"""Solo / Versus 1v1 arena sandbox."""

import pygame

from config.boss_config import SOLO_BOSS_CONFIG
from config.mode_config import (
    SOLO_BOSS_ENERGY_COLOR,
    SOLO_DEALT_HIT_ENERGY_GAIN,
    SOLO_ENEMY_RIGHT_OFFSET,
    SOLO_ENERGY_DISC_ENERGY_COST,
    SOLO_ENERGY_BG,
    SOLO_ENERGY_COLOR,
    SOLO_HURT_ENERGY_GAIN,
    SOLO_FIGHT_CALLOUT_DURATION,
    SOLO_INTRO_ENTRY_DURATION,
    SOLO_KI_BLAST_ENERGY_COST,
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
from systems.combat_momentum import CombatMomentum
from systems.effects import CombatImpact
from systems.input_manager import InputManager
from systems.projectile_manager import ProjectileManager
from systems.skill_manager import SkillManager
from systems.solo_boss_combo_controller import SoloBossComboController
from systems.solo_sprite_renderer import SoloSpriteRenderer
from ui.combat_hud import draw_resource_bar, draw_saiyan_bar, draw_skill_bar
from ui.combat_momentum import draw_combat_momentum
from ui.completion_overlay import draw_completion_overlay
from ui.controls_overlay import draw_controls_hint, draw_controls_overlay
from ui.fonts import get_font
from ui.health_bar import draw_health_bar
from ui.pause_overlay import draw_pause_overlay
from ui.solo_setup import draw_center_text, draw_solo_setup, slider_index_at, value_from_slider_x
from world.battlefield import draw_arena


SOLO_SETUP = "SETUP"
SOLO_INTRO = "INTRO"
SOLO_ACTIVE = "ACTIVE"
SOLO_VICTORY = "VICTORY"
SOLO_DEFEAT = "DEFEAT"


class SoloMode:
    """Playable single-fight arena using the shared combat foundation."""

    def __init__(self, preferences=None, audio_manager=None, input_manager=None):
        self.preferences = preferences if preferences is not None else {}
        self.audio_manager = audio_manager
        self.input_manager = input_manager if input_manager is not None else InputManager(self.preferences)
        self.setup_player_hp = SOLO_SETUP_PLAYER_HP_MIN
        self.setup_boss_hp = SOLO_SETUP_BOSS_HP_MIN
        self.setup_selected_slider = 0
        self.setup_dragging_slider = None
        self.reset_fight(show_setup=True)

    def reset_fight(self, show_setup=False):
        """Create a clean rematch without carrying combat or cooldown state."""
        self.player = Player(SOLO_PLAYER_SPAWN_X, GROUND_Y - PLAYER_HEIGHT)
        self.player.audio_manager = self.audio_manager
        self.player.input_manager = self.input_manager
        self.combat_momentum = CombatMomentum()
        self.player.combat_momentum = self.combat_momentum
        self.player.max_health = self.setup_player_hp
        self.player.health = self.player.max_health
        self.enemy = EliteEnemy(WIDTH - SOLO_ENEMY_RIGHT_OFFSET)
        self.enemy.audio_manager = self.audio_manager
        self.configure_solo_boss()
        self.impact = CombatImpact(self.preferences)
        self.projectile_manager = ProjectileManager(self.preferences)
        self.skill_manager = SkillManager(self.projectile_manager, self.input_manager)
        self.sprite_renderer = SoloSpriteRenderer(self.preferences)
        self.max_energy = SOLO_MAX_ENERGY
        self.energy = SOLO_START_ENERGY
        self.dealt_hit_energy_gain = SOLO_DEALT_HIT_ENERGY_GAIN
        self.hurt_energy_gain = SOLO_HURT_ENERGY_GAIN
        self.paused = False
        self.controls_visible = False
        self.intro_phase = "entry"
        self.intro_timer = SOLO_INTRO_ENTRY_DURATION
        self.result_state = SOLO_SETUP if show_setup else SOLO_INTRO

    def handle_event(self, event):
        """Handle player combat inputs during the active duel."""
        if event.type == pygame.KEYDOWN:
            if self.input_manager.event_matches("help", event):
                self.controls_visible = not self.controls_visible
                return
            if self.controls_visible:
                return
            if self.input_manager.event_matches("pause", event) and self.can_pause():
                self.paused = not self.paused
                return
            if self.paused:
                if self.input_manager.event_matches("retry", event):
                    self.reset_fight()
                return

        if self.is_setup():
            self.handle_setup_event(event)
            return
        if event.type != pygame.KEYDOWN:
            return
        if self.input_manager.event_matches("retry", event) and not self.is_active():
            self.reset_fight()
            return
        if not self.is_active() or self.impact.is_hitstop_active():
            return

        if self.player.is_transforming():
            return

        if self.input_manager.event_matches("jump", event):
            self.player.jump()
        elif self.input_manager.event_matches("dash", event):
            self.player.start_dash()
        elif self.input_manager.event_matches("skill_1", event):
            self.try_use_ki_blast()
        elif self.input_manager.event_matches("skill_2", event):
            self.try_use_kamehameha()
        elif self.input_manager.event_matches("skill_3", event):
            self.try_use_energy_disc()
        elif self.input_manager.event_matches("guard", event):
            self.player.start_guard()
        elif self.input_manager.event_matches("dodge", event):
            dodge_result = self.player.start_dodge()
            if dodge_result:
                self.impact.start_hit_impact(dodge_result)
        elif self.input_manager.event_matches("attack", event):
            self.player.start_light_attack()
        elif self.input_manager.event_matches("kick", event):
            self.player.start_kick_attack()

    def update(self, keys, dt):
        """Update the 1v1 fight."""
        if self.is_gameplay_frozen():
            return

        self.impact.update(dt)
        if self.is_intro():
            self.sprite_renderer.update(
                self.player,
                self.enemy,
                dt,
                self.get_player_action_override(),
            )
            self.update_intro(dt)
            return
        if not self.is_active() or self.impact.is_hitstop_active():
            return

        self.combat_momentum.update(dt)
        previous_player_health = self.player.health
        previous_enemy_health = self.enemy.health
        self.skill_manager.update(dt)
        self.player.update(keys, dt)
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

        self.sprite_renderer.update(
            self.player,
            self.enemy,
            dt,
            self.get_player_action_override(),
        )
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
        self.sprite_renderer.draw_player(
            scene_surface,
            self.player,
            self.get_player_action_override(),
        )
        self.projectile_manager.draw(scene_surface)
        self.sprite_renderer.draw_boss(scene_surface, self.enemy)

        screen.fill((0, 0, 0))
        screen.blit(scene_surface, self.impact.get_camera_offset())
        self.draw_ui(screen)
        self.draw_intro_overlay(screen)

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
        draw_saiyan_bar(screen, self.player, y=138)
        self.draw_boss_energy_bar(screen)
        self.draw_player_status_feedback(screen)
        draw_combat_momentum(screen, self.combat_momentum)
        draw_skill_bar(
            screen,
            self.skill_manager,
            energy=self.energy,
            energy_costs={
                1: SOLO_KI_BLAST_ENERGY_COST,
                2: SOLO_KAMEHAMEHA_ENERGY_COST,
                3: SOLO_ENERGY_DISC_ENERGY_COST,
            },
        )

    def draw_result(self, screen, label):
        """Draw the end-state overlay without changing the fight underneath."""
        draw_completion_overlay(screen, label, "Rematch", self.input_manager)

    def update_result_state(self):
        """Move to the correct terminal state once a fighter is defeated."""
        if self.player.defeated:
            if self.result_state != SOLO_DEFEAT:
                self.play_sfx("defeat")
            self.result_state = SOLO_DEFEAT
        elif self.enemy.defeated:
            if self.result_state != SOLO_VICTORY:
                self.play_sfx("victory")
            self.result_state = SOLO_VICTORY

    def is_active(self):
        """Return True while the fight is still playable."""
        return self.result_state == SOLO_ACTIVE

    def is_setup(self):
        """Return True while Solo is waiting for pre-fight HP confirmation."""
        return self.result_state == SOLO_SETUP

    def is_intro(self):
        """Return True while the pre-fight presentation freezes combat."""
        return self.result_state == SOLO_INTRO

    def update_intro(self, dt):
        """Advance entry frames into the readable FIGHT callout."""
        self.intro_timer = max(0.0, self.intro_timer - dt)
        if self.intro_timer > 0:
            return
        if self.intro_phase == "entry":
            self.intro_phase = "fight"
            self.intro_timer = SOLO_FIGHT_CALLOUT_DURATION
        else:
            self.intro_phase = None
            self.result_state = SOLO_ACTIVE

    def draw_intro_overlay(self, screen):
        """Draw the short centered callout after the entry playback."""
        if self.is_intro() and self.intro_phase == "fight":
            draw_center_text(screen, "FIGHT", HEIGHT // 2, 108, WHITE)

    def get_player_action_override(self):
        """Select only user-approved presentation overrides."""
        if self.is_intro():
            return "intro_entry" if self.intro_phase == "entry" else "fight_ready"
        if self.result_state == SOLO_VICTORY:
            return "victory"
        return None

    def play_sfx(self, name):
        """Play one optional Solo event hook."""
        if self.audio_manager is not None:
            self.audio_manager.play_sfx(name)

    def can_pause(self):
        """Allow pause only while the Solo duel is actively running."""
        return self.is_active()

    def is_gameplay_frozen(self):
        """Freeze all gameplay timers while a modal QoL overlay is open."""
        return self.paused or self.controls_visible

    def draw_qol_overlays(self, screen):
        """Draw pause first so the controls panel can sit above it when requested."""
        if self.preferences.get("show_controls_hint", True) and not self.is_gameplay_frozen():
            draw_controls_hint(screen, self.input_manager)
        if self.paused:
            draw_pause_overlay(screen, "Restart Fight", self.input_manager)
        if self.controls_visible:
            draw_controls_overlay(screen, "solo", self.input_manager)

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

    def try_use_ki_blast(self):
        """Spend Solo energy only when the user-approved first skill starts."""
        if self.energy < SOLO_KI_BLAST_ENERGY_COST:
            return False
        if not self.skill_manager.use_slot(1, self.player):
            return False
        self.energy -= SOLO_KI_BLAST_ENERGY_COST
        return True

    def try_use_energy_disc(self):
        """Spend Solo energy only when the approved disc skill starts."""
        if self.energy < SOLO_ENERGY_DISC_ENERGY_COST:
            return False
        if not self.skill_manager.use_slot(3, self.player):
            return False
        self.energy -= SOLO_ENERGY_DISC_ENERGY_COST
        return True

    def draw_energy_bar(self, screen):
        """Draw a compact energy bar beneath player health."""
        draw_resource_bar(screen, 60, 96, 300, 16, self.energy, self.max_energy, "ENERGY", SOLO_ENERGY_COLOR)

    def draw_boss_energy_bar(self, screen):
        """Draw the Solo boss energy resource beneath its health bar."""
        draw_resource_bar(
            screen,
            WIDTH - 360,
            96,
            300,
            16,
            self.enemy.energy,
            self.enemy.max_energy,
            "BOSS ENERGY",
            SOLO_BOSS_ENERGY_COLOR,
            align_right=True,
        )

    def draw_player_status_feedback(self, screen):
        """Draw small readable timers for temporary Solo-only control effects."""
        statuses = []
        if self.player.stun_timer > 0:
            statuses.append(("STUNNED", self.player.stun_timer, (255, 214, 115)))
        if self.player.skill_lock_timer > 0:
            statuses.append(("SKILL LOCKED", self.player.skill_lock_timer, (255, 160, 115)))

        if not statuses:
            return

        font = get_font(28)
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
        ki_blast = self.skill_manager.get_slot(1)
        kamehameha = self.skill_manager.get_slot(2)
        energy_disc = self.skill_manager.get_slot(3)
        return [
            "Skills:",
            f"{self.input_manager.get_binding_label('skill_1')}: Ki Blast {ki_blast.status_text()} Cost {SOLO_KI_BLAST_ENERGY_COST}",
            f"{self.input_manager.get_binding_label('skill_2')}: Kamehameha {kamehameha.status_text()} Cost {SOLO_KAMEHAMEHA_ENERGY_COST}",
            f"{self.input_manager.get_binding_label('skill_3')}: Energy Disc {energy_disc.status_text()} Cost {SOLO_ENERGY_DISC_ENERGY_COST}",
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
            elif self.input_manager.event_matches("move_left", event) or event.key == pygame.K_LEFT:
                self.adjust_setup_slider(-1)
            elif self.input_manager.event_matches("move_right", event) or event.key == pygame.K_RIGHT:
                self.adjust_setup_slider(1)
            elif self.input_manager.event_matches("confirm", event):
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
