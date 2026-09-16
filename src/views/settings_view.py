import arcade

from src import constants
from src.ui.menu import MenuButton
from src.ui.scenes import load_scene_texture


class SettingsView(arcade.View):
    def __init__(self, previous_view):
        super().__init__()
        self.previous_view = previous_view
        self.scale = constants.SCREEN_HEIGHT / constants.BASE_HEIGHT
        s = self.scale

        self.background = load_scene_texture(constants.SCENE_MENU)

        self.title = arcade.Text(
            "Paramètres",
            constants.SCREEN_WIDTH / 2, 940 * s,
            (232, 214, 170),
            int(60 * s),
            font_name=constants.FONT_TITLE,
            bold=True,
            anchor_x="center",
        )

        self.buttons = [
            MenuButton("Retour", constants.SCREEN_WIDTH / 2, 120 * s, 320 * s, 76 * s,
                       self.on_back, int(26 * s)),
        ]

    def on_draw(self):
        self.clear()
        s = self.scale
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            pixelated=True,
        )
        # voile sombre sur tout l'écran
        arcade.draw_lbwh_rectangle_filled(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, (8, 6, 10, 170)
        )
        # panneau central
        panel_w, panel_h = 1000 * s, 990 * s
        panel_left = (constants.SCREEN_WIDTH - panel_w) / 2
        panel_bottom = 45 * s
        arcade.draw_lbwh_rectangle_filled(panel_left, panel_bottom, panel_w, panel_h, (18, 14, 20, 235))
        arcade.draw_lbwh_rectangle_outline(panel_left, panel_bottom, panel_w, panel_h, (214, 200, 168), 2)

        self.title.draw()
        for button in self.buttons:
            button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.hovered = button.contains(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for menu_button in self.buttons:
            if menu_button.contains(x, y):
                menu_button.on_click()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.on_back()

    def on_back(self):
        self.window.show_view(self.previous_view)