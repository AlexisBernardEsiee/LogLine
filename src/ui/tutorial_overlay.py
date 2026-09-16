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

        self._escape_x = constants.SCREEN_WIDTH - 150
        self._escape_y = constants.SCREEN_HEIGHT - 55
        self._escape_width = 58
        self._escape_height = 32

        self._escape_key = arcade.Text(
            "ESC",
            self._escape_x,
            self._escape_y,
            (255, 255, 255, 230),
            16,
            anchor_x="center",
            anchor_y="center",
        )

        self._menu_text = arcade.Text(
            "Menu",
            self._escape_x + 42,
            self._escape_y,
            (255, 255, 255, 230),
            16,
            anchor_y="center",
        )

    def show(self):
        self.visible = True

    def mark_moved(self):
        self.visible = False

    def draw(self):
        # Tutoriel
        if self.visible:
            move = f"{key_name(constants.KEY_LEFT)} / {key_name(constants.KEY_RIGHT)}  pour marcher"
            interact = f"{key_name(constants.KEY_INTERACT)}  pour interagir"

            if self._move.text != move:
                self._move.text = move

            if self._interact.text != interact:
                self._interact.text = interact

            self._move.draw()
            self._interact.draw()


        arcade.draw_lbwh_rectangle_filled(
            self._escape_x - self._escape_width / 2,
            self._escape_y - self._escape_height / 2,
            self._escape_width,
            self._escape_height,
            (35, 35, 40, 220),
        )

        arcade.draw_lbwh_rectangle_outline(
            self._escape_x - self._escape_width / 2,
            self._escape_y - self._escape_height / 2,
            self._escape_width,
            self._escape_height,
            (220, 220, 225, 230),
            border_width=2,
        )

        self._escape_key.draw()
        self._menu_text.draw()