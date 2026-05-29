"""Lightweight pacing and pressure director for encounters."""

from settings import (
    ENCOUNTER_ATTACK_SWAP_DELAY,
    ENCOUNTER_PRESSURE_LEAD_TIME,
    ENCOUNTER_RECOVERY_TEXT_Y,
    ENCOUNTER_STATUS_Y,
    ENCOUNTER_WAVE_ACTIVATION_DELAY,
    ENCOUNTER_WAVE_BANNER_DURATION,
    ENEMY_STATE_TELEGRAPH,
    WHITE,
    WIDTH,
)
from ui.wave_banner import draw_wave_banner
import pygame


class EncounterDirector:
    """Coordinate wave intros, attack turns, and pacing-friendly downtime."""

    def __init__(self):
        self.banner_text = ""
        self.banner_timer = 0
        self.banner_duration = ENCOUNTER_WAVE_BANNER_DURATION
        self.wave_activation_timer = ENCOUNTER_WAVE_ACTIVATION_DELAY
        self.attack_swap_delay = ENCOUNTER_ATTACK_SWAP_DELAY
        self.attack_swap_timer = ENCOUNTER_ATTACK_SWAP_DELAY
        self.pressure_lead_time = ENCOUNTER_PRESSURE_LEAD_TIME
        self.pressure_candidate = None
        self.pressure_candidate_timer = 0
        self.current_attacker = None
        self.last_attacker = None
        self.recovery_active = True
        self.recovery_text = "Prepare"
        self.encounter_cleared = False

    def update(self, dt, enemies):
        """Advance banner, activation, and attack handoff timers."""
        if self.banner_timer > 0:
            self.banner_timer = max(0, self.banner_timer - dt)

        if self.wave_activation_timer > 0:
            self.wave_activation_timer = max(0, self.wave_activation_timer - dt)

        if self.attack_swap_timer > 0:
            self.attack_swap_timer = max(0, self.attack_swap_timer - dt)

        if self.pressure_candidate_timer > 0:
            self.pressure_candidate_timer = max(0, self.pressure_candidate_timer - dt)

        self.update_attacker_tracking(enemies)

    def update_attacker_tracking(self, enemies):
        """Track the currently engaged attacker and add a small handoff gap."""
        engaged_enemy = next(
            (
                enemy
                for enemy in enemies
                if not enemy.defeated and (enemy.is_attack_active() or enemy.state == ENEMY_STATE_TELEGRAPH)
            ),
            None,
        )

        if engaged_enemy is not None:
            self.current_attacker = engaged_enemy
            self.pressure_candidate = None
            self.pressure_candidate_timer = 0
            engaged_enemy.aggression_focus_timer = max(engaged_enemy.aggression_focus_timer, 0.18)
            return

        if self.current_attacker is not None:
            self.last_attacker = self.current_attacker if not self.current_attacker.defeated else None
            self.current_attacker = None
            self.attack_swap_timer = self.attack_swap_delay

    def configure_wave(self, wave_profile):
        """Load per-wave pacing values into the director."""
        self.banner_duration = wave_profile["banner_duration"]
        self.attack_swap_delay = wave_profile["attack_swap_delay"]
        self.pressure_lead_time = wave_profile["pressure_lead_time"]
        self.wave_activation_timer = wave_profile["activation_delay"]
        self.recovery_text = wave_profile["recovery_text"]

    def start_wave(self, wave_number, wave_profile):
        """Show a brief wave intro and hold enemy aggression for a moment."""
        self.configure_wave(wave_profile)
        self.banner_text = f"Wave {wave_number}"
        self.banner_timer = self.banner_duration
        self.recovery_active = False
        self.recovery_text = ""
        self.current_attacker = None
        self.last_attacker = None
        self.pressure_candidate = None
        self.pressure_candidate_timer = 0
        self.attack_swap_timer = self.wave_activation_timer * 0.4

    def start_recovery_window(self, has_next_wave):
        """Enter a short calm state between waves."""
        self.recovery_active = has_next_wave
        self.recovery_text = self.recovery_text if has_next_wave else ""
        self.current_attacker = None
        self.last_attacker = None
        self.attack_swap_timer = 0
        self.pressure_candidate = None
        self.pressure_candidate_timer = 0

    def mark_encounter_cleared(self):
        """Set final encounter state and show a clear banner."""
        self.encounter_cleared = True
        self.banner_text = "Encounter Cleared"
        self.banner_timer = self.banner_duration
        self.recovery_active = False
        self.recovery_text = ""
        self.pressure_candidate = None
        self.pressure_candidate_timer = 0

    def get_attack_leader(self, enemies, player):
        """Choose which enemy is allowed to initiate pressure next."""
        if self.wave_activation_timer > 0 or self.recovery_active:
            return None

        engaged_enemy = next(
            (
                enemy
                for enemy in enemies
                if not enemy.defeated and (enemy.is_attack_active() or enemy.state == ENEMY_STATE_TELEGRAPH)
            ),
            None,
        )
        if engaged_enemy is not None:
            return engaged_enemy

        self.cleanup_pressure_candidate()

        if self.attack_swap_timer > 0:
            return None

        alive_enemies = [enemy for enemy in enemies if not enemy.defeated]
        if not alive_enemies:
            return None

        preferred_enemies = [enemy for enemy in alive_enemies if enemy is not self.last_attacker]
        candidate_pool = preferred_enemies or alive_enemies
        selected_enemy = min(candidate_pool, key=lambda enemy: abs(enemy.rect.centerx - player.rect.centerx))

        if self.pressure_candidate is not selected_enemy:
            self.pressure_candidate = selected_enemy
            self.pressure_candidate_timer = self.pressure_lead_time
            selected_enemy.pressure_indicator_timer = max(
                selected_enemy.pressure_indicator_timer,
                self.pressure_lead_time,
            )
            return None

        if self.pressure_candidate_timer > 0:
            return None

        selected_enemy.aggression_focus_timer = max(selected_enemy.aggression_focus_timer, 0.22)
        return selected_enemy

    def cleanup_pressure_candidate(self):
        """Drop stale pressure candidates when their window has passed."""
        if self.pressure_candidate is None:
            return

        if self.pressure_candidate.defeated:
            self.pressure_candidate = None
            self.pressure_candidate_timer = 0

    def get_status_text(self, current_wave_number):
        """Return the small persistent top-of-screen status text."""
        if self.encounter_cleared:
            return "Encounter Cleared"

        if self.recovery_active and current_wave_number > 0:
            return f"Wave {current_wave_number} Clear"

        return f"Wave {max(1, current_wave_number)}"

    def draw(self, surface, current_wave_number):
        """Draw banner and lightweight pacing text."""
        draw_wave_banner(surface, self.banner_text, self.banner_timer, self.banner_duration)
        draw_status_text(surface, self.get_status_text(current_wave_number), ENCOUNTER_STATUS_Y)

        if self.recovery_active and self.recovery_text:
            draw_status_text(surface, self.recovery_text, ENCOUNTER_RECOVERY_TEXT_Y, size=34)


def draw_status_text(surface, text, center_y, size=42):
    """Draw a centered status label."""
    if not text:
        return

    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, center_y))
    surface.blit(text_surface, text_rect)
