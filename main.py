import arcade

from src import constants
from src.views.menu_view import MenuView


def main():
    constants.load_fonts()
    window = arcade.Window(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        constants.SCREEN_TITLE,
    )
    window.set_update_rate(1 / constants.FPS)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
