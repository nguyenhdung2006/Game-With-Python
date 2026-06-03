"""Player skill slot routing and cooldown tracking."""

from config.goku_sprite_config import GOKU_KI_BLAST_ACTION_IDS
from config.skill_config import ENERGY_DISC_CONFIG, KAMEHAMEHA_CONFIG, KI_BLAST_CONFIG
from systems.skill import Skill
from systems.super_saiyan import get_outgoing_damage_multiplier


class SkillManager:
    """Own the three user-approved player skill slots."""

    def __init__(self, projectile_manager, input_manager=None):
        self.projectile_manager = projectile_manager
        self.input_manager = input_manager
        self.input_labels = ("U", "I", "O")
        self.slots = [
            Skill(
                "ki_blast",
                "Ki Blast",
                cooldown=KI_BLAST_CONFIG["cooldown"],
                use_callback=self.use_ki_blast,
            ),
            Skill(
                "kamehameha",
                "Kamehameha",
                cooldown=KAMEHAMEHA_CONFIG["cooldown"],
                use_callback=self.use_kamehameha,
            ),
            Skill(
                "energy_disc",
                "Energy Disc",
                cooldown=ENERGY_DISC_CONFIG["cooldown"],
                use_callback=self.use_energy_disc,
            ),
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

        used = skill.use({"player": player})
        if used:
            skill.current_cooldown *= getattr(player, "skill_cooldown_multiplier", 1.0)
        return used

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
                    "input": self.get_input_label(index),
                    "display_name": skill.display_name,
                    "status": skill.status_text(),
                    "unlocked": skill.unlocked,
                }
            )
        return statuses

    def get_input_label(self, slot_index):
        """Return one configured skill binding label with legacy fallback."""
        if self.input_manager is None:
            return self.input_labels[slot_index - 1]
        return self.input_manager.get_binding_label(f"skill_{slot_index}")

    def use_ki_blast(self, context):
        """Fire the user-approved fast projectile skill."""
        player = self.get_context_player(context)
        if player is None or not self.can_use_player_skill(player):
            return False

        damage = round(
            KI_BLAST_CONFIG["damage"]
            * get_outgoing_damage_multiplier(player)
            * getattr(player, "skill_damage_multiplier", 1.0)
        )
        self.projectile_manager.spawn_ki_blast(player, damage)
        visual_index = getattr(player, "ki_blast_visual_index", 0)
        player.skill_visual_state = GOKU_KI_BLAST_ACTION_IDS[
            visual_index % len(GOKU_KI_BLAST_ACTION_IDS)
        ]
        player.ki_blast_visual_index = visual_index + 1
        player.skill_visual_timer = KI_BLAST_CONFIG["visual_duration"]
        return True

    def use_kamehameha(self, context):
        """Fire the user-approved beam prototype skill."""
        player = self.get_context_player(context)
        if player is None or not self.can_use_player_skill(player, require_grounded=True):
            return False

        damage = round(
            KAMEHAMEHA_CONFIG["damage"]
            * get_outgoing_damage_multiplier(player)
            * getattr(player, "skill_damage_multiplier", 1.0)
        )
        self.projectile_manager.spawn_kamehameha(player, damage)
        player.skill_visual_state = (
            "super_saiyan_skill_2"
            if getattr(player, "is_super_saiyan", False)
            else "skill_2"
        )
        player.skill_visual_timer = KAMEHAMEHA_CONFIG["visual_duration"]
        return True

    def use_energy_disc(self, context):
        """Fire the approved animated disc projectile skill."""
        player = self.get_context_player(context)
        if player is None or not self.can_use_player_skill(player):
            return False

        damage = round(
            ENERGY_DISC_CONFIG["damage"]
            * get_outgoing_damage_multiplier(player)
            * getattr(player, "skill_damage_multiplier", 1.0)
        )
        self.projectile_manager.spawn_energy_disc(player, damage)
        player.skill_visual_state = "skill_3"
        player.skill_visual_timer = ENERGY_DISC_CONFIG["visual_duration"]
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
        if getattr(player, "skill_lock_timer", 0) > 0:
            return False
        if getattr(player, "is_transforming", lambda: False)():
            return False
        if require_grounded and not getattr(player, "grounded", True):
            return False
        return True
