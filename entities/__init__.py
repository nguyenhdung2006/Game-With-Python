"""Entity classes such as the player, enemy archetypes, bosses, and projectiles."""

from .basic_enemy import BasicEnemy
from .fast_enemy import FastEnemy
from .player import Player

__all__ = ["Player", "BasicEnemy", "FastEnemy"]
