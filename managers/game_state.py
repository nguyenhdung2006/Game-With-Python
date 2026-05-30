"""Game-level screen routing for mode selection and playable modes."""


MODE_SELECT = "MODE_SELECT"
DUNGEON_MODE = "DUNGEON_MODE"
SOLO_MODE = "SOLO_MODE"
TEAM_MODE_LOCKED = "TEAM_MODE_LOCKED"


class GameState:
    """Track the active top-level screen without owning mode internals."""

    def __init__(self):
        self.current = MODE_SELECT

    def enter_mode_select(self):
        self.current = MODE_SELECT

    def enter_dungeon_mode(self):
        self.current = DUNGEON_MODE

    def enter_solo_mode(self):
        self.current = SOLO_MODE

    def enter_team_mode_locked(self):
        self.current = TEAM_MODE_LOCKED

    def is_mode_select(self):
        return self.current == MODE_SELECT

    def is_dungeon_mode(self):
        return self.current == DUNGEON_MODE

    def is_placeholder_screen(self):
        return self.current in {SOLO_MODE, TEAM_MODE_LOCKED}
