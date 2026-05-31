"""Balanced melee enemy archetype."""

from config.enemy_config import BASIC_ENEMY_CONFIG
from entities.base_enemy import BaseEnemy


class BasicEnemy(BaseEnemy):
    """Readable baseline enemy used as the standard melee archetype."""

    def __init__(self, x, y=None):
        super().__init__(x, y, BASIC_ENEMY_CONFIG)
