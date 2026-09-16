from pathlib import Path

import arcade
from arcade.key import E, ENTER, LEFT, RIGHT, SPACE

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASE_WIDTH = 1920
BASE_HEIGHT = 1080

def get_window_size():
    screen_width, screen_height = arcade.get_display_size()
    max_width = int(screen_width * 0.7)
    max_height = int(screen_height * 0.7)
    aspect_ratio = BASE_WIDTH / BASE_HEIGHT

    width = max_width
    height = int(width / aspect_ratio)

    if height > max_height:
        height = max_height
        width = int(height * aspect_ratio)

    return width, height


SCREEN_WIDTH, SCREEN_HEIGHT = get_window_size()
SCREEN_TITLE = "LogLine"
FPS = 60

PLAYER_SCALE = 0.32
PLAYER_SPEED = 7
SPRITE_JAM_IDLE = str(PROJECT_ROOT / "assets" / "sprites" / "jam" / "jam_idle.png")

KEY_LEFT = LEFT
KEY_RIGHT = RIGHT
KEY_INTERACT = E
KEY_CONFIRM = ENTER
KEY_SKIP = SPACE

DATA_DIALOGUES = PROJECT_ROOT / "src" / "data" / "dialogues"
DATA_ROOMS = PROJECT_ROOT / "src" / "data" / "rooms"
DATA_SCENES = PROJECT_ROOT / "src" / "data" / "scenes.json"

FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"
FONT_TITLE = "Lora"
FONT_BODY = "Verdana"
_FONTS_LOADED = False


def load_fonts():
    global _FONTS_LOADED
    if _FONTS_LOADED:
        return
    arcade.load_font(FONTS_DIR / "Verdana.ttf")
    arcade.load_font(FONTS_DIR / "static" / "Lora-Regular.ttf")
    arcade.load_font(FONTS_DIR / "static" / "Lora-Bold.ttf")
    arcade.load_font(FONTS_DIR / "static" / "Lora-Italic.ttf")
    _FONTS_LOADED = True


DIALOGUE_CHARS_PER_SECOND = 42
DIALOGUE_PORTRAIT_SCALE = 0.38
DIALOGUE_BOX_LEFT = SCREEN_WIDTH * 0.04
DIALOGUE_BOX_RIGHT = SCREEN_WIDTH - DIALOGUE_BOX_LEFT
DIALOGUE_BOX_BOTTOM = SCREEN_HEIGHT * 0.04
DIALOGUE_BOX_TOP =  DIALOGUE_BOX_BOTTOM + SCREEN_HEIGHT * 0.28

BASE_DIALOGUE_FONT_SIZE = 25
DIALOGUE_FONT_SIZE = int(
    BASE_DIALOGUE_FONT_SIZE * SCREEN_HEIGHT / BASE_HEIGHT
)

ROOM_CORRIDOR = "room_1"
ROOM_BAR = "room_2"
SCENE_ROOM = "room"
