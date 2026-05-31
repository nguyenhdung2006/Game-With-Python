"""Shared runtime settings and compatibility exports.

Gameplay tuning now lives in ``config/``. Re-exporting those values keeps the
existing modules stable while each area moves toward explicit config imports.
"""

from config.boss_config import *  # noqa: F403
from config.enemy_config import *  # noqa: F403
from config.mode_config import *  # noqa: F403
from config.player_config import *  # noqa: F403

# Window and world geometry
WIDTH = 1280
HEIGHT = 720
FPS = 60
GROUND_Y = 540

# Basic colors used by the arena and HUD.
SKY_TOP = (12, 14, 26)
SKY_BOTTOM = (42, 36, 48)
GROUND = (70, 62, 58)
GROUND_DARK = (34, 31, 32)
CRACK = (18, 18, 22)
PLAYER_COLOR = (76, 180, 255)
ENEMY_COLOR = (225, 70, 74)
ENEMY_HURT_COLOR = (255, 235, 235)
ENEMY_DEFEATED_COLOR = (80, 45, 48)
HEALTH_BG = (35, 35, 40)
HEALTH_PLAYER = (60, 220, 120)
HEALTH_ENEMY = (230, 60, 70)
WHITE = (235, 235, 240)
