class Interactable:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.kind = data.get("kind", "object")
        self.hitbox = tuple(data.get("hitbox", (0, 0, 0, 0)))
        self.rect = tuple(data.get("rect", self.hitbox))
        self.dialogue_id = data.get("dialogue_id")
        self.done_dialogue = data.get("done_dialogue")
        self.done_flag = data.get("done_flag")
        self.locked_dialogue = data.get("locked_dialogue")
        self.locked_dialogue_if = data.get("locked_dialogue_if") or {}
        self.leads_to = data.get("leads_to")
        self.requires = data.get("requires")
        self.inspect = data.get("inspect")
        self.sprite = data.get("sprite")
        self.hidden_unless = data.get("hidden_unless")
        self.hide_if = data.get("hide_if")
        self.reveals = data.get("reveals")
        self.gives = data.get("gives")
        self.dialogue_if = data.get("dialogue_if") or {}
        self.death = data.get("death")
        self.sfx = data.get("sfx")
        self.transition = data.get("transition")
        self.blocks = bool(data.get("blocks", False))
        self.keypad = data.get("keypad")
        self.bookshelf = data.get("bookshelf")
        self.priority = int(data.get("priority", 0))

    def is_active(self, state):
        if state is None:
            return True
        if self.hidden_unless and not state.flag(self.hidden_unless):
            return False
        if self.hide_if and state.flag(self.hide_if):
            return False
        return True

    def resolve_dialogue(self, state):
        if state is not None:
            for flag, scene_id in self.dialogue_if.items():
                if scene_id and state.flag(flag):
                    return scene_id
        return self.dialogue_id

    def resolve_locked_dialogue(self, state):
        if state is not None:
            for flag, scene_id in self.locked_dialogue_if.items():
                if scene_id and state.flag(flag):
                    return scene_id
        return self.locked_dialogue

    def contains(self, sprite):
        left, right, _bottom, _top = self.hitbox
        return left <= sprite.center_x <= right

    def contains_point(self, x, y):
        left, right, bottom, top = self.hitbox
        return left <= x <= right and bottom <= y <= top
