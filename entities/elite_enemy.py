"""Elite melee enemy archetype for deliberate boss-room combat."""

from entities.base_enemy import BaseEnemy
from settings import ELITE_ENEMY_CONFIG
from systems.boss_skill_controller import BossSkillController


class EliteEnemy(BaseEnemy):
    """Heavy single-enemy encounter built from existing melee combat rules."""

    def __init__(self, x, y=None):
        super().__init__(x, y, ELITE_ENEMY_CONFIG)
        self.skill_controller = BossSkillController()

    def update(self, player, dt, allow_attack=True):
        """Let the skill controller temporarily own behavior when active."""
        skill_controls_boss = self.skill_controller.update(self, player, dt)
        if skill_controls_boss:
            self.update_timers(dt)
            return

        super().update(player, dt, allow_attack=allow_attack)

    def take_damage(self, amount, knockback_x=0):
        """Cancel placeholder skill flow when the boss is interrupted."""
        damage_applied = super().take_damage(amount, knockback_x)
        if damage_applied:
            self.skill_controller.cancel()
        return damage_applied

    def draw(self, surface):
        """Draw the shared enemy body plus placeholder skill readability."""
        super().draw(surface)
        self.skill_controller.draw(surface, self)
