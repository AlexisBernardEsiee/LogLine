import json

import arcade

from src import constants
from src.entities.interactable import Interactable


class RoomManager:
    def __init__(self):
        self.named_scenes = {}
        if constants.DATA_SCENES.exists():
            self.named_scenes = json.loads(constants.DATA_SCENES.read_text(encoding="utf-8"))

        self.current_room_id = None
        self.name = ""
        self.entry_x = 220
        self.entry_facing_right = True
        self.floor_y = 168
        self.on_enter = None
        self.tutorial = False
        self.background = None
        self.layers = []
        self.interactables = []
        self._visited = set()
        self._textures = {}
        self._override = None

    @property
    def shows_world(self):
        return self._override is None

    def show(self, room_id, from_room_id=None):
        path = constants.DATA_ROOMS / f"{room_id}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        self.current_room_id = room_id
        self.name = data.get("name", room_id)
        self.entry_x, self.entry_facing_right = self._entry_from(data, from_room_id)
        self.floor_y = data.get("floor_y", 168)
        self.on_enter = data.get("on_enter")
        self.tutorial = bool(data.get("tutorial", False))
        self.background = data.get("background")
        self.layers = data.get("layers", [])
        self.interactables = [Interactable(item) for item in data.get("interactables", [])]
        self._override = None

    def consume_on_enter(self):
        room_id = self.current_room_id
        if room_id is None or room_id in self._visited:
            return None
        self._visited.add(room_id)
        return self.on_enter

    def set_scene(self, scene):
        if scene in (None, constants.SCENE_ROOM):
            self._override = None
            return
        spec = self.named_scenes.get(scene, scene)
        if isinstance(spec, str):
            spec = {"type": "image", "path": spec}
        scene_type = spec.get("type", "image")
        if scene_type == "room":
            self._override = None
        elif scene_type == "color":
            self._override = ("color", tuple(spec["color"]))
        else:
            self._override = ("image", self._texture(spec["path"]))

    def current_background_texture(self):
        if self._override is not None:
            kind, value = self._override
            return value if kind == "image" else None
        if not self.background:
            return None
        spec = self.named_scenes.get(self.background, self.background)
        if isinstance(spec, str):
            return self._texture(spec)
        if isinstance(spec, dict) and spec.get("type") == "image":
            return self._texture(spec["path"])
        return None

    def get_nearby_interactable(self, player):
        if player is None or not self.shows_world:
            return None
        for item in self.interactables:
            if item.contains(player):
                return item
        return None

    def draw(self):
        if self._override is not None:
            kind, value = self._override
            if kind == "color":
                self._fill(value)
            else:
                self._draw_texture(value)
            return

        if self.background:
            spec = self.named_scenes.get(self.background, self.background)
            if isinstance(spec, str):
                self._draw_texture(self._texture(spec))
            elif spec.get("type") == "color":
                self._fill(tuple(spec["color"]))
            elif spec.get("type") == "image":
                self._draw_texture(self._texture(spec["path"]))
        else:
            for layer in self.layers:
                arcade.draw_lrbt_rectangle_filled(
                    layer["left"],
                    layer["right"],
                    layer["bottom"],
                    layer["top"],
                    tuple(layer["color"]),
                )
            for item in self.interactables:
                self._draw_item(item)

    def _entry_from(self, data, from_room_id):
        default_x = data.get("entry_x", 220)
        entry = data.get("entries", {}).get(from_room_id) if from_room_id else None
        if isinstance(entry, dict):
            x = entry.get("x", default_x)
            facing = entry.get("facing")
            facing_right = facing != "left" if facing else x < constants.BASE_WIDTH / 2
            return x, facing_right
        if entry is not None:
            x = entry
            return x, x < constants.BASE_WIDTH / 2
        return default_x, True

    def _fill(self, color):
        arcade.draw_lrbt_rectangle_filled(
            0, constants.SCREEN_WIDTH, 0, constants.SCREEN_HEIGHT, color
        )

    def _draw_texture(self, texture):
        arcade.draw_texture_rect(
            texture,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
        )

    def _texture(self, relative_path):
        if relative_path not in self._textures:
            full_path = constants.PROJECT_ROOT / relative_path
            if not full_path.exists():
                raise FileNotFoundError(f"Image introuvable : {full_path}")
            self._textures[relative_path] = arcade.load_texture(str(full_path))
        return self._textures[relative_path]

    def _draw_item(self, item):
        left, right, bottom, top = item.rect
        if item.kind == "photo":
            arcade.draw_lrbt_rectangle_filled(left - 10, right + 10, bottom - 10, top + 10, (92, 68, 46))
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (186, 176, 158))
            arcade.draw_lrbt_rectangle_filled(left + 18, right - 18, bottom + 24, top - 24, (120, 108, 96))
        elif item.kind == "door":
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (74, 50, 36))
            arcade.draw_lrbt_rectangle_filled(left + 12, right - 12, bottom + 8, top - 8, (58, 38, 28))
            arcade.draw_circle_filled(left + 22, (bottom + top) / 2, 7, (212, 186, 92))
