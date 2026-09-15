import json

import arcade

from src import constants
from src.entities.interactable import Interactable


class RoomManager:
    def __init__(self):
        self.current_room_id = None
        self.name = ""
        self.entry_x = 220
        self.floor_y = 168
        self.interactables = []

    def load_room(self, room_id):
        path = constants.DATA_ROOMS / f"{room_id}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        self.current_room_id = room_id
        self.name = data.get("name", room_id)
        self.entry_x = data.get("entry_x", 220)
        self.floor_y = data.get("floor_y", 168)
        self.interactables = [Interactable(item) for item in data.get("interactables", [])]

    def get_nearby_interactable(self, player):
        if player is None:
            return None
        for item in self.interactables:
            if item.contains(player):
                return item
        return None

    def draw(self):
        if self.current_room_id == constants.ROOM_CORRIDOR:
            self._draw_corridor()
        else:
            self._draw_placeholder()

        for item in self.interactables:
            self._draw_item(item)

    def _draw_corridor(self):
        arcade.draw_lrbt_rectangle_filled(
            0, constants.SCREEN_WIDTH, self.floor_y, constants.SCREEN_HEIGHT, (236, 224, 204)
        )
        arcade.draw_lrbt_rectangle_filled(
            0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT - 90, constants.SCREEN_HEIGHT, (214, 200, 178)
        )
        arcade.draw_lrbt_rectangle_filled(
            0, constants.SCREEN_WIDTH, 0, self.floor_y, (108, 82, 60)
        )
        arcade.draw_lrbt_rectangle_filled(
            0, constants.SCREEN_WIDTH, self.floor_y, self.floor_y + 14, (78, 56, 40)
        )

    def _draw_placeholder(self):
        arcade.draw_lrbt_rectangle_filled(
            0, constants.SCREEN_WIDTH, self.floor_y, constants.SCREEN_HEIGHT, (48, 42, 40)
        )
        arcade.draw_lrbt_rectangle_filled(
            0, constants.SCREEN_WIDTH, 0, self.floor_y, (72, 52, 40)
        )
        arcade.draw_text(
            self.name,
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2 + 80,
            (180, 170, 160),
            28,
            anchor_x="center",
        )

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
