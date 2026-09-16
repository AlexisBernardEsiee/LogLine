import arcade
from PIL import Image

from src import constants


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _crop_from_screen(texture, left, right, bottom, top):
    tex_w, tex_h = texture.width, texture.height
    x = int(left / constants.SCREEN_WIDTH * tex_w)
    width = max(1, int((right - left) / constants.SCREEN_WIDTH * tex_w))
    height = max(1, int((top - bottom) / constants.SCREEN_HEIGHT * tex_h))
    y_from_top = int((1.0 - top / constants.SCREEN_HEIGHT) * tex_h)
    x = max(0, min(x, tex_w - 1))
    y_from_top = max(0, min(y_from_top, tex_h - 1))
    width = min(width, tex_w - x)
    height = min(height, tex_h - y_from_top)
    return texture.crop(x, y_from_top, width, height)


def _load_inspect_sprite(relative_path):
    full_path = constants.PROJECT_ROOT / relative_path
    image = Image.open(full_path).convert("RGBA")
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)
    return arcade.Texture(image, hash=f"inspect-sprite:{relative_path}")


class InspectEffect:
    """Deux effets distincts : crop du décor, ou sprite dédié."""

    def __init__(self):
        self.active = False
        self.closing = False
        self.just_opened = False
        self._skip_open = False
        self.progress = 0.0
        self.duration = constants.INSPECT_DURATION
        self.texture = None
        self.src = None
        self.dst = None
        self._sprite_cache = {}

    def start_from_decor(self, background_texture, rect, zoom=None, duration=None):
        if background_texture is None:
            return False
        left, right, bottom, top = rect
        texture = _crop_from_screen(background_texture, left, right, bottom, top)
        dest = self._target_from_rect(left, right, bottom, top, zoom or constants.INSPECT_ZOOM)
        return self._begin(texture, rect, dest, duration)

    def start_from_sprite(self, sprite_path, rect, zoom=None, duration=None):
        if not sprite_path:
            return False
        if sprite_path not in self._sprite_cache:
            self._sprite_cache[sprite_path] = _load_inspect_sprite(sprite_path)
        texture = self._sprite_cache[sprite_path]
        dest = self._target_from_texture(texture, zoom or 1.0)
        return self._begin(texture, rect, dest, duration)

    def _begin(self, texture, src_rect, dest_rect, duration):
        self.texture = texture
        self.src = tuple(src_rect)
        self.dst = dest_rect
        self.duration = duration if duration is not None else constants.INSPECT_DURATION
        self.active = True
        self.closing = False
        self.just_opened = False
        self._skip_open = False
        self.progress = 0.0
        return True

    def set_sprite(self, sprite_path):
        if not sprite_path or not self.active:
            return False
        if sprite_path not in self._sprite_cache:
            self._sprite_cache[sprite_path] = _load_inspect_sprite(sprite_path)
        texture = self._sprite_cache[sprite_path]
        self.texture = texture
        self.dst = self._target_from_texture(texture, 1.0)
        return True

    def close(self):
        if not self.active:
            return
        self.closing = True
        self.just_opened = False

    def skip_open(self):
        if self.active and not self.closing and self.progress < 1.0:
            self._skip_open = True

    def update(self, delta_time):
        self.just_opened = False
        if not self.active:
            return
        if self._skip_open:
            self._skip_open = False
            self.progress = 1.0
            self.just_opened = True
            return
        step = delta_time / max(self.duration, 0.01)
        if self.closing:
            self.progress = max(0.0, self.progress - step)
            if self.progress <= 0.0:
                self.active = False
                self.closing = False
                self.texture = None
            return
        was_opening = self.progress < 1.0
        self.progress = min(1.0, self.progress + step)
        if was_opening and self.progress >= 1.0:
            self.just_opened = True

    def draw(self):
        if not self.active or self.texture is None or self.src is None:
            return
        t = _ease(self.progress)
        arcade.draw_lrbt_rectangle_filled(
            0,
            constants.SCREEN_WIDTH,
            0,
            constants.SCREEN_HEIGHT,
            (0, 0, 0, int(constants.INSPECT_FADE_ALPHA * t)),
        )
        left, right, bottom, top = (
            self.src[i] + (self.dst[i] - self.src[i]) * t for i in range(4)
        )
        arcade.draw_texture_rect(
            self.texture,
            arcade.LRBT(left, right, bottom, top),
            alpha=int(80 + 175 * t),
            pixelated=True,
        )

    @staticmethod
    def _target_from_rect(left, right, bottom, top, zoom):
        width = (right - left) * zoom
        height = (top - bottom) * zoom
        max_width = constants.SCREEN_WIDTH * 0.62
        max_height = constants.SCREEN_HEIGHT - constants.DIALOGUE_BOX_TOP - 48
        scale = min(1.0, max_width / max(width, 1), max_height / max(height, 1))
        width *= scale
        height *= scale
        cx = constants.SCREEN_WIDTH / 2
        cy = (constants.DIALOGUE_BOX_TOP + constants.SCREEN_HEIGHT) / 2
        return (cx - width / 2, cx + width / 2, cy - height / 2, cy + height / 2)

    @staticmethod
    def _target_from_texture(texture, zoom):
        max_width = constants.SCREEN_WIDTH * 0.42 * zoom
        max_height = (constants.SCREEN_HEIGHT - constants.DIALOGUE_BOX_TOP - 48) * 0.92
        aspect = texture.width / max(texture.height, 1)
        if max_width / aspect <= max_height:
            width, height = max_width, max_width / aspect
        else:
            height, width = max_height, max_height * aspect
        cx = constants.SCREEN_WIDTH / 2
        cy = (constants.DIALOGUE_BOX_TOP + constants.SCREEN_HEIGHT) / 2
        return (cx - width / 2, cx + width / 2, cy - height / 2, cy + height / 2)
