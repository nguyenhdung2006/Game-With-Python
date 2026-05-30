"""Neutral skill slot primitives for future character-defined moves."""


class Skill:
    """A cooldown-driven action entry without character fantasy attached."""

    def __init__(
        self,
        skill_id,
        display_name,
        cooldown=0.0,
        resource_cost=0,
        unlocked=True,
        use_callback=None,
    ):
        self.id = skill_id
        self.display_name = display_name
        self.cooldown = cooldown
        self.current_cooldown = 0.0
        self.resource_cost = resource_cost
        self.unlocked = unlocked
        self.use_callback = use_callback

    def can_use(self, context=None):
        """Return True when this skill is unlocked and not cooling down."""
        return self.unlocked and self.current_cooldown <= 0

    def use(self, context=None):
        """Run the skill callback and start its cooldown if it succeeds."""
        if not self.can_use(context):
            return False

        if self.use_callback is not None and not self.use_callback(context):
            return False

        self.current_cooldown = self.cooldown
        return True

    def update(self, dt):
        """Tick cooldown toward ready."""
        if self.current_cooldown > 0:
            self.current_cooldown = max(0.0, self.current_cooldown - dt)

    def status_text(self):
        """Return a compact HUD status label."""
        if not self.unlocked:
            return "Locked"
        if self.current_cooldown <= 0:
            return "Ready"
        return f"{self.current_cooldown:.1f}s"
