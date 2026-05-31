"""Solo-only sprite playback and slash visual prototype."""

from pathlib import Path
import re

import pygame

from settings import ENEMY_STATE_ATTACK, ENEMY_STATE_TELEGRAPH, GROUND_Y
from systems.boss_skill_controller import BOSS_SKILL_ACTIVE, BOSS_SKILL_TELEGRAPH
from systems.combat import create_enemy_attack_hitbox
from systems.effects import (
    draw_block_guard,
    draw_dodge_overlay,
    draw_enemy_attack_rectangle,
    draw_enemy_warning,
    draw_parry_guard,
    draw_rect_afterimages,
)


PLAYER_SCALE = 0.38
PLAYER_SLASH_SCALE = 0.17
BOSS_SCALE = 0.45
BOSS_TECHNIQUE_SCALE = 0.82


class SoloSpriteRenderer:
    """Draw Solo prototype sprites while leaving shared entity renderers stable."""

    def __init__(self):
        asset_root = Path(__file__).resolve().parents[1] / "assets" / "sprites"
        self.player_frames = self.load_numbered_frames(
            asset_root / "player" / "shaman",
            "shaman_*.png",
            PLAYER_SCALE,
        )
        self.slash_frames = self.load_numbered_frames(
            asset_root / "player" / "hit",
            "frame_*.png",
            PLAYER_SLASH_SCALE,
        )
        self.boss_frames = self.load_numbered_frames(
            asset_root / "enemies" / "boss_01",
            "frame_*.png",
            BOSS_SCALE,
        )
        self.boss_technique_frames = self.load_numbered_frames(
            asset_root / "enemies" / "hit_and_technique",
            "frame_*.png",
            BOSS_TECHNIQUE_SCALE,
        )

        self.player_idle_index = 0
        self.player_idle_timer = 0.0
        self.player_idle_delay = 0.12
        self.player_attack_key = None
        self.player_attack_elapsed = 0.0
        self.slash_frame_index = 0

        self.boss_frame_index = 0
        self.boss_frame_timer = 0.0
        self.boss_frame_delay = 0.10
        self.boss_technique_index = 0
        self.boss_technique_timer = 0.0
        self.boss_technique_delay = 0.085

    def update(self, player, boss, dt):
        """Tick body and effect animation timers independently from combat."""
        self.player_idle_timer += dt
        if self.player_frames and self.player_idle_timer >= self.player_idle_delay:
            self.player_idle_timer %= self.player_idle_delay
            self.player_idle_index = (self.player_idle_index + 1) % len(self.player_frames)

        self.update_player_slash(player, dt)

        self.boss_frame_timer += dt
        if self.boss_frames and self.boss_frame_timer >= self.boss_frame_delay:
            self.boss_frame_timer %= self.boss_frame_delay
            self.boss_frame_index = (self.boss_frame_index + 1) % len(self.boss_frames)

        if self.should_draw_boss_technique(boss):
            self.boss_technique_timer += dt
            if self.boss_technique_frames and self.boss_technique_timer >= self.boss_technique_delay:
                self.boss_technique_timer %= self.boss_technique_delay
                self.boss_technique_index = (self.boss_technique_index + 1) % len(self.boss_technique_frames)
        else:
            self.boss_technique_index = 0
            self.boss_technique_timer = 0.0

    def update_player_slash(self, player, dt):
        """Map each normal combo hit onto its four matching slash frames."""
        if not player.is_attacking or player.is_counter_attacking:
            self.player_attack_key = None
            self.player_attack_elapsed = 0.0
            return

        attack_key = player.combo_step
        if attack_key != self.player_attack_key:
            self.player_attack_key = attack_key
            self.player_attack_elapsed = 0.0
        else:
            self.player_attack_elapsed += dt

        base_index = max(0, min(2, player.combo_step - 1)) * 4
        frame_duration = max(0.01, player.attack_duration / 4)
        offset = min(3, int(self.player_attack_elapsed / frame_duration))
        self.slash_frame_index = base_index + offset

    def draw_player(self, surface, player):
        """Draw the shaman prototype with slash frames and safe fallback."""
        if not self.player_frames:
            player.draw(surface)
            return

        draw_rect_afterimages(
            surface,
            player.dash_trail,
            (player.width, player.height),
            player.trail_lifetime,
            (76, 180, 255),
        )

        frame = self.player_frames[self.player_idle_index % len(self.player_frames)]
        if player.facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        frame_rect = frame.get_rect(midbottom=(player.rect.centerx, player.rect.bottom + 4))
        surface.blit(frame, frame_rect)

        self.draw_player_slash(surface, player, frame_rect)
        draw_block_guard(
            surface,
            player.rect,
            player.block_direction,
            player.is_blocking,
            player.block_flash_timer,
            player.block_color,
            player.block_flash_color,
        )
        draw_parry_guard(
            surface,
            player.rect,
            player.block_direction,
            player.is_parrying,
            player.successful_parry_timer,
            player.parry_color,
            player.parry_flash_color,
        )
        if player.is_dodging or player.dodge_invulnerability_timer > 0:
            draw_dodge_overlay(surface, frame_rect, player.dodge_color)

    def draw_player_slash(self, surface, player, frame_rect):
        """Draw a close body-adjacent slash visual separate from gameplay hitbox."""
        if not player.is_attacking or player.is_counter_attacking or not self.slash_frames:
            return

        slash_index = min(self.slash_frame_index, len(self.slash_frames) - 1)
        slash = self.slash_frames[slash_index]
        if player.combo_step >= 3:
            slash = pygame.transform.scale_by(slash, 1.12)

        if player.facing < 0:
            slash = pygame.transform.flip(slash, True, False)
            slash_rect = slash.get_rect(midright=(frame_rect.centerx - 6, frame_rect.centery + 4))
        else:
            slash_rect = slash.get_rect(midleft=(frame_rect.centerx + 6, frame_rect.centery + 4))

        surface.blit(slash, slash_rect)

    def draw_boss(self, surface, boss):
        """Draw the slightly larger boss sprite and attached technique visual."""
        if not self.boss_frames:
            boss.draw(surface)
            return

        frame = self.boss_frames[self.boss_frame_index % len(self.boss_frames)]
        if boss.facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        frame_rect = frame.get_rect(midbottom=(boss.rect.centerx, GROUND_Y))
        surface.blit(frame, frame_rect)

        self.draw_boss_technique(surface, boss, frame_rect)

        attack_hitbox = create_enemy_attack_hitbox(boss)
        if boss.state == ENEMY_STATE_TELEGRAPH:
            draw_enemy_warning(
                surface,
                attack_hitbox,
                boss.telegraph_color,
                boss.telegraph_timer,
                boss.telegraph_pulse_speed,
            )
        elif boss.state == ENEMY_STATE_ATTACK:
            draw_enemy_attack_rectangle(surface, attack_hitbox, boss.attack_color)

        boss.skill_controller.draw(surface, boss)

    def draw_boss_technique(self, surface, boss, frame_rect):
        """Attach available technique frames to existing boss attack states."""
        if not self.should_draw_boss_technique(boss) or not self.boss_technique_frames:
            return

        technique = self.boss_technique_frames[self.boss_technique_index % len(self.boss_technique_frames)]
        if boss.facing < 0:
            technique = pygame.transform.flip(technique, True, False)
            technique_rect = technique.get_rect(midright=(frame_rect.centerx - 8, frame_rect.centery + 18))
        else:
            technique_rect = technique.get_rect(midleft=(frame_rect.centerx + 8, frame_rect.centery + 18))

        surface.blit(technique, technique_rect)

    def should_draw_boss_technique(self, boss):
        """Return True for normal attack and Phase 31 skill presentation states."""
        return boss.state in {
            ENEMY_STATE_TELEGRAPH,
            ENEMY_STATE_ATTACK,
            BOSS_SKILL_TELEGRAPH,
            BOSS_SKILL_ACTIVE,
        }

    def has_player_sprite(self):
        """Return True when the shaman prototype frames loaded."""
        return bool(self.player_frames)

    def has_boss_sprite(self):
        """Return True when the boss prototype frames loaded."""
        return bool(self.boss_frames)

    def load_numbered_frames(self, directory, pattern, scale):
        """Load sorted PNG frames safely, returning an empty fallback list."""
        try:
            paths = sorted(directory.glob(pattern), key=self.extract_frame_number)
            return [self.load_scaled_image(path, scale) for path in paths]
        except (OSError, pygame.error):
            return []

    def load_scaled_image(self, path, scale):
        """Load and resize one prototype frame."""
        image = pygame.image.load(str(path)).convert_alpha()
        width = max(1, round(image.get_width() * scale))
        height = max(1, round(image.get_height() * scale))
        return pygame.transform.smoothscale(image, (width, height))

    def extract_frame_number(self, path):
        """Read the first number from a prototype sprite filename."""
        match = re.search(r"(\d+)", path.stem)
        if match is None:
            return 0
        return int(match.group(1))
