from pathlib import Path

import arcade
from arcade.key import C, E, ENTER, ESCAPE, F11, G, LEFT, RIGHT, SPACE

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASE_WIDTH = 1920
BASE_HEIGHT = 1080
WORLD_WIDTH = BASE_WIDTH
WORLD_HEIGHT = BASE_HEIGHT
SCREEN_WIDTH = WORLD_WIDTH
SCREEN_HEIGHT = WORLD_HEIGHT
ASPECT_RATIO = WORLD_WIDTH / WORLD_HEIGHT
WINDOW_MIN_WIDTH = 640
WINDOW_MIN_HEIGHT = 360
# Taille de la fenetre en mode fenetre (et au retour depuis le plein ecran).
WINDOW_DEFAULT_WIDTH = 1280
WINDOW_DEFAULT_HEIGHT = 720
SCREEN_TITLE = "LogLine"
FPS = 60
LETTERBOX_COLOR = (8, 8, 10)


def ratio_label(width, height):
    a, b = int(width), int(height)
    while b:
        a, b = b, a % b
    gcd = max(a, 1)
    return f"{int(width) // gcd}:{int(height) // gcd}"


def scale_h(value):
    return value * SCREEN_HEIGHT / BASE_HEIGHT

PLAYER_SCALE = 0.5
PLAYER_SEARCH_HEIGHT = 1.06
PLAYER_SPEED = 7
SPRITE_JAM_WALK_DIR = PROJECT_ROOT / "assets" / "sprites" / "jam" / "walk"
SPRITE_JAM_DIR = PROJECT_ROOT / "assets" / "sprites" / "jam"
SPRITE_JAM_MENU = str(SPRITE_JAM_DIR / "dialogs" / "jam_smile_1.png")
SPRITE_JAM_IDLE = str(SPRITE_JAM_DIR / "jam_idle.png")
SPRITE_JAM_SEARCH = str(SPRITE_JAM_DIR / "jam_idle_search.png")
SPRITE_JAM_WALK = [
    str(SPRITE_JAM_WALK_DIR / "walk1.png"),
    str(SPRITE_JAM_WALK_DIR / "walk2.png"),
    str(SPRITE_JAM_WALK_DIR / "walk3.png"),
    str(SPRITE_JAM_WALK_DIR / "walk4.png"),
]
SPRITE_JAM_DEATH_DIR = SPRITE_JAM_DIR / "death"
SPRITE_JAM_DEATH_POSE = [
    SPRITE_JAM_IDLE,
    str(SPRITE_JAM_DEATH_DIR / "death_spirte_1.png"),
    str(SPRITE_JAM_DEATH_DIR / "death_spirte_2.png"),
    str(SPRITE_JAM_DEATH_DIR / "death_spirte_3.png"),
    str(SPRITE_JAM_DEATH_DIR / "death_spirte_4.png"),
]
SPRITE_JAM_DEATH = [
    str(SPRITE_JAM_DEATH_DIR / "death1.png"),
    str(SPRITE_JAM_DEATH_DIR / "death2.png"),
    str(SPRITE_JAM_DEATH_DIR / "death3.png"),
]

DEATH_POSE_DURATIONS = (0.22, 0.48, 0.38, 0.42, 0.75)
DEATH_OVERLAY_DURATION = 0.85
DEATH_POSE_SCALE = (1.0, 0.82, 1.12, 1.12, 1.12)
DEATH_POSE_DROP = (0.0, 0.0, 38.0, 38.0, 38.0)

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
KEY_FULLSCREEN = F11
KEY_BACK = ESCAPE

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
DIALOGUE_TYPEWRITER_VOLUME = 0.07
DIALOGUE_TYPEWRITER_INTERVAL = 0.08
DIALOGUE_GLITCH_VOLUME_CAP = 0.04
DIALOGUE_TEXT_RATIO = 0.70
DIALOGUE_BOX_LEFT = 64
DIALOGUE_BOX_RIGHT = int(SCREEN_WIDTH * DIALOGUE_TEXT_RATIO)
DIALOGUE_BOX_BOTTOM = 36
DIALOGUE_BOX_TOP = 336
DIALOGUE_FONT_SIZE = 25
DIALOGUE_PORTRAIT_PAD = -20
DIALOGUE_PORTRAIT_HEIGHT_RATIO = 0.6

INSPECT_DURATION = 0.55
INSPECT_ZOOM = 2.5
INSPECT_FADE_ALPHA = 175

ROOM_CORRIDOR = "room_1"
ROOM_BAR = "room_2"
ROOM_BEDROOM = "room_3"
ROOM_OFFICE = "room_4"
ROOM_VOID = "void"
SCENE_ROOM = "room"
SCENE_MENU = "menu"

SAVE_PATH = PROJECT_ROOT / "saves" / "autosave.json"

SPRITE_KEY = "assets/sprites/key.png"
SPRITE_POISON = "assets/sprites/poison.png"
SPRITE_ASHTRAY = "assets/sprites/ashtray.png"
SPRITE_DIARY = "assets/sprites/diaries.png"
SPRITE_FRAME = "assets/sprites/broken_frame.png"
SPRITE_HORSE = "assets/sprites/horse.png"
SPRITE_MR_P = "assets/sprites/shadow_man.png"
SPRITE_MR_P_GLITCH = "assets/sprites/glitch_man.png"
SPRITE_BOOKMARK_FRONT = "assets/sprites/bookmark/front_bookmark.png"
SPRITE_BOOKMARK_BACK = "assets/sprites/bookmark/back_bookmark.png"
SPRITE_LETTERS = "assets/sprites/Letters.png"
SPRITE_LUSTRE = "assets/sprites/lustre/lustre_x4.png"

SOUND_AMBIANCE = PROJECT_ROOT / "assets" / "sounds" / "ambiance_2.mp3"
SOUND_DISCORD = PROJECT_ROOT / "assets" / "sounds" / "erreur.mp3"
SOUND_POISON = PROJECT_ROOT / "assets" / "sounds" / "respiration_poison.mp3"
SOUND_GLASS = PROJECT_ROOT / "assets" / "sounds" / "verre_coupure.mp3"
SOUND_GLASS_BREAK = PROJECT_ROOT / "assets" / "sounds" / "verre_casser.mp3"
SOUND_DOOR = PROJECT_ROOT / "assets" / "sounds" / "grincement_porte.mp3"
SOUND_PAGE = PROJECT_ROOT / "assets" / "sounds" / "tourner_page.mp3"
SOUND_STATIC = PROJECT_ROOT / "assets" / "sounds" / "tremblement.mp3"
SOUND_MENU = PROJECT_ROOT / "assets" / "sounds" / "accueil.mp3"
SOUND_LUSTRE = PROJECT_ROOT / "assets" / "sounds" / "lustre.mp3"
SOUND_VOID = PROJECT_ROOT / "assets" / "sounds" / "neant.mp3"
SOUND_DISINTEGRATION = PROJECT_ROOT / "assets" / "sounds" / "desintegration_pere.mp3"

CREDITS_BACKGROUND = (
    PROJECT_ROOT / "assets" / "sprites" / "rooms" / "jeu_1920x1080" / "neant.png"
)
CREDITS_VEIL_COLOR = (8, 5, 10, 70)
CREDITS_SCROLL_SPEED = scale_h(80)
CREDITS_START_OFFSET = scale_h(30)
CREDITS_FADE_MARGIN = scale_h(130)
CREDITS_LOOP_GAP = scale_h(220)
CREDITS_TEXT_WIDTH = int(SCREEN_WIDTH * 0.8)
