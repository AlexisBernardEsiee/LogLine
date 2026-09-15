import arcade

from src import constants
from src.views.game_view import GameView


def main():
    window = arcade.Window(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        constants.SCREEN_TITLE,
    )
    window.set_update_rate(1 / constants.FPS)
    view = GameView()
    view.setup()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
