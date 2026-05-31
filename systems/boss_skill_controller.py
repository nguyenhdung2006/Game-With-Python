"""Neutral boss skill AI foundation for elite encounters."""

import pygame

from settings import ENEMY_STATE_CHASE, ENEMY_STATE_IDLE, GROUND_Y
from systems.combat import apply_knockback


BOSS_SKILL_READY = "READY"
BOSS_SKILL_TELEGRAPH = "SKILL_TELEGRAPH"
BOSS_SKILL_ACTIVE = "SKILL_ACTIVE"
BOSS_SKILL_RECOVERY = "SKILL_RECOVERY"

WARNING_COLOR = (255, 224, 150)
ACTIVE_COLOR = (225, 105, 92)


class BossSkillController:
    """Manage a readable mechanical placeholder skill for the elite boss."""

    def __init__(self):
        self.state = BOSS_SKILL_READY
        self.state_timer = 0.0
        self.cooldown = 6.5
        self.cooldown_timer = 3.5
        self.decision_delay_timer = 2.0
        self.telegraph_duration = 0.82
        self.active_duration = 0.18
        self.recovery_duration = 0.82
        self.skill_range = 220
        self.skill_height = 42
        self.damage = 20
        self.knockback = 320
        self.has_hit_this_use = False

    def update(self, boss, player, dt):
        """Tick cooldowns, advance skill states, and start fair skill uses."""
        self.cooldown_timer = max(0.0, self.cooldown_timer - dt)
        self.decision_delay_timer = max(0.0, self.decision_delay_timer - dt)

        if boss.defeated:
            self.cancel()
            return False

        if self.state == BOSS_SKILL_TELEGRAPH:
            self.update_telegraph(boss, dt)
            return True
        if self.state == BOSS_SKILL_ACTIVE:
            self.update_active(boss, player, dt)
            return True
        if self.state == BOSS_SKILL_RECOVERY:
            self.update_recovery(boss, dt)
            return True

        if self.can_start_skill(boss, player):
            self.start_telegraph(boss)
            return True

        return False

    def can_start_skill(self, boss, player):
        """Return True only when a readable skill use is fair to begin."""
        if self.cooldown_timer > 0 or self.decision_delay_timer > 0:
            return False
        if boss.state not in {ENEMY_STATE_IDLE, ENEMY_STATE_CHASE}:
            return False
        if boss.hurt_reaction_timer > 0 or boss.stagger_timer > 0:
            return False
        if boss.retreat_timer > 0 or boss.recovery_timer > 0:
            return False
        if boss.attack_timer > 0 or boss.telegraph_timer > 0:
            return False
        if boss.attack_cooldown_timer > 0:
            return False
        if boss.entrance_delay_timer > 0 or boss.entrance_pause_timer > 0:
            return False

        distance = abs(player.rect.centerx - boss.rect.centerx)
        return distance <= self.skill_range + 70

    def start_telegraph(self, boss):
        """Open the avoidable warning window before the placeholder skill."""
        self.state = BOSS_SKILL_TELEGRAPH
        self.state_timer = self.telegraph_duration
        self.cooldown_timer = self.cooldown
        self.has_hit_this_use = False
        boss.state = BOSS_SKILL_TELEGRAPH

    def update_telegraph(self, boss, dt):
        """Advance from warning into the short active hitbox."""
        self.state_timer = max(0.0, self.state_timer - dt)
        if self.state_timer == 0:
            self.state = BOSS_SKILL_ACTIVE
            self.state_timer = self.active_duration
            boss.state = BOSS_SKILL_ACTIVE

    def update_active(self, boss, player, dt):
        """Damage the player once if the active ground hitbox connects."""
        hitbox = self.create_hitbox(boss)
        if not self.has_hit_this_use and hitbox.colliderect(player.rect):
            if player.take_damage(self.damage):
                apply_knockback(player, boss.facing, self.knockback)
                self.has_hit_this_use = True

        self.state_timer = max(0.0, self.state_timer - dt)
        if self.state_timer == 0:
            self.start_recovery(boss)

    def start_recovery(self, boss):
        """Expose a clear punish window after the skill commits."""
        self.state = BOSS_SKILL_RECOVERY
        self.state_timer = self.recovery_duration
        boss.state = BOSS_SKILL_RECOVERY
        boss.punish_window_timer = max(boss.punish_window_timer, self.recovery_duration)
        boss.recovery_flash_timer = max(boss.recovery_flash_timer, self.recovery_duration)

    def update_recovery(self, boss, dt):
        """Return control to normal melee AI after recovery."""
        self.state_timer = max(0.0, self.state_timer - dt)
        if self.state_timer == 0:
            self.state = BOSS_SKILL_READY
            self.decision_delay_timer = 1.25
            boss.state = ENEMY_STATE_IDLE

    def cancel(self):
        """Clear an in-progress placeholder skill after interruption."""
        self.state = BOSS_SKILL_READY
        self.state_timer = 0.0
        self.decision_delay_timer = max(self.decision_delay_timer, 1.0)
        self.has_hit_this_use = False

    def is_controlling(self):
        """Return True while the placeholder skill owns boss behavior."""
        return self.state != BOSS_SKILL_READY

    def create_hitbox(self, boss):
        """Build the short-range ground rectangle in front of the boss."""
        if boss.facing >= 0:
            x = boss.rect.right
        else:
            x = boss.rect.left - self.skill_range

        return pygame.Rect(x, GROUND_Y - self.skill_height, self.skill_range, self.skill_height)

    def draw(self, surface, boss):
        """Draw a warning outline or active placeholder rectangle."""
        hitbox = self.create_hitbox(boss)
        if self.state == BOSS_SKILL_TELEGRAPH:
            pygame.draw.rect(surface, WARNING_COLOR, hitbox, 3)
        elif self.state == BOSS_SKILL_ACTIVE:
            pygame.draw.rect(surface, ACTIVE_COLOR, hitbox)
            pygame.draw.rect(surface, WARNING_COLOR, hitbox, 2)
