import arcade
from arcade.types import LRBT

from src import constants


class WorldCamera:
    """Monde fixe 1920×1080. La fenêtre peut changer : letterbox 16:9 + bandes noires."""

    def __init__(self, window=None):
        self._camera = arcade.Camera2D(
            window=window,
            projection=LRBT(0, constants.WORLD_WIDTH, 0, constants.WORLD_HEIGHT),
            position=(0.0, 0.0),
        )
        self.fit_to_window()

    def fit_to_window(self):
        self._camera.match_window(
            viewport=True,
            projection=False,
            scissor=False,
            position=False,
            aspect=constants.ASPECT_RATIO,
        )
        self._camera.projection = LRBT(0, constants.WORLD_WIDTH, 0, constants.WORLD_HEIGHT)
        self._camera.position = (0.0, 0.0)

    def use(self):
        self._camera.use()

    def begin_frame(self):
        """Efface toute la fenêtre (bandes noires), puis active le cadre 16:9."""
        window = self._camera._window
        window.ctx.viewport = (0, 0, window.width, window.height)
        window.clear(color=constants.LETTERBOX_COLOR)
        self.use()

    def to_world(self, screen_x, screen_y):
        world = self._camera.unproject((screen_x, screen_y))
        return world.x, world.y
