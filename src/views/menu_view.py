import json
import sys
import os

import arcade

from src import constants
from src.ui.menu import MenuButton
from src.views.game_view import GameView


class MenuView(arcade.View):
    def __init__(self):                    
        super().__init__()
        scenes = json.loads(constants.DATA_SCENES.read_text(encoding="utf-8"))
        path = constants.PROJECT_ROOT / scenes[constants.SCENE_MENU]["path"]
        self.background = arcade.load_texture(path)
        self.scale = constants.SCREEN_HEIGHT / constants.BASE_HEIGHT
        s = self.scale

        self.jam = arcade.load_texture(constants.SPRITE_JAM_MENU)

        self.title = arcade.Text(
            constants.SCREEN_TITLE,      
            140 * s, 800 * s,                    
            (232, 214, 170),             
            int(110 * s),
            font_name=constants.FONT_TITLE,
            bold=True,
        )
        self.subtitle = arcade.Text(
            "Mourir pour mieux avancer",
            146 * s, 740 * s,
            (210, 198, 176),
            int(30 * s),
            font_name=constants.FONT_TITLE,
            italic=True,
        )

        button_x = self.title.x + self.title.content_width / 2
        self.buttons = [
            MenuButton("Jouer", button_x, 560 * s, 420 * s, 76 * s, self.on_play, int(26 * s)),
            MenuButton("Quitter", button_x, 460 * s, 420 * s, 76 * s, self.on_quit, int(26 * s)),
        ]

    def on_show_view(self):
        self.window.background_color = (8, 8, 10)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            pixelated=True,
        )
        s = self.scale
        arcade.draw_lbwh_rectangle_filled(0, 0, 900 * s, constants.SCREEN_HEIGHT, (8, 6, 10, 160))

        height = 650 * s
        width = self.jam.width * height / self.jam.height
        arcade.draw_texture_rect(self.jam, arcade.LBWH(1330 * s, -30 * s, width, height))

        self.title.draw()
        self.subtitle.draw()

        for button in self.buttons:
            button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.hovered = button.contains(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for menu_button in self.buttons:
            if menu_button.contains(x, y):
                menu_button.on_click()

    def on_play(self):
        game = GameView()
        game.setup()
        self.window.show_view(game)

    def on_quit(self):
        self.window.close()
        os._exit(0)