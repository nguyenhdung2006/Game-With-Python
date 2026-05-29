"""Balanced melee enemy archetype."""

from entities.base_enemy import BaseEnemy
from settings import BASIC_ENEMY_CONFIG


class BasicEnemy(BaseEnemy):
    """Readable baseline enemy used as the standard melee archetype."""

    def __init__(self, x, y=None):
        super().__init__(x, y, BASIC_ENEMY_CONFIG)
