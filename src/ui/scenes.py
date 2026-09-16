import json

import arcade

from src import constants


def load_scene_texture(name):
    scenes = json.loads(constants.DATA_SCENES.read_text(encoding="utf-8"))
    return arcade.load_texture(constants.PROJECT_ROOT / scenes[name]["path"])