"""Render-layer helpers for keeping scene draw order explicit."""


def draw_combat_scene(surface, player, encounter_manager, draw_world, projectile_manager=None):
    """Draw world, actors, and combat-space effects in stable back-to-front order."""
    draw_world(surface)
    player.draw(surface)
    if projectile_manager is not None:
        projectile_manager.draw(surface)
    encounter_manager.draw(surface)
