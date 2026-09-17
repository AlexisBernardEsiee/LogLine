import arcade

from src import constants
from src.ui.menu import MenuButton

DIGIT_KEYS = {
    **{getattr(arcade.key, f"KEY_{n}"): str(n) for n in range(10)},
    **{getattr(arcade.key, f"NUM_{n}"): str(n) for n in range(10)},
}
ERASE_KEYS = (arcade.key.BACKSPACE, arcade.key.DELETE)
VALIDATE_KEYS = (arcade.key.ENTER, arcade.key.RETURN, arcade.key.NUM_ENTER)

TEXT_COLOR = (232, 214, 170)
ERROR_COLOR = (220, 90, 80)
PANEL_BG = (18, 14, 20, 240)
PANEL_BORDER = (214, 200, 168)


class KeypadOverlay:
    """Cadenas à code : chiffres au clavier ou à la souris."""

    PANEL_LEFT = 680
    PANEL_BOTTOM = 160
    PANEL_WIDTH = 560
    PANEL_HEIGHT = 790

    def __init__(self):
        self.active = False
        self.code = ""
        self.entered = ""
        self.error_timer = 0.0
        cx = constants.SCREEN_WIDTH / 2
        self._title = arcade.Text(
            "", cx, 895, TEXT_COLOR, 34,
            font_name=constants.FONT_TITLE, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hint = arcade.Text(
            "", cx, 842, (200, 190, 170), 20,
            font_name=constants.FONT_TITLE, italic=True,
            anchor_x="center", anchor_y="center",
        )
        self._message = arcade.Text(
            "", cx, 205, ERROR_COLOR, 20,
            font_name=constants.FONT_BODY,
            anchor_x="center", anchor_y="center",
        )
        self._digits = [
            arcade.Text(
                "", 0, 745, TEXT_COLOR, 48,
                font_name=constants.FONT_TITLE, bold=True,
                anchor_x="center", anchor_y="center",
            )
            for _ in range(4)
        ]
        self.buttons = []
        rows = [("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9"), ("C", "0", "OK")]
        for row_index, row in enumerate(rows):
            y = 615 - row_index * 100
            for col_index, label in enumerate(row):
                x = cx + (col_index - 1) * 120
                self.buttons.append(
                    MenuButton(label, x, y, 104, 84, lambda value=label: self.press(value), 30)
                )

    def open(self, spec):
        self.code = str(spec.get("code", ""))
        self.entered = ""
        self.error_timer = 0.0
        self._title.text = spec.get("title", "Cadenas")
        self._hint.text = spec.get("hint", "")
        self._message.text = ""
        self._layout_digits()
        self.active = True

    def close(self):
        self.active = False

    def _layout_digits(self):
        count = max(1, len(self.code))
        if len(self._digits) != count:
            self._digits = [
                arcade.Text(
                    "", 0, 745, TEXT_COLOR, 48,
                    font_name=constants.FONT_TITLE, bold=True,
                    anchor_x="center", anchor_y="center",
                )
                for _ in range(count)
            ]
        for index, label in enumerate(self._digits):
            label.x = constants.SCREEN_WIDTH / 2 + (index - (count - 1) / 2) * 110

    def press(self, value):
        """Retourne True si le code est bon."""
        if value == "C":
            self.entered = self.entered[:-1]
            return False
        if value == "OK":
            return self.validate()
        if len(self.entered) < len(self.code):
            self.entered += value
            self._message.text = ""
        return False

    def validate(self):
        if self.entered == self.code:
            return True
        self.entered = ""
        self.error_timer = 1.6
        self._message.text = "Ce n'est pas le bon code."
        return False

    def on_key_press(self, key):
        """Retourne True si le code est bon."""
        if key in DIGIT_KEYS:
            return self.press(DIGIT_KEYS[key])
        if key in ERASE_KEYS:
            return self.press("C")
        if key in VALIDATE_KEYS or key == constants.KEY_CONFIRM:
            return self.validate()
        return False

    def on_mouse_motion(self, x, y):
        for button in self.buttons:
            button.hovered = button.contains(x, y)

    def on_mouse_press(self, x, y):
        """Retourne True si le code est bon."""
        for button in self.buttons:
            if button.contains(x, y):
                return bool(button.on_click())
        return False

    def update(self, delta_time):
        if self.error_timer > 0:
            self.error_timer = max(0.0, self.error_timer - delta_time)

    def draw(self):
        if not self.active:
            return
        arcade.draw_lbwh_rectangle_filled(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, (8, 6, 10, 170)
        )
        arcade.draw_lbwh_rectangle_filled(
            self.PANEL_LEFT, self.PANEL_BOTTOM, self.PANEL_WIDTH, self.PANEL_HEIGHT, PANEL_BG
        )
        arcade.draw_lbwh_rectangle_outline(
            self.PANEL_LEFT, self.PANEL_BOTTOM, self.PANEL_WIDTH, self.PANEL_HEIGHT, PANEL_BORDER, 2
        )
        self._title.draw()
        self._hint.draw()

        border = ERROR_COLOR if self.error_timer > 0 else PANEL_BORDER
        for index, label in enumerate(self._digits):
            arcade.draw_lbwh_rectangle_outline(label.x - 45, 690, 90, 110, border, 3)
            label.text = self.entered[index] if index < len(self.entered) else ""
            label.draw()

        for button in self.buttons:
            button.draw()
        self._message.draw()
