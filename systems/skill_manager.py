"""Player skill slot routing and cooldown tracking."""

from systems.skill import Skill


class SkillManager:
    """Own the three user-approved player skill slots."""

    def __init__(self, projectile_manager):
        self.projectile_manager = projectile_manager
        self.input_labels = ("U", "I", "O")
        self.slots = [
            Skill(
                "ki_blast",
                "Ki Blast",
                cooldown=0.45,
                use_callback=self.use_ki_blast,
            ),
            Skill(
                "kamehameha",
                "Kamehameha",
                cooldown=5.0,
                use_callback=self.use_kamehameha,
            ),
            Skill("locked", "Locked", unlocked=False),
        ]

    def update(self, dt):
        """Tick all slot cooldowns."""
        for skill in self.slots:
            skill.update(dt)

    def reset_cooldowns(self):
        """Clear transient cooldown state between independent combat screens."""
        for skill in self.slots:
            skill.current_cooldown = 0.0

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
                    "input": self.input_labels[index - 1],
                    "display_name": skill.display_name,
                    "status": skill.status_text(),
                    "unlocked": skill.unlocked,
                }
            )
        return statuses

    def use_ki_blast(self, context):
        """Fire the user-approved fast projectile skill."""
        player = self.get_context_player(context)
        if player is None or not self.can_use_player_skill(player):
            return False

        damage = round(10 * getattr(player, "damage_multiplier", 1.0))
        self.projectile_manager.spawn_ki_blast(player, damage)
        return True

    def use_kamehameha(self, context):
        """Fire the user-approved beam prototype skill."""
        player = self.get_context_player(context)
        if player is None or not self.can_use_player_skill(player, require_grounded=True):
            return False

        damage = round(34 * getattr(player, "damage_multiplier", 1.0))
        self.projectile_manager.spawn_kamehameha(player, damage)
        return True

    def get_context_player(self, context):
        """Extract the player from a skill context if available."""
        if context is None:
            return None
        return context.get("player")

    def can_use_player_skill(self, player, require_grounded=False):
        """Block skill use during unsafe non-combat player states."""
        if getattr(player, "defeated", False):
            return False
        if getattr(player, "is_hurt", False) or getattr(player, "hurt_timer", 0) > 0:
            return False
        if require_grounded and not getattr(player, "grounded", True):
            return False
        return True
