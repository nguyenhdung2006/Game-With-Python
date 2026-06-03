"""Presentation-only combat momentum tracking.

The tracker rewards clean strings and parries with visible feedback. It never
changes damage, cooldowns, AI, or any other gameplay rule.
"""


MOMENTUM_CHAIN_DURATION = 2.40
MOMENTUM_DECAY_PER_SECOND = 18.0
MOMENTUM_MAX_SCORE = 260.0
MOMENTUM_PULSE_DURATION = 0.22

MOMENTUM_RANKS = (
    (0, "CALM", (170, 184, 205)),
    (34, "FLOW", (130, 220, 255)),
    (78, "RUSH", (145, 236, 190)),
    (138, "SURGE", (255, 214, 115)),
    (210, "LIMIT", (255, 142, 132)),
)


class CombatMomentum:
    """Track readable combat flow without affecting simulation."""

    def __init__(self):
        self.score = 0.0
        self.chain_count = 0
        self.chain_timer = 0.0
        self.pulse_timer = 0.0
        self.last_attack_style = None
        self.last_event = "Build a clean string"

    def update(self, dt):
        """Decay presentation state after the player stops applying pressure."""
        if self.chain_timer > 0:
            self.chain_timer = max(0.0, self.chain_timer - dt)
            if self.chain_timer == 0:
                self.chain_count = 0
                self.last_attack_style = None
                self.last_event = "Keep the rhythm"
        elif self.score > 0:
            self.score = max(0.0, self.score - MOMENTUM_DECAY_PER_SECOND * dt)

        if self.pulse_timer > 0:
            self.pulse_timer = max(0.0, self.pulse_timer - dt)

    def register_hit(self, player):
        """Reward one connected melee strike, with a small variation bonus."""
        combo_step = max(1, getattr(player, "combo_step", 1))
        attack_style = getattr(player, "attack_style", "punch")
        gain = 10 + min(combo_step, 5) * 3
        if self.last_attack_style is not None and self.last_attack_style != attack_style:
            gain += 8
            self.last_event = "Style switch"
        elif combo_step >= 3:
            gain += 6
            self.last_event = "Combo pressure"
        else:
            self.last_event = "Clean hit"

        self.score = min(MOMENTUM_MAX_SCORE, self.score + gain)
        self.chain_count += 1
        self.chain_timer = MOMENTUM_CHAIN_DURATION
        self.pulse_timer = MOMENTUM_PULSE_DURATION
        self.last_attack_style = attack_style

    def register_parry(self):
        """Reward a correctly timed defensive read."""
        self.score = min(MOMENTUM_MAX_SCORE, self.score + 30)
        self.chain_count += 1
        self.chain_timer = MOMENTUM_CHAIN_DURATION
        self.pulse_timer = MOMENTUM_PULSE_DURATION
        self.last_event = "Perfect read"

    def register_damage_taken(self):
        """Break the active string after a clean enemy hit."""
        self.score *= 0.45
        self.chain_count = 0
        self.chain_timer = 0.0
        self.pulse_timer = MOMENTUM_PULSE_DURATION
        self.last_attack_style = None
        self.last_event = "Reset and retaliate"

    def current_rank(self):
        """Return the current readable rank label and accent color."""
        rank = MOMENTUM_RANKS[0]
        for candidate in MOMENTUM_RANKS:
            if self.score < candidate[0]:
                break
            rank = candidate
        return rank[1], rank[2]

    def score_ratio(self):
        """Return a clamped normalized score for HUD rendering."""
        return min(1.0, max(0.0, self.score / MOMENTUM_MAX_SCORE))
