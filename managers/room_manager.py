"""Fixed dungeon room progression manager."""

from dataclasses import dataclass

from managers.room_state import (
    ROOM_ACTIVE,
    ROOM_BOSS_ENCOUNTER,
    ROOM_CLEARED,
    ROOM_COMPLETE,
    ROOM_DEFEAT,
    ROOM_DUNGEON_CLEAR,
    ROOM_ENCOUNTER,
    ROOM_REWARD,
)


@dataclass(frozen=True)
class DungeonRoom:
    """One fixed room entry in the current dungeon sequence."""

    room_type: str


class RoomManager:
    """Track fixed dungeon room flow without owning combat or rendering."""

    def __init__(self):
        self.rooms = [
            DungeonRoom(ROOM_ENCOUNTER),
            DungeonRoom(ROOM_ENCOUNTER),
            DungeonRoom(ROOM_BOSS_ENCOUNTER),
        ]
        self.current_room_index = 0
        self.flow_state = ROOM_ACTIVE

    def current_room(self):
        """Return the active room, or None after dungeon completion."""
        if self.is_dungeon_complete():
            return None
        return self.rooms[self.current_room_index]

    def current_room_type(self):
        """Return the current room type or the final clear marker."""
        room = self.current_room()
        if room is None:
            return ROOM_DUNGEON_CLEAR
        return room.room_type

    def room_number(self):
        """Return the 1-based room number for UI."""
        return min(self.current_room_index + 1, self.total_rooms())

    def total_rooms(self):
        """Return total fixed dungeon rooms."""
        return len(self.rooms)

    def cleared_room_count(self):
        """Return how many rooms are cleared for run summary UI."""
        if self.is_dungeon_complete():
            return self.total_rooms()
        if self.is_room_cleared() or self.is_reward_active():
            return self.current_room_index + 1
        return self.current_room_index

    def is_final_room(self):
        """Return True when the current room is the last fixed room."""
        return self.current_room_index >= self.total_rooms() - 1

    def is_room_active(self):
        """Return True while the current room is still running."""
        return self.flow_state == ROOM_ACTIVE

    def is_room_cleared(self):
        """Return True while waiting for player confirmation after a clear."""
        return self.flow_state == ROOM_CLEARED

    def is_reward_active(self):
        """Return True while the player is choosing a room reward."""
        return self.flow_state == ROOM_REWARD

    def is_dungeon_complete(self):
        """Return True after all rooms are finished."""
        return self.flow_state == ROOM_COMPLETE

    def is_dungeon_defeated(self):
        """Return True after the player has been defeated during a run."""
        return self.flow_state == ROOM_DEFEAT

    def is_run_finished(self):
        """Return True while the run is in a terminal state."""
        return self.is_dungeon_complete() or self.is_dungeon_defeated()

    def mark_room_cleared(self):
        """Freeze room progress until the player continues."""
        if not self.is_run_finished():
            self.flow_state = ROOM_CLEARED

    def start_reward(self):
        """Move from room clear into reward selection."""
        if self.is_room_cleared():
            self.flow_state = ROOM_REWARD

    def mark_dungeon_defeated(self):
        """Stop room progression after the player is defeated."""
        if not self.is_dungeon_complete():
            self.flow_state = ROOM_DEFEAT

    def advance_room(self):
        """Advance to the next room, or mark the dungeon complete."""
        if self.is_run_finished():
            return

        if self.is_final_room():
            self.flow_state = ROOM_COMPLETE
            return

        self.current_room_index += 1
        self.flow_state = ROOM_ACTIVE
