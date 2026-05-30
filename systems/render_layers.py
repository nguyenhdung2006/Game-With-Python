"""Render-layer helpers for keeping scene draw order explicit."""


def draw_combat_scene(surface, player, encounter_manager, draw_world):
    """Draw world, actors, and combat-space effects in stable back-to-front order."""
    draw_world(surface)
    player.draw(surface)
    encounter_manager.draw(surface)
