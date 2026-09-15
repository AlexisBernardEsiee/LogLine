import arcade

from src import constants


class Player(arcade.SpriteSolidColor):
    def __init__(self):
        super().__init__(
            width=constants.PLAYER_WIDTH,
            height=constants.PLAYER_HEIGHT,
            color=constants.PLAYER_COLOR,
        )
        self.speed_x = 0

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.center_x += self.speed_x
        half_w = self.width / 2
        self.center_x = max(half_w, min(constants.SCREEN_WIDTH - half_w, self.center_x))
