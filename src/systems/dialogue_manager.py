import json

from src import constants


class DialogueManager:
    def __init__(self):
        self.data = {}
        self.lines = []
        self.index = 0
        self.is_active = False

    def load_room(self, room_id):
        path = constants.DATA_DIALOGUES / f"{room_id}.json"
        if path.exists():
            self.data = json.loads(path.read_text(encoding="utf-8"))
        else:
            self.data = {}
        self.lines = []
        self.index = 0
        self.is_active = False

    def start(self, scene_id):
        lines = self.data.get(scene_id, [])
        if not lines:
            self.is_active = False
            return False
        self.lines = lines
        self.index = 0
        self.is_active = True
        return True

    def current(self):
        if not self.is_active:
            return None
        return self.lines[self.index]

    def advance(self):
        self.index += 1
        if self.index >= len(self.lines):
            self.is_active = False
            return True
        return False
