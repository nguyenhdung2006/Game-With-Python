"""Solo-only boss energy and multi-hit combo controller."""

import pygame

from config.boss_config import SOLO_BOSS_COMBO_CONFIG
from settings import ENEMY_STATE_CHASE, ENEMY_STATE_IDLE, GROUND_Y
from systems.audio_manager import play_audio_event
from systems.boss_skill_controller import (
    ACTIVE_COLOR,
    BOSS_SKILL_ACTIVE,
    BOSS_SKILL_READY,
    BOSS_SKILL_RECOVERY,
    BOSS_SKILL_TELEGRAPH,
    WARNING_COLOR,
)
from systems.combat import apply_knockback


class SoloBossComboController:
    """Use the user-approved Solo boss combo structure without changing Dungeon."""

    def __init__(self):
        self.max_energy = SOLO_BOSS_COMBO_CONFIG["max_energy"]
        self.start_energy = SOLO_BOSS_COMBO_CONFIG["start_energy"]
        self.dealt_hit_energy_gain = SOLO_BOSS_COMBO_CONFIG["dealt_hit_energy_gain"]
        self.hurt_energy_gain = SOLO_BOSS_COMBO_CONFIG["hurt_energy_gain"]
        self.state = BOSS_SKILL_READY
        self.state_timer = 0.0
        self.cooldown_timer = SOLO_BOSS_COMBO_CONFIG["initial_cooldown"]
        self.decision_delay_timer = SOLO_BOSS_COMBO_CONFIG["decision_delay"]
        self.major_skill_spacing_timer = 0.0
        self.final_lockout_timer = 0.0
        self.skill_cooldown_timers = {
            skill_id: 0.0
            for skill_id in ("skill_1", "skill_2", "final_skill")
        }
        self.weighted_skill_cycle = tuple(
            skill_id
            for skill_id in ("skill_1", "skill_2", "final_skill")
            for _ in range(SOLO_BOSS_COMBO_CONFIG[skill_id]["weight"])
        )
        self.selection_cursor = 0
        self.last_skill_id = None
        self.repeat_count = 0
        self.skills_since_final = 0
        self.active_skill_id = None
        self.active_profile = None
        self.hit_index = 0
        self.hit_resolved = False
        self.connected_this_combo = False
        self.visual_frame_index = None

    def update(self, boss, player, dt):
        """Advance cooldowns, select an affordable combo, and resolve each hit."""
        self.cooldown_timer = max(0.0, self.cooldown_timer - dt)
        self.decision_delay_timer = max(0.0, self.decision_delay_timer - dt)
        self.major_skill_spacing_timer = max(0.0, self.major_skill_spacing_timer - dt)
        self.final_lockout_timer = max(0.0, self.final_lockout_timer - dt)
        for skill_id in self.skill_cooldown_timers:
            self.skill_cooldown_timers[skill_id] = max(0.0, self.skill_cooldown_timers[skill_id] - dt)

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
            skill_id, profile = self.choose_skill(boss, player)
            if profile is not None:
                self.start_telegraph(boss, skill_id, profile)
                return True

        return False

    def choose_skill(self, boss, player=None):
        """Pick an affordable weighted combo while enforcing anti-spam gates."""
        for offset in range(len(self.weighted_skill_cycle)):
            cycle_index = (self.selection_cursor + offset) % len(self.weighted_skill_cycle)
            skill_id = self.weighted_skill_cycle[cycle_index]
            profile = SOLO_BOSS_COMBO_CONFIG[skill_id]
            if not self.can_select_skill(skill_id, profile, boss, player):
                continue

            self.selection_cursor = (cycle_index + 1) % len(self.weighted_skill_cycle)
            return skill_id, profile
        return None, None

    def can_select_skill(self, skill_id, profile, boss, player=None):
        """Return True when one combo tier is affordable and fairly spaced."""
        if boss.energy < profile["energy_cost"]:
            return False
        if self.skill_cooldown_timers[skill_id] > 0:
            return False
        if skill_id in {"skill_2", "final_skill"} and self.major_skill_spacing_timer > 0:
            return False
        if self.last_skill_id == skill_id and self.repeat_count >= SOLO_BOSS_COMBO_CONFIG["max_repeat_count"]:
            return False
        if skill_id != "final_skill":
            return True
        if self.final_lockout_timer > 0:
            return False
        if self.skills_since_final < SOLO_BOSS_COMBO_CONFIG["final_min_prior_skills"]:
            return False
        if player is None:
            return True
        distance = abs(player.rect.centerx - boss.rect.centerx)
        return distance <= SOLO_BOSS_COMBO_CONFIG["final_range"]

    def can_start_skill(self, boss, player):
        """Start only from a fair idle/chase window within configured range."""
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
        if boss.entrance_delay_timer > 0 or boss.entrance_pause_timer > 0:
            return False

        distance = abs(player.rect.centerx - boss.rect.centerx)
        return distance <= SOLO_BOSS_COMBO_CONFIG["skill_range"]

    def start_telegraph(self, boss, skill_id, profile):
        """Spend energy and expose a readable warning before the combo."""
        boss.energy = max(0, boss.energy - profile["energy_cost"])
        self.active_skill_id = skill_id
        self.active_profile = profile
        self.hit_index = 0
        self.hit_resolved = False
        self.connected_this_combo = False
        self.visual_frame_index = profile["frames"][0]
        self.state = BOSS_SKILL_TELEGRAPH
        self.state_timer = profile["telegraph_duration"]
        self.cooldown_timer = SOLO_BOSS_COMBO_CONFIG["decision_delay"]
        self.skill_cooldown_timers[skill_id] = profile["cooldown_gate"]
        if skill_id in {"skill_2", "final_skill"}:
            self.major_skill_spacing_timer = SOLO_BOSS_COMBO_CONFIG["major_skill_spacing"]
        if skill_id == "final_skill":
            self.final_lockout_timer = SOLO_BOSS_COMBO_CONFIG["final_lockout"]
            self.skills_since_final = 0
        else:
            self.skills_since_final += 1

        if self.last_skill_id == skill_id:
            self.repeat_count += 1
        else:
            self.last_skill_id = skill_id
            self.repeat_count = 1
        boss.state = BOSS_SKILL_TELEGRAPH
        play_audio_event(boss, "boss_skill")

    def update_telegraph(self, boss, dt):
        """Open the first active combo frame after the warning."""
        self.state_timer = max(0.0, self.state_timer - dt)
        if self.state_timer == 0:
            self.state = BOSS_SKILL_ACTIVE
            self.state_timer = self.current_hit_duration()
            boss.state = BOSS_SKILL_ACTIVE

    def update_active(self, boss, player, dt):
        """Resolve one damage event per logical frame, then advance the combo."""
        if not self.hit_resolved:
            self.resolve_current_hit(boss, player)
            self.hit_resolved = True

        self.state_timer = max(0.0, self.state_timer - dt)
        if self.state_timer > 0:
            return

        self.hit_index += 1
        if self.hit_index >= len(self.active_profile["frames"]):
            self.start_recovery(boss)
            return

        self.visual_frame_index = self.active_profile["frames"][self.hit_index]
        self.hit_resolved = False
        self.state_timer = self.current_hit_duration()
        self.state_timer += self.active_profile["group_pause_after_hits"].get(self.hit_index, 0.0)

    def resolve_current_hit(self, boss, player):
        """Apply the configured frame damage while allowing connected follow-ups."""
        if not self.create_hitbox(boss).colliderect(player.rect):
            return

        if self.connected_this_combo:
            player.invulnerability_timer = 0

        damage = self.current_hit_damage()
        previous_hurt_timer = player.hurt_timer
        if not player.take_damage(damage):
            return

        self.connected_this_combo = True
        player.hurt_timer = max(player.hurt_timer, previous_hurt_timer)
        apply_knockback(player, boss.facing, SOLO_BOSS_COMBO_CONFIG["knockback"])
        if self.hit_index + 1 in self.active_profile["stun_hits"]:
            player.hurt_timer = max(player.hurt_timer, SOLO_BOSS_COMBO_CONFIG["stun_duration"])
            player.stun_timer = max(player.stun_timer, SOLO_BOSS_COMBO_CONFIG["stun_duration"])
            player.is_hurt = True
        if self.hit_index + 1 in self.active_profile["skill_lock_hits"]:
            player.skill_lock_timer = max(
                player.skill_lock_timer,
                SOLO_BOSS_COMBO_CONFIG["skill_lock_duration"],
            )

    def current_hit_damage(self):
        """Return the user-approved logical-frame damage for the active combo."""
        base_damage = SOLO_BOSS_COMBO_CONFIG["base_hit_damage"][self.hit_index % 3]
        return base_damage * self.active_profile["damage_multiplier"]

    def current_hit_duration(self):
        """Return the tuned visual window for the current logical frame."""
        return self.active_profile["hit_durations"][self.hit_index]

    def start_recovery(self, boss):
        """Expose the normal post-combo punish window."""
        self.state = BOSS_SKILL_RECOVERY
        self.state_timer = self.active_profile["recovery_duration"]
        self.visual_frame_index = None
        boss.state = BOSS_SKILL_RECOVERY
        boss.punish_window_timer = max(boss.punish_window_timer, self.state_timer)
        boss.recovery_flash_timer = max(boss.recovery_flash_timer, self.state_timer)

    def update_recovery(self, boss, dt):
        """Return control to normal melee AI after combo recovery."""
        self.state_timer = max(0.0, self.state_timer - dt)
        if self.state_timer == 0:
            self.state = BOSS_SKILL_READY
            self.decision_delay_timer = self.active_profile["post_decision_delay"]
            self.active_skill_id = None
            self.active_profile = None
            boss.state = ENEMY_STATE_IDLE

    def cancel(self):
        """Clear an interrupted Solo combo without affecting shared boss logic."""
        self.state = BOSS_SKILL_READY
        self.state_timer = 0.0
        self.decision_delay_timer = SOLO_BOSS_COMBO_CONFIG["decision_delay"]
        self.active_skill_id = None
        self.active_profile = None
        self.hit_index = 0
        self.hit_resolved = False
        self.connected_this_combo = False
        self.visual_frame_index = None

    def is_controlling(self):
        """Return True while a Solo boss combo owns behavior."""
        return self.state != BOSS_SKILL_READY

    def create_hitbox(self, boss):
        """Build one close-range combo hitbox in front of the boss."""
        skill_range = SOLO_BOSS_COMBO_CONFIG["skill_range"]
        skill_height = SOLO_BOSS_COMBO_CONFIG["skill_height"]
        if boss.facing >= 0:
            x = boss.rect.right
        else:
            x = boss.rect.left - skill_range
        return pygame.Rect(x, GROUND_Y - skill_height, skill_range, skill_height)

    def draw(self, surface, boss):
        """Reuse readable placeholder rectangles for Solo combo timing."""
        hitbox = self.create_hitbox(boss)
        if self.state == BOSS_SKILL_TELEGRAPH:
            pygame.draw.rect(surface, WARNING_COLOR, hitbox, 3)
        elif self.state == BOSS_SKILL_ACTIVE:
            pygame.draw.rect(surface, ACTIVE_COLOR, hitbox, 2)
