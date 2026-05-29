"""Effect helpers re-exported from focused submodules."""

from .camera import CombatImpact
from .defense import (
    choose_flash_color,
    create_particles_placeholder,
    draw_block_guard,
    draw_dodge_overlay,
    draw_parry_guard,
)
from .slash import draw_attack_rectangle, draw_enemy_attack_rectangle, draw_enemy_warning
from .trail import create_afterimage, draw_rect_afterimages, update_timed_effects
from .ui import draw_counter_ready_glow

__all__ = [
    "CombatImpact",
    "choose_flash_color",
    "create_afterimage",
    "create_particles_placeholder",
    "draw_attack_rectangle",
    "draw_block_guard",
    "draw_counter_ready_glow",
    "draw_dodge_overlay",
    "draw_enemy_attack_rectangle",
    "draw_enemy_warning",
    "draw_parry_guard",
    "draw_rect_afterimages",
    "update_timed_effects",
]
