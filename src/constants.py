from pathlib import Path

import arcade
from arcade.key import C, E, ENTER, G, LEFT, RIGHT, SPACE

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASE_WIDTH = 1920
BASE_HEIGHT = 1080

def get_window_size():
    screen_width, screen_height = arcade.get_display_size()
    max_width = int(screen_width)
    max_height = int(screen_height)
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

PLAYER_SCALE = 0.3
PLAYER_SPEED = 7
SPRITE_JAM_WALK_DIR = PROJECT_ROOT / "assets" / "sprites" / "jam" / "walk"
SPRITE_JAM_DIR = PROJECT_ROOT / "assets" / "sprites" / "jam"
SPRITE_JAM_MENU = str(SPRITE_JAM_DIR / "dialogs" / "jam_smile_1.png")
SPRITE_JAM_IDLE = str(SPRITE_JAM_DIR / "jam_idle.png")
SPRITE_JAM_WALK = [
    str(SPRITE_JAM_WALK_DIR / "walk1.png"),
    str(SPRITE_JAM_WALK_DIR / "walk2.png"),
    str(SPRITE_JAM_WALK_DIR / "walk3.png"),
    str(SPRITE_JAM_WALK_DIR / "walk4.png"),
]
# Durées par frame : contact (3 et 5) un peu plus long, pour poser le pied.
PLAYER_WALK_FRAME_DURATIONS = (0.15, 0.19, 0.15, 0.19)
PLAYER_WALK_BOB_PIXELS = 2.2
PLAYER_IDLE_BOB_SPEED = 1.4
PLAYER_IDLE_BOB_PIXELS = 1.6

KEY_LEFT = LEFT
KEY_RIGHT = RIGHT
KEY_INTERACT = E
KEY_CONFIRM = ENTER
KEY_SKIP = SPACE
KEY_GRID = G
KEY_COPY_HITBOX = C

DEBUG_GRID_STEP = 50
DEBUG_GRID_MAJOR = 100

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
DIALOGUE_PORTRAIT_SCALE = 0.27
DIALOGUE_BOX_LEFT = SCREEN_WIDTH * 0.04
DIALOGUE_BOX_RIGHT = SCREEN_WIDTH - DIALOGUE_BOX_LEFT
DIALOGUE_BOX_BOTTOM = SCREEN_HEIGHT * 0.04
DIALOGUE_BOX_TOP =  DIALOGUE_BOX_BOTTOM + SCREEN_HEIGHT * 0.28

BASE_DIALOGUE_FONT_SIZE = 25
DIALOGUE_FONT_SIZE = int(
    BASE_DIALOGUE_FONT_SIZE * SCREEN_HEIGHT / BASE_HEIGHT
)

INSPECT_DURATION = 0.55
INSPECT_ZOOM = 2.5
INSPECT_FADE_ALPHA = 175

ROOM_CORRIDOR = "room_1"
ROOM_BAR = "room_2"
SCENE_ROOM = "room"

SCENE_MENU = "menu"
