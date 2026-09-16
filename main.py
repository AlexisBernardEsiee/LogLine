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


def main():
    parser = argparse.ArgumentParser(description="LogLine")
    parser.add_argument(
        "--size",
        type=_parse_size,
        default=(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
        help="Taille initiale de la fenêtre, ex. 1280x800 ou 1080x1080",
    )
    parser.add_argument("--fullscreen", action="store_true")
    args = parser.parse_args()

    constants.load_fonts()
    width, height = args.size
    window = arcade.Window(
        width,
        height,
        constants.SCREEN_TITLE,
        resizable=True,
        fullscreen=args.fullscreen,
    )
    window.set_minimum_size(constants.WINDOW_MIN_WIDTH, constants.WINDOW_MIN_HEIGHT)
    window.background_color = constants.LETTERBOX_COLOR
    window.set_update_rate(1 / constants.FPS)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
