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

    def has_choices(self):
        line = self.current()
        return bool(line and line.get("choices"))

    def get_choices(self):
        line = self.current()
        if not line:
            return []
        return line.get("choices", [])

    def choose(self, choice_index):
        choices = self.get_choices()
        if not 0 <= choice_index < len(choices):
            return False
        next_scene = choices[choice_index].get("next")
        if not next_scene:
            self.is_active = False
            return True
        return self.start(next_scene)

    def advance(self):
        self.index += 1
        if self.index >= len(self.lines):
            self.is_active = False
            return True
        return False