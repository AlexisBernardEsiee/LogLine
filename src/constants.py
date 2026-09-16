from pathlib import Path

import arcade
from arcade.key import E, ENTER, LEFT, RIGHT, SPACE

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "LogLine"
FPS = 60

PLAYER_SCALE = 0.32
PLAYER_SPEED = 7
SPRITE_JAM_IDLE = str(PROJECT_ROOT / "assets" / "sprites" / "jam" / "jam_idle.png")
SPRITE_JAM_MENU = str(PROJECT_ROOT / "assets" / "sprites" / "jam" / "jam_smile_1.png")

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
DIALOGUE_BOX_LEFT = 70
DIALOGUE_BOX_RIGHT = 1280
DIALOGUE_BOX_BOTTOM = 36
DIALOGUE_BOX_TOP = 290

ROOM_CORRIDOR = "room_1"
ROOM_BAR = "room_2"
SCENE_ROOM = "room"

SCENE_MENU = "accueil"
