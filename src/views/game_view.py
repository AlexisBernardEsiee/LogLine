import arcade

from src import constants
from src.entities.player import Player


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.keys_held = set()

    def setup(self):
        self.player = Player()
        self.player.center_x = constants.SCREEN_WIDTH / 2
        self.player.center_y = constants.PLAYER_HEIGHT / 2 + 40

    def on_show_view(self):
        self.window.background_color = arcade.color.GRAY

    def on_draw(self):
        self.clear()
        if self.player:
            arcade.draw_sprite(self.player)

    def on_update(self, delta_time):
        if self.player is None:
            return
        self.player.speed_x = 0
        if constants.KEY_LEFT in self.keys_held:
            self.player.speed_x -= constants.PLAYER_SPEED
        if constants.KEY_RIGHT in self.keys_held:
            self.player.speed_x += constants.PLAYER_SPEED
        self.player.update(delta_time)

    def on_key_press(self, key, modifiers):
        self.keys_held.add(key)

    def on_key_release(self, key, modifiers):
        self.keys_held.discard(key)
