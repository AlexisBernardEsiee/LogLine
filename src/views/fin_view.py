import arcade

from src import constants
from src.camera import WorldCamera
from src.systems.game_state import GameState


class FinView(arcade.View):
    """Écran noir, un mot qui clignote, puis les crédits."""

    def __init__(self):
        super().__init__()
        constants.load_fonts()
        self.world_camera = WorldCamera(self.window)
        self.timer = 0.0
        self._label = arcade.Text(
            "FIN.",
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2 + 20,
            (236, 220, 178),
            72,
            font_name=constants.FONT_TITLE,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        self._cursor = arcade.Text(
            "_",
            constants.SCREEN_WIDTH / 2 + 92,
            constants.SCREEN_HEIGHT / 2 + 8,
            (236, 220, 178),
            64,
            font_name=constants.FONT_TITLE,
            bold=True,
            anchor_x="left",
            anchor_y="center",
        )

    def on_show_view(self):
        self.window.background_color = constants.LETTERBOX_COLOR
        self.world_camera.fit_to_window()
        self.timer = 0.0

    def on_resize(self, width, height):
        self.world_camera.fit_to_window()

    def on_update(self, delta_time):
        self.timer += delta_time
        if self.timer >= 3.4:
            self._to_credits()

    def on_draw(self):
        self.world_camera.begin_frame()
        arcade.draw_lrbt_rectangle_filled(
            0,
            constants.SCREEN_WIDTH,
            0,
            constants.SCREEN_HEIGHT,
            (6, 4, 8),
        )
        blink = int(self.timer * 2.2) % 2 == 0
        self._label.color = (236, 220, 178, 255 if self.timer > 0.35 else 0)
        self._label.draw()
        if blink and self.timer > 0.5:
            self._cursor.draw()

    def on_key_press(self, key, modifiers):
        if key in (constants.KEY_CONFIRM, constants.KEY_SKIP, constants.KEY_BACK, constants.KEY_INTERACT):
            self._to_credits()

    def on_mouse_press(self, x, y, button, modifiers):
        self._to_credits()

    def _to_credits(self):
        GameState.clear()
        from src.views.credits_view import CreditsView

        self.window.show_view(CreditsView())
