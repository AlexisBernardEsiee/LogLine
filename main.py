import arcade

from src import constants
from src.views.credits_view import CreditsView
from src.views.game_view import GameView


def main():
    constants.load_fonts()
    window = arcade.Window(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        constants.SCREEN_TITLE,
    )
    window.set_update_rate(1 / constants.FPS)
    # TEMPORAIRE : on demarre sur les credits pour les developper sans menu.
    #     view = GameView()
    #     view.setup()
    view = CreditsView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
