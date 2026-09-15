import arcade

from src import constants


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(constants.SPRITE_JAM_IDLE, scale=constants.PLAYER_SCALE)
        self.speed_x = 0
        self.facing_right = True

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.center_x += self.speed_x
        if self.speed_x > 0:
            self.facing_right = True
        elif self.speed_x < 0:
            self.facing_right = False

        abs_scale = abs(self.scale_x)
        self.scale_x = abs_scale if self.facing_right else -abs_scale

        half_w = abs(self.width) / 2
        self.center_x = max(half_w, min(constants.SCREEN_WIDTH - half_w, self.center_x))
