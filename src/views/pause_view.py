import os

import arcade

from src import constants
from src.camera import WorldCamera
from src.ui.menu import MenuButton
from src.views.credits_view import CreditsView
from src.views.settings_view import SettingsView


class PauseView(arcade.View):

    def __init__(self, game_view):
        super().__init__()
        self.world_camera = WorldCamera(self.window)
        self.game_view = game_view
        self.scale = constants.SCREEN_HEIGHT / constants.BASE_HEIGHT
        s = self.scale

        self.title = arcade.Text(
            "Pause",
            constants.SCREEN_WIDTH / 2, 790 * s,
            (232, 214, 170),
            int(64 * s),
            font_name=constants.FONT_TITLE,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

        rows = [
            ("Reprendre", self.on_resume),
            ("Paramètres", self.on_settings),
            ("Crédits", self.on_credits),
            ("Menu principal", self.on_main_menu),
            ("Quitter le jeu", self.on_quit),
        ]
        self.buttons = [
            MenuButton(
                label,
                constants.SCREEN_WIDTH / 2, y * s,
                420 * s, 72 * s,
                action,
                int(26 * s),
            )
            for (label, action), y in zip(rows, range(660, 160, -100))
        ]

    def on_show_view(self):
        self.world_camera.fit_to_window()
        for button in self.buttons:
            button.hovered = False

    def on_resize(self, width, height):
        self.world_camera.fit_to_window()

    def on_draw(self):
        self.game_view.on_draw()
        self.world_camera.use()

        s = self.scale
        arcade.draw_lbwh_rectangle_filled(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, (8, 6, 10, 180)
        )
        panel_w, panel_h = 640 * s, 660 * s
        panel_left = (constants.SCREEN_WIDTH - panel_w) / 2
        panel_bottom = 210 * s
        arcade.draw_lbwh_rectangle_filled(panel_left, panel_bottom, panel_w, panel_h, (18, 14, 20, 235))
        arcade.draw_lbwh_rectangle_outline(panel_left, panel_bottom, panel_w, panel_h, (214, 200, 168), 2)

        self.title.draw()
        for button in self.buttons:
            button.draw()

    # Entrées joueur

    def on_key_press(self, key, modifiers):
        if key == constants.KEY_BACK:
            self.on_resume()

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.world_camera.to_world(x, y)
        for button in self.buttons:
            button.hovered = button.contains(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = self.world_camera.to_world(x, y)
        for menu_button in self.buttons:
            if menu_button.contains(x, y):
                menu_button.on_click()
                return

    # Actions

    def on_resume(self):
        self.window.show_view(self.game_view)

    def on_settings(self):
        self.window.show_view(SettingsView(self))

    def on_credits(self):
        self.window.show_view(CreditsView(self))

    def on_main_menu(self):
        # Import tardif : menu_view importe game_view, qui importe ce fichier.
        from src.views.menu_view import MenuView

        self.game_view.audio.stop_music()
        self.window.show_view(MenuView())

    def on_quit(self):
        self.window.close()
        os._exit(0)
