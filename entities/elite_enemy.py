"""Elite melee enemy archetype for deliberate boss-room combat."""

from entities.base_enemy import BaseEnemy
from settings import ELITE_ENEMY_CONFIG


class EliteEnemy(BaseEnemy):
    """Heavy single-enemy encounter built from existing melee combat rules."""

    def __init__(self, x, y=None):
        super().__init__(x, y, ELITE_ENEMY_CONFIG)
