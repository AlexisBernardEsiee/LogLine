import json

from src import constants

DEFAULT_FLAGS = {
    "has_key": False,
    "key_revealed": False,
    "seen_corridor_intro": False,
    "seen_house_thought": False,
    "seen_bar_intro": False,
    "seen_bedroom_intro": False,
    "died_poison": False,
    "died_glass": False,
    "died_lustre": False,
    "seen_bookmark": False,
    "seen_letters": False,
    "seen_office_intro": False,
    "seen_void_reveal": False,
    "seen_library_intro": False,
    "seen_catalogue": False,
    "seen_blank_book": False,
    "library_door_open": False,
    "tutorial_done": False,
    "death_count": 0,
}


class GameState:
    def __init__(self):
        self.room_id = constants.ROOM_CORRIDOR
        self.from_room_id = None
        self.flags = dict(DEFAULT_FLAGS)

    def flag(self, name):
        return bool(self.flags.get(name, False))

    def set_flag(self, name, value=True, save=True):
        self.flags[name] = value
        if save:
            self.save()

    def bump_death(self):
        self.flags["death_count"] = int(self.flags.get("death_count", 0)) + 1
        self.save()

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "from_room_id": self.from_room_id,
            "flags": dict(self.flags),
        }

    def save(self):
        path = constants.SAVE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls):
        state = cls()
        path = constants.SAVE_PATH
        if not path.exists():
            return state
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return state
        state.room_id = data.get("room_id", constants.ROOM_CORRIDOR)
        state.from_room_id = data.get("from_room_id")
        flags = data.get("flags", {})
        state.flags = dict(DEFAULT_FLAGS)
        state.flags.update(flags)
        return state

    @classmethod
    def exists(cls):
        return constants.SAVE_PATH.exists()

    @classmethod
    def clear(cls):
        path = constants.SAVE_PATH
        if path.exists():
            path.unlink()
