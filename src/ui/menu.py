import arcade

from src import constants

COLOR_BG = (18, 14, 20, 215)
COLOR_BG_HOVER = (107, 26, 38, 235)
COLOR_BORDER = (214, 200, 168, 150)
COLOR_BORDER_HOVER = (232, 214, 170, 255)
COLOR_TEXT = (232, 214, 170)


class MenuButton:
    def __init__(self, text, center_x, center_y, width, height, on_click, font_size):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.on_click = on_click
        self.hovered = False
        self.label = arcade.Text(
            text,
            center_x,
            center_y,
            COLOR_TEXT,
            font_size,
            font_name=constants.FONT_TITLE,
            anchor_x="center",
            anchor_y="center",
        )

    def contains(self, x, y):
        return (
            abs(x - self.center_x) <= self.width / 2
            and abs(y - self.center_y) <= self.height / 2
        )

    def draw(self):
        left = self.center_x - self.width / 2
        bottom = self.center_y - self.height / 2
        bg = COLOR_BG_HOVER if self.hovered else COLOR_BG
        border = COLOR_BORDER_HOVER if self.hovered else COLOR_BORDER
        arcade.draw_lbwh_rectangle_filled(left, bottom, self.width, self.height, bg)
        arcade.draw_lbwh_rectangle_outline(left, bottom, self.width, self.height, border, 2)
        self.label.draw()