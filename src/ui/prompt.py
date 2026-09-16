import arcade

from src import constants
from src.ui.key_names import key_name


class InteractionPrompt:
    def __init__(self):
        self.visible = False
        self._label = arcade.Text(
            "E",
            0,
            0,
            arcade.color.WHITE,
            22,
            bold=True,
            anchor_x="center",
        )

    def set_target(self, player, nearby):
        self.visible = nearby is not None and player is not None
        if self.visible:
            self._label.x = player.center_x
            self._label.y = player.top + 16

    def draw(self):
        if self.visible:
            name = key_name(constants.KEY_INTERACT)
            if self._label.text != name:
                self._label.text = name
            self._label.draw()
