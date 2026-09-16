class Interactable:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.kind = data.get("kind", "object")
        self.hitbox = tuple(data.get("hitbox", (0, 0, 0, 0)))
        self.rect = tuple(data.get("rect", self.hitbox))
        self.dialogue_id = data.get("dialogue_id")
        self.done_dialogue = data.get("done_dialogue")
        self.locked_dialogue = data.get("locked_dialogue")
        self.leads_to = data.get("leads_to")
        self.requires = data.get("requires")
        self.inspect = data.get("inspect")
        self.sprite = data.get("sprite")
        self.hidden_unless = data.get("hidden_unless")
        self.hide_if = data.get("hide_if")
        self.reveals = data.get("reveals")
        self.gives = data.get("gives")
        self.death = data.get("death")
        self.sfx = data.get("sfx")
        self.priority = int(data.get("priority", 0))

    def is_active(self, state):
        if state is None:
            return True
        if self.hidden_unless and not state.flag(self.hidden_unless):
            return False
        if self.hide_if and state.flag(self.hide_if):
            return False
        return True

    def contains(self, sprite):
        left, right, _bottom, _top = self.hitbox
        return left <= sprite.center_x <= right

    def contains_point(self, x, y):
        left, right, bottom, top = self.hitbox
        return left <= x <= right and bottom <= y <= top
