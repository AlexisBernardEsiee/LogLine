import argparse

import arcade

from src import constants
from src.views.menu_view import MenuView


def _parse_size(value):
    try:
        width_text, height_text = value.lower().split("x", 1)
        width, height = int(width_text), int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Format attendu : LARGEURxHAUTEUR, ex. 1280x800") from exc
    if width < 1 or height < 1:
        raise argparse.ArgumentTypeError("La taille doit être positive")
    return width, height


class GameWindow(arcade.Window):

    def on_key_press(self, symbol, modifiers):
        if symbol == constants.KEY_FULLSCREEN:
            self.set_fullscreen(not self.fullscreen)


def main():
    parser = argparse.ArgumentParser(description="LogLine")
    parser.add_argument(
        "--size",
        type=_parse_size,
        default=(constants.WINDOW_DEFAULT_WIDTH, constants.WINDOW_DEFAULT_HEIGHT),
        help="Taille en mode fenêtre, ex. 1280x800 ou 1080x1080",
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Démarrer en fenêtre plutôt qu'en plein écran",
    )
    args = parser.parse_args()

    constants.load_fonts()
    width, height = args.size
    # width/height ignorés quand on est en plein écran, mais pyglet les retient : c'est la taille que reprendra la fenêtre au premier F11.
    window = GameWindow(
        width,
        height,
        constants.SCREEN_TITLE,
        resizable=True,
        fullscreen=not args.windowed,
    )
    window.set_minimum_size(constants.WINDOW_MIN_WIDTH, constants.WINDOW_MIN_HEIGHT)
    window.background_color = constants.LETTERBOX_COLOR
    window.set_update_rate(1 / constants.FPS)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
