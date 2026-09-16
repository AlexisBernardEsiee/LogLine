import arcade

from src import constants
from src.ui.key_names import key_name


class TutorialOverlay:
    def __init__(self):
        self.visible = False
        self._move = arcade.Text(
            "<-  ->  pour marcher",
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT - 70,
            (255, 255, 255, 210),
            20,
            anchor_x="center",
        )
        self._interact = arcade.Text(
            "E  pour interagir",
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT - 104,
            (255, 255, 255, 210),
            20,
            anchor_x="center",
        )

    def show(self):
        self.visible = True

    def mark_moved(self):
        self.visible = False

    def draw(self):
        if not self.visible:
            return
        move = f"{key_name(constants.KEY_LEFT)} / {key_name(constants.KEY_RIGHT)}  pour marcher"
        interact = f"{key_name(constants.KEY_INTERACT)}  pour interagir"
        if self._move.text != move:
            self._move.text = move
        if self._interact.text != interact:
            self._interact.text = interact
        self._move.draw()
        self._interact.draw()
