import math

import arcade
from PIL import Image

from src import constants


def _texture_from_path(path, hash_key):
    image = Image.open(path).convert("RGBA")
    bbox = image.getbbox()
    return arcade.Texture(image, hash=hash_key), image, bbox


class Player(arcade.Sprite):
    def __init__(self):
        idle, idle_image, idle_bbox = _texture_from_path(
            constants.SPRITE_JAM_IDLE, "jam-idle"
        )
        super().__init__(idle, scale=constants.PLAYER_SCALE)
        self.idle_texture = idle
        self.walk_textures = [arcade.load_texture(path) for path in constants.SPRITE_JAM_WALK]
        self.search_texture, self.search_scale, self._search_foot_lift = self._prepare_search(
            idle_image, idle_bbox
        )
        self.speed_x = 0
        self.facing_right = True
        self.ground_y = 0
        self.searching = False
        self._walk_time = 0.0
        self._idle_time = 0.0
        self._cycle = sum(constants.PLAYER_WALK_FRAME_DURATIONS)

    @staticmethod
    def _prepare_search(idle_image, idle_bbox):
        image = Image.open(constants.SPRITE_JAM_SEARCH).convert("RGBA")
        bbox = image.getbbox()
        if bbox:
            image = image.crop(bbox)
        texture = arcade.Texture(image, hash="jam-search")
        idle_body_h = max(1, idle_bbox[3] - idle_bbox[1]) if idle_bbox else idle_image.height
        search_body_h = max(1, image.height)
        scale = constants.PLAYER_SCALE * idle_body_h / search_body_h * constants.PLAYER_SEARCH_HEIGHT
        idle_below_feet = idle_image.height - idle_bbox[3] if idle_bbox else 0
        foot_lift = idle_below_feet * constants.PLAYER_SCALE
        return texture, scale, foot_lift

    def place_on_floor(self, x: float, floor_y: float, facing_right: bool = True):
        self.center_x = x
        self.ground_y = floor_y
        self.speed_x = 0
        self.facing_right = facing_right
        self._walk_time = 0.0
        self._idle_time = 0.0
        self.angle = 0
        self.searching = False
        self.apply_idle_pose()

    def _walk_frame(self) -> int:
        t = self._walk_time % self._cycle
        elapsed = 0.0
        for index, duration in enumerate(constants.PLAYER_WALK_FRAME_DURATIONS):
            elapsed += duration
            if t < elapsed:
                return index
        return 0

    def _pose_scale(self, searching=False):
        scale = self.search_scale if searching else constants.PLAYER_SCALE
        self.scale_y = scale
        self.scale_x = scale if self.facing_right else -scale

    def apply_idle_pose(self):
        searching = bool(self.searching)
        self.texture = self.search_texture if searching else self.idle_texture
        self._pose_scale(searching)
        bob = (
            (1.0 - math.cos(self._idle_time * constants.PLAYER_IDLE_BOB_SPEED))
            * 0.5
            * constants.PLAYER_IDLE_BOB_PIXELS
        )
        lift = self._search_foot_lift if searching else 0.0
        self.bottom = self.ground_y - 50 + lift + bob

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
            self._pose_scale(False)
            step = (self._walk_time / self._cycle) % 1.0
            bob = -abs(math.sin(step * math.pi * 2.0)) * constants.PLAYER_WALK_BOB_PIXELS
            self.bottom = self.ground_y - 50 + bob
        else:
            self._idle_time += delta_time
            self.angle = 0
            self.apply_idle_pose()

        half_w = abs(self.width) / 2
        self.center_x = max(half_w, min(constants.SCREEN_WIDTH - half_w, self.center_x))
