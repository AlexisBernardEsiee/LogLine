import math

import arcade

from src import constants


class Player(arcade.Sprite):
    def __init__(self):
        idle = arcade.load_texture(constants.SPRITE_JAM_IDLE)
        super().__init__(idle, scale=constants.PLAYER_SCALE)
        self.idle_texture = idle
        self.walk_textures = [arcade.load_texture(path) for path in constants.SPRITE_JAM_WALK]
        self.speed_x = 0
        self.facing_right = True
        self.ground_y = 0
        self._walk_time = 0.0
        self._idle_time = 0.0
        self._cycle = sum(constants.PLAYER_WALK_FRAME_DURATIONS)

    def place_on_floor(self, x: float, floor_y: float):
        self.center_x = x
        self.ground_y = floor_y
        self.bottom = floor_y
        self.speed_x = 0
        self._walk_time = 0.0
        self._idle_time = 0.0
        self.angle = 0
        self.scale_y = constants.PLAYER_SCALE
        self.texture = self.idle_texture

    def _walk_frame(self) -> int:
        t = self._walk_time % self._cycle
        elapsed = 0.0
        for index, duration in enumerate(constants.PLAYER_WALK_FRAME_DURATIONS):
            elapsed += duration
            if t < elapsed:
                return index
        return 0

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.center_x += self.speed_x
        if self.speed_x > 0:
            self.facing_right = True
        elif self.speed_x < 0:
            self.facing_right = False
            

        moving = self.speed_x != 0
        if moving:
            self._walk_time += delta_time
            self._idle_time = 0.0
            frame = self._walk_frame()
            self.texture = self.walk_textures[frame]
            self.angle = 0
            self.scale_y = constants.PLAYER_SCALE
            step = (self._walk_time / self._cycle) % 1.0
            bob = -abs(math.sin(step * math.pi * 2.0)) * constants.PLAYER_WALK_BOB_PIXELS
            self.bottom = self.ground_y + bob
        else:
            self._idle_time += delta_time
            self.texture = self.idle_texture
            self.angle = 0
            self.scale_y = constants.PLAYER_SCALE
            bob = (1.0 - math.cos(self._idle_time * constants.PLAYER_IDLE_BOB_SPEED)) * 0.5 * constants.PLAYER_IDLE_BOB_PIXELS
            self.bottom = self.ground_y + bob

        abs_scale = abs(self.scale_x) or constants.PLAYER_SCALE
        self.scale_x = abs_scale if self.facing_right else -abs_scale

        half_w = abs(self.width) / 2
        self.center_x = max(half_w, min(constants.SCREEN_WIDTH - half_w, self.center_x))
