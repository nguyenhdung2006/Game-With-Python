"""Higher-durability Dungeon Orc variants using the shared melee behavior."""

from config.enemy_config import ORC_LEVEL_2_ENEMY_CONFIG, ORC_LEVEL_3_ENEMY_CONFIG
from entities.base_enemy import BaseEnemy


class OrcLevel2Enemy(BaseEnemy):
    """Second Orc durability tier with prototype level-two sprite strips."""

    dungeon_sprite_id = "orc2"

    def __init__(self, x, y=None):
        super().__init__(x, y, ORC_LEVEL_2_ENEMY_CONFIG)


class OrcLevel3Enemy(BaseEnemy):
    """Third Orc durability tier with prototype level-three sprite strips."""

    dungeon_sprite_id = "orc3"

    def __init__(self, x, y=None):
        super().__init__(x, y, ORC_LEVEL_3_ENEMY_CONFIG)
