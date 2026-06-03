"""Fixed dungeon room layout data access."""

from dataclasses import dataclass

from config.dungeon_layout_config import DUNGEON_CLEAR_LAYOUT, DUNGEON_ROOM_LAYOUTS


@dataclass(frozen=True)
class DungeonLayout:
    """One fixed room layout with explicit identity, bounds, and spawn anchors."""

    layout_id: str
    label: str
    title: str
    subtitle: str
    layout_type: str
    room_type: str
    room_bounds: tuple
    arena_bounds: tuple
    player_spawn: tuple
    enemy_spawn_points_right: tuple
    enemy_spawn_points_left: tuple
    exit_position: tuple | None
    torch_positions: tuple
    decor_props: tuple

    def enemy_spawn_points_for_player(self, player_center_x):
        """Return configured spawn anchors on the side away from the player."""
        arena_left, arena_right = self.arena_bounds
        if player_center_x < (arena_left + arena_right) / 2:
            return self.enemy_spawn_points_right
        return self.enemy_spawn_points_left


class DungeonLayoutManager:
    """Own the current fixed-layout catalog without procedural generation."""

    def __init__(self):
        self.room_layouts = tuple(self.create_layout(data) for data in DUNGEON_ROOM_LAYOUTS)
        self.clear_layout = self.create_layout(DUNGEON_CLEAR_LAYOUT)

    def create_layout(self, data):
        """Convert one config dictionary into an immutable layout object."""
        return DungeonLayout(**data)

    def layout_for_room_index(self, room_index):
        """Return one combat-room layout by progression index."""
        return self.room_layouts[room_index]

    def total_room_layouts(self):
        """Return the number of fixed combat layouts."""
        return len(self.room_layouts)
