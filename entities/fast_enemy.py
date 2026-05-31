"""Fast melee enemy archetype."""

from config.enemy_config import FAST_ENEMY_CONFIG
from entities.base_enemy import BaseEnemy


class FastEnemy(BaseEnemy):
    """Low-health, high-speed enemy that pressures dodge and parry timing."""

    def __init__(self, x, y=None):
        super().__init__(x, y, FAST_ENEMY_CONFIG)
