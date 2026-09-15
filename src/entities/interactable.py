class Interactable:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.kind = data.get("kind", "object")
        self.hitbox = tuple(data.get("hitbox", (0, 0, 0, 0)))
        self.rect = tuple(data.get("rect", self.hitbox))
        self.dialogue_id = data.get("dialogue_id")
        self.leads_to = data.get("leads_to")

    def contains(self, sprite):
        left, right, _bottom, _top = self.hitbox
        return left <= sprite.center_x <= right
