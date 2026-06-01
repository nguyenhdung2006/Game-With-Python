"""Small Dungeon melee enemy archetype backed by the Slime prototype strips."""

from config.enemy_config import SLIME_ENEMY_CONFIG
from entities.base_enemy import BaseEnemy


class SlimeEnemy(BaseEnemy):
    """Readable low-health Dungeon enemy using the shared melee state machine."""

    dungeon_sprite_id = "slime"

    def __init__(self, x, y=None):
        super().__init__(x, y, SLIME_ENEMY_CONFIG)
