"""Solo-only automatic three-hit combo prototype."""


class SoloComboBurst:
    """Sequence the existing normal combo attacks without changing combat core."""

    def __init__(self, energy_cost=40):
        self.energy_cost = energy_cost
        self.active = False
        self.next_combo_step = 0
        self.gap_timer = 0.0
        self.gap_duration = 0.045

    def can_start(self, player, energy):
        """Return True when the player can safely begin the burst."""
        return (
            energy >= self.energy_cost
            and not self.active
            and not player.defeated
            and not player.is_hurt
            and not player.is_attacking
            and not player.is_blocking
            and not player.is_parrying
            and not player.is_dodging
            and not player.is_dashing
            and player.attack_recovery_timer <= 0
        )

    def start(self, player, energy):
        """Spend energy and open the first normal combo hit."""
        if not self.can_start(player, energy):
            return energy, False

        self.active = True
        self.next_combo_step = 2
        self.gap_timer = 0.0
        self.start_combo_step(player, 1)
        return energy - self.energy_cost, True

    def update(self, player, dt):
        """Start the next normal hit after a tiny readable gap."""
        if not self.active:
            return

        if player.defeated or player.is_hurt:
            self.cancel()
            return

        if player.is_attacking:
            return

        if self.next_combo_step > 3:
            self.cancel()
            return

        self.gap_timer += dt
        if self.gap_timer < self.gap_duration:
            return

        self.gap_timer = 0.0
        player.attack_recovery_timer = 0
        player.attack_cooldown_timer = 0
        self.start_combo_step(player, self.next_combo_step)
        self.next_combo_step += 1

    def start_combo_step(self, player, combo_step):
        """Reuse Player's existing normal combo setup for one burst hit."""
        player.queued_next_attack = False
        player.buffered_attack = False
        player.begin_combo_attack(combo_step)

    def cancel(self):
        """Stop the burst sequence without changing the current attack."""
        self.active = False
        self.next_combo_step = 0
        self.gap_timer = 0.0

    def status_text(self, energy):
        """Return a compact Solo HUD status."""
        if self.active:
            return "Active"
        if energy < self.energy_cost:
            return f"Need {self.energy_cost}"
        return "Ready"
