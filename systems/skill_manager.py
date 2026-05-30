"""Player skill slot routing and cooldown tracking."""

from systems.skill import Skill


class SkillManager:
    """Own the three player skill slots without defining a final moveset."""

    def __init__(self, projectile_manager):
        self.projectile_manager = projectile_manager
        self.slots = [
            Skill(
                "debug_projectile",
                "Debug Projectile",
                cooldown=1.0,
                use_callback=self.use_debug_projectile,
            ),
            Skill("skill_2", "Skill 2", unlocked=False),
            Skill("skill_3", "Skill 3", unlocked=False),
        ]

    def update(self, dt):
        """Tick all slot cooldowns."""
        for skill in self.slots:
            skill.update(dt)

    def use_slot(self, slot_index, player):
        """Use a 1-based skill slot if it is available."""
        skill = self.get_slot(slot_index)
        if skill is None:
            return False

        return skill.use({"player": player})

    def get_slot(self, slot_index):
        """Return a 1-based slot entry, or None for invalid indexes."""
        index = slot_index - 1
        if index < 0 or index >= len(self.slots):
            return None
        return self.slots[index]

    def get_slot_statuses(self):
        """Return compact mechanical HUD labels for each slot."""
        statuses = []
        for index, skill in enumerate(self.slots, start=1):
            statuses.append(
                {
                    "slot": index,
                    "display_name": skill.display_name,
                    "status": skill.status_text(),
                    "unlocked": skill.unlocked,
                }
            )
        return statuses

    def use_debug_projectile(self, context):
        """Temporary foundation-only projectile hook for validation."""
        if context is None or "player" not in context:
            return False

        self.projectile_manager.spawn_debug_projectile(context["player"])
        return True
