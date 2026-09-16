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
            bold = True,
            anchor_x = "center",
            anchor_y = "center"
        )
        self._box_width = 48
        self._box_height = 48


    def set_target(self, player, nearby):
        self.visible = nearby is not None and player is not None
        if self.visible:
            self._label.x = player.center_x
            self._label.y = constants.SCREEN_HEIGHT * 0.64
    
    def draw(self):
        if not self.visible:
            return
        name = key_name(constants.KEY_INTERACT)

        if self._label.text != name:
            self._label.text = name

        left = self._label.x - self._box_width / 2
        bottom = self._label.y - self._box_height / 2

        arcade.draw_lbwh_rectangle_filled(
            left,
            bottom,
            self._box_width,
            self._box_height,
            (35, 35, 40, 220),
        )

        arcade.draw_lbwh_rectangle_outline(
            left,
            bottom,
            self._box_width,
            self._box_height,
            arcade.color.WHITE,
            border_width=2,
        )
        
        self._label.draw()
