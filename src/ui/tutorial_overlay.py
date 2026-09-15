import arcade

from src import constants


class TutorialOverlay:
    def __init__(self):
        self.visible = False
        self._move = arcade.Text(
            "<-  ->  pour marcher",
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT - 70,
            (70, 60, 50, 210),
            20,
            anchor_x="center",
        )
        self._interact = arcade.Text(
            "E  pour interagir",
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT - 104,
            (70, 60, 50, 210),
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
        self._move.draw()
        self._interact.draw()
