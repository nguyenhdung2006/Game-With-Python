"""Fast melee enemy archetype."""

from entities.base_enemy import BaseEnemy
from settings import FAST_ENEMY_CONFIG


class FastEnemy(BaseEnemy):
    """Low-health, high-speed enemy that pressures dodge and parry timing."""

    def __init__(self, x, y=None):
        super().__init__(x, y, FAST_ENEMY_CONFIG)
