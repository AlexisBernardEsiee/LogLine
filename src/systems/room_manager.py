import json

import arcade
from PIL import Image

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
        self.on_enter_flag = None
        self.tutorial = False
        self.background = None
        self.background_if = {}
        self.auto_deaths = []
        self.lustre_prop = None
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
        self.on_enter_flag = data.get("on_enter_flag")
        self.tutorial = bool(data.get("tutorial", False))
        self.background = data.get("background")
        self.background_if = data.get("background_if", {})
        self.auto_deaths = data.get("auto_deaths", [])
        self.lustre_prop = data.get("lustre_prop")
        self.layers = data.get("layers", [])
        self.interactables = [Interactable(item) for item in data.get("interactables", [])]
        self._override = None

    def consume_on_enter(self, state=None):
        if not self.on_enter:
            return None
        if state is not None and self.on_enter_flag:
            if state.flag(self.on_enter_flag):
                return None
            state.set_flag(self.on_enter_flag)
            return self.on_enter
        room_id = self.current_room_id
        if room_id is None or room_id in self._visited:
            return None
        self._visited.add(room_id)
        return self.on_enter

    def active_interactables(self, state=None):
        return [item for item in self.interactables if item.is_active(state)]

    def get_nearby_interactable(self, player, state=None):
        if player is None or not self.shows_world:
            return None
        matches = [item for item in self.active_interactables(state) if item.contains(player)]
        if not matches:
            return None
        return max(matches, key=lambda item: item.priority)

    def get_interactable_at(self, x, y, state=None):
        if not self.shows_world:
            return None
        matches = [
            item for item in self.active_interactables(state) if item.contains_point(x, y)
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: item.priority)

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

    def resolved_background(self, state=None):
        if state is not None:
            for flag, name in self.background_if.items():
                if state.flag(flag):
                    return name
        return self.background

    def _background_spec(self, state=None):
        background = self.resolved_background(state)
        if not background:
            return None
        return self.named_scenes.get(background, background)

    def _texture_from_spec(self, spec):
        if spec is None:
            return None
        if isinstance(spec, str):
            return self._texture(spec)
        if isinstance(spec, dict) and spec.get("type") == "image":
            return self._texture(spec["path"])
        return None

    def current_background_texture(self, state=None):
        if self._override is not None:
            kind, value = self._override
            return value if kind == "image" else None
        return self._texture_from_spec(self._background_spec(state))

    def _room_background_texture(self, state=None):
        return self._texture_from_spec(self._background_spec(state))

    def draw(self, state=None):
        if self._override is not None:
            kind, value = self._override
            if kind == "color":
                self._fill(value)
            else:
                self._draw_texture(value)
                if value is self._room_background_texture(state):
                    self._draw_overlays(state)
            return

        spec = self._background_spec(state)
        if spec:
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
        self._draw_overlays(state)

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

    def _overlay_texture(self, relative_path):
        key = f"overlay:{relative_path}"
        if key not in self._textures:
            full_path = constants.PROJECT_ROOT / relative_path
            if not full_path.exists():
                raise FileNotFoundError(f"Image introuvable : {full_path}")
            image = Image.open(full_path).convert("RGBA")
            bbox = image.getbbox()
            if bbox:
                image = image.crop(bbox)
            self._textures[key] = arcade.Texture(image, hash=key)
        return self._textures[key]

    def _draw_overlays(self, state=None):
        for item in self.active_interactables(state):
            if not item.sprite:
                continue
            texture = self._overlay_texture(item.sprite)
            left, right, bottom, top = self._fit_overlay_rect(item.rect, texture)
            arcade.draw_texture_rect(texture, arcade.LRBT(left, right, bottom, top))

    @staticmethod
    def _fit_overlay_rect(rect, texture):
        left, right, bottom, top = rect
        box_w = max(right - left, 1)
        box_h = max(top - bottom, 1)
        image_aspect = texture.width / max(texture.height, 1)
        box_aspect = box_w / box_h
        if image_aspect > box_aspect:
            width = box_w
            height = box_w / image_aspect
        else:
            height = box_h
            width = box_h * image_aspect
        cx = (left + right) / 2
        return (cx - width / 2, cx + width / 2, bottom, bottom + height)

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
