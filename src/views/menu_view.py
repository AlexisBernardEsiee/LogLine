import os
import sys

import arcade

from src import constants
from src.camera import WorldCamera
from src.ui.menu import MenuButton
from src.ui.scenes import load_scene_texture
from src.views.game_view import GameView
from src.views.settings_view import SettingsView


class MenuView(arcade.View):
    def __init__(self):                    
        super().__init__()
        self.world_camera = WorldCamera(self.window)
        self.background = load_scene_texture(constants.SCENE_MENU)
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
            MenuButton("Jouer", button_x, 600 * s, 420 * s, 76 * s, self.on_play, int(26 * s)),
            MenuButton("Paramètres", button_x, 500 * s, 420 * s, 76 * s, self.on_settings, int(26 * s)),
            MenuButton("Quitter", button_x, 400 * s, 420 * s, 76 * s, self.on_quit, int(26 * s)),
        ]

    def on_show_view(self):
        self.window.background_color = (8, 8, 10)
        self.world_camera.fit_to_window()
        for button in self.buttons:
            button.hovered = False

    def on_draw(self):
        self.world_camera.begin_frame()
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
        x, y = self.world_camera.to_world(x, y)
        for button in self.buttons:
            button.hovered = button.contains(x, y)

    def on_mouse_press(self, x, y, button, modifiers):  
        x, y = self.world_camera.to_world(x, y)
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

    def on_settings(self):
        self.window.show_view(SettingsView(self))

    def on_resize(self, width, height):
        self.world_camera.fit_to_window()