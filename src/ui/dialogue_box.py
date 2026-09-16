import arcade
from PIL import Image

from src import constants

_PORTRAIT_TEXTURES = {}


def _portrait_texture(relative_path):
    texture = _PORTRAIT_TEXTURES.get(relative_path)
    if texture is not None:
        return texture
    full_path = constants.PROJECT_ROOT / relative_path
    image = Image.open(full_path).convert("RGBA")
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)
    texture = arcade.Texture(image, hash=f"dialogue-portrait:{relative_path}")
    _PORTRAIT_TEXTURES[relative_path] = texture
    return texture


def warmup_portraits(relative_paths):
    for relative_path in relative_paths:
        _portrait_texture(relative_path)


class DialogueBox:
    def __init__(self, audio_manager=None):
        constants.load_fonts()
        self.speaker = ""
        self.full_text = ""
        self.visible = False
        self.audio = audio_manager
        self.thought = False
        self.shown_chars = 0.0
        self.chars_per_second = constants.DIALOGUE_CHARS_PER_SECOND
        self._portraits = {}
        self._portrait = None
        self._name_label = arcade.Text(
            "",
            constants.DIALOGUE_BOX_LEFT + 28,
            constants.DIALOGUE_BOX_TOP - 46,
            (232, 214, 170),
            constants.DIALOGUE_FONT_SIZE,
            font_name=constants.FONT_TITLE,
            bold=True,
        )
        self._body_label = self._make_body_label(italic=False)
        self._hint_label = arcade.Text(
            "▼",
            constants.DIALOGUE_BOX_RIGHT - 42,
            constants.DIALOGUE_BOX_BOTTOM + 18,
            (200, 190, 170),
            16,
            font_name=constants.FONT_BODY,
        )

    def _make_body_label(self, italic):
        return arcade.Text(
            "",
            constants.DIALOGUE_BOX_LEFT + 28,
            constants.DIALOGUE_BOX_TOP - 88,
            arcade.color.WHITE,
            constants.DIALOGUE_FONT_SIZE,
            font_name=constants.FONT_BODY,
            width=int(constants.DIALOGUE_BOX_RIGHT - constants.DIALOGUE_BOX_LEFT - 56),
            multiline=True,
            italic=italic,
            anchor_y="top",
        )

    def show(self, line):
        self.speaker = line.get("speaker", "")
        self.full_text = line.get("text", "")
        self.thought = bool(line.get("thought", False))
        self.shown_chars = 0.0
        self.visible = True
        self._portrait = self._load_portrait(line.get("sprite"))
        self._name_label.text = self.speaker
        if self.speaker == "???":
            self._name_label.color = (80, 220, 110)
        else:
            self._name_label.color = (
                (210, 198, 176)
                if self.thought
                else (232, 214, 170)
            )
        self._body_label = self._make_body_label(italic=self.thought)
        self._refresh_body()

    def hide(self):
        self.visible = False
        self._portrait = None

    def update(self, delta_time):
        if not self.visible:
            return
        old_chars = int(self.shown_chars)
        self.shown_chars = min(
            len(self.full_text),
            self.shown_chars + self.chars_per_second * delta_time,
        )
        new_chars = int(self.shown_chars)

        # Déclenche un son si une nouvelle lettre (non vide) vient d'apparaître
        if new_chars > old_chars and self.audio:
            added_text = self.full_text[old_chars:new_chars]
            if added_text.strip():
                self.audio.play_typewriter_sound()

        self._refresh_body()

    def is_typing(self):
        return self.visible and self.shown_chars < len(self.full_text)

    def skip_typing(self):
        self.shown_chars = float(len(self.full_text))
        self._refresh_body()

    def _refresh_body(self):
        self._body_label.text = self.full_text[: int(self.shown_chars)]

    def _load_portrait(self, relative_path):
        if not relative_path:
            return None
        if relative_path not in self._portraits:
            texture = _portrait_texture(relative_path)
            sprite = arcade.Sprite(texture)
            pad = constants.DIALOGUE_PORTRAIT_PAD
            avail_w = constants.SCREEN_WIDTH - constants.DIALOGUE_BOX_RIGHT - pad * 2
            avail_h = constants.SCREEN_HEIGHT * constants.DIALOGUE_PORTRAIT_HEIGHT_RATIO
            sprite.scale = min(avail_w / sprite.width, avail_h / sprite.height)
            sprite.center_x = (constants.DIALOGUE_BOX_RIGHT + constants.SCREEN_WIDTH) / 2
            sprite.bottom = pad
            self._portraits[relative_path] = sprite
        return self._portraits[relative_path]

    def draw(self):
        if not self.visible:
            return

        if self._portrait:
            arcade.draw_sprite(self._portrait)

        arcade.draw_lrbt_rectangle_filled(
            constants.DIALOGUE_BOX_LEFT,
            constants.DIALOGUE_BOX_RIGHT,
            constants.DIALOGUE_BOX_BOTTOM,
            constants.DIALOGUE_BOX_TOP,
            (18, 14, 20, 230),
        )
        arcade.draw_lrbt_rectangle_outline(
            constants.DIALOGUE_BOX_LEFT,
            constants.DIALOGUE_BOX_RIGHT,
            constants.DIALOGUE_BOX_BOTTOM,
            constants.DIALOGUE_BOX_TOP,
            (214, 200, 168, 255),
            2,
        )
        self._name_label.draw()
        self._body_label.draw()
        if not self.is_typing():
            self._hint_label.draw()
