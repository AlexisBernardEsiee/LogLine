import arcade
from PIL import Image

from src import constants


def _ease_in(t):
    t = max(0.0, min(1.0, t))
    return t * t


class LustreProp:
    """Lustre visible dans le bureau : suspendu, puis chute animée."""

    def __init__(self):
        self.texture = None
        self.hang = (790, 1130, 580, 1020)
        self.land = (980, 1340, 230, 580)
        self.duration = 0.85
        self.phase = "hanging"
        self.timer = 0.0
        self.just_landed = False
        self._cx = 0.0
        self._cy = 0.0
        self._w = 1.0
        self._h = 1.0
        self._angle = 0.0

    def configure(self, data):
        if not data:
            self.texture = None
            self.phase = "hidden"
            return
        path = constants.PROJECT_ROOT / data.get(
            "sprite", "assets/sprites/lustre/lustre_x4.png"
        )
        image = Image.open(path).convert("RGBA")
        bbox = image.getbbox()
        if bbox:
            image = image.crop(bbox)
        self.texture = arcade.Texture(image, hash="lustre-prop")
        self.hang = tuple(data.get("hang", self.hang))
        self.land = tuple(data.get("land", self.land))
        self.duration = float(data.get("fall_seconds", 0.85))
        self.reset()

    def reset(self):
        self.phase = "hanging" if self.texture else "hidden"
        self.timer = 0.0
        self.just_landed = False
        self._place(self.hang, 0.0)

    @property
    def falling(self):
        return self.phase == "falling"

    @property
    def blocking(self):
        return self.phase == "falling"

    def start_fall(self):
        if self.texture is None or self.phase == "falling":
            return
        self.phase = "falling"
        self.timer = 0.0
        self.just_landed = False

    def hide(self):
        self.phase = "gone"

    def update(self, delta_time):
        self.just_landed = False
        if self.phase != "falling":
            if self.phase == "hanging":
                self._place(self.hang, 0.0)
            return
        self.timer += delta_time
        t = _ease_in(self.timer / max(self.duration, 0.01))
        self._lerp(self.hang, self.land, min(1.0, t), -62.0 * min(1.0, t))
        if self.timer >= self.duration:
            self._place(self.land, -62.0)
            self.phase = "landed"
            self.just_landed = True

    def draw(self):
        if self.texture is None or self.phase in ("hidden", "gone"):
            return
        if self.phase == "hanging":
            self._place(self.hang, 0.0)
        arcade.draw_texture_rect(
            self.texture,
            arcade.LBWH(self._cx - self._w / 2, self._cy - self._h / 2, self._w, self._h),
            angle=self._angle,
            pixelated=True,
        )

    def _place(self, rect, angle):
        left, right, bottom, top = rect
        self._cx = (left + right) / 2
        self._cy = (bottom + top) / 2
        self._w = max(right - left, 1)
        self._h = max(top - bottom, 1)
        self._fit()
        self._angle = angle

    def _lerp(self, start, end, t, angle):
        s_cx = (start[0] + start[1]) / 2
        s_cy = (start[2] + start[3]) / 2
        e_cx = (end[0] + end[1]) / 2
        e_cy = (end[2] + end[3]) / 2
        self._cx = s_cx + (e_cx - s_cx) * t
        self._cy = s_cy + (e_cy - s_cy) * t
        self._w = max(end[1] - end[0], 1)
        self._h = max(end[3] - end[2], 1)
        self._fit()
        self._angle = angle

    def _fit(self):
        if self.texture is None:
            return
        aspect = self.texture.width / max(self.texture.height, 1)
        box_aspect = self._w / self._h
        if aspect > box_aspect:
            self._h = self._w / aspect
        else:
            self._w = self._h * aspect
