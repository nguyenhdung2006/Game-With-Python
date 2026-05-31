"""Default keyboard bindings for the lightweight input foundation."""


# Required gameplay actions stay JSON-safe so future remapping can persist them.
# Guard, dodge, and menu routing are included to preserve existing controls.
DEFAULT_KEY_BINDINGS = {
    "move_left": "a",
    "move_right": "d",
    "jump": "w",
    "dash": "left shift",
    "attack": "j",
    "guard": "k",
    "dodge": "l",
    "skill_1": "u",
    "skill_2": "i",
    "skill_3": "o",
    "pause": "p",
    "help": "h",
    "confirm": "return",
    "back": "escape",
    "retry": "r",
    "select_solo": "1",
    "select_dungeon": "2",
    "select_team": "3",
    "select_settings": "4",
}

KEY_BINDING_LABELS = {
    "left shift": "Shift",
    "return": "Enter",
    "escape": "Esc",
}
