import arcade

from src import constants
from src.entities.player import Player
from src.systems.dialogue_manager import DialogueManager
from src.systems.room_manager import RoomManager
from src.ui.dialogue_box import DialogueBox
from src.ui.prompt import InteractionPrompt
from src.ui.tutorial_overlay import TutorialOverlay


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.state = constants.STATE_INTRO
        self.player = None
        self.keys_held = set()
        self.room_manager = RoomManager()
        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox()
        self.prompt = InteractionPrompt()
        self.tutorial = TutorialOverlay()
        self.background_image = None

    def setup(self):
        self.state = constants.STATE_INTRO
        self.player = None
        self.keys_held.clear()
        self.dialogue_manager.load_room(constants.ROOM_CORRIDOR)
        self.dialogue_manager.start("corridor_intro")
        self.dialogue_box.show(self.dialogue_manager.current())

    def on_show_view(self):
        if self.state == constants.STATE_INTRO:
            self.background_image = arcade.load_texture("assets/images/rooms/manoir.webp")
        else:
            self.window.background_color = (236, 224, 204)

    def on_draw(self):
        self.clear()
        if self.state == constants.STATE_INTRO:
            arcade.draw_texture_rect(
            self.background_image,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
        )

        if self.state == constants.STATE_EXPLORE:
            self.room_manager.draw()
            if self.player:
                arcade.draw_sprite(self.player)
            self.prompt.draw()
            self.tutorial.draw()
        self.dialogue_box.draw()

    def on_update(self, delta_time):
        self.dialogue_box.update(delta_time)
        if self.state != constants.STATE_EXPLORE or self.player is None:
            return
        if self.dialogue_manager.is_active:
            self.prompt.visible = False
            return

        self.player.speed_x = 0
        if constants.KEY_LEFT in self.keys_held:
            self.player.speed_x -= constants.PLAYER_SPEED
        if constants.KEY_RIGHT in self.keys_held:
            self.player.speed_x += constants.PLAYER_SPEED

        if self.player.speed_x != 0:
            self.tutorial.mark_moved()

        self.player.update(delta_time)
        nearby = self.room_manager.get_nearby_interactable(self.player)
        self.prompt.set_target(self.player, nearby)

    def on_key_press(self, key, modifiers):
        if self.dialogue_manager.is_active:
            if key in (constants.KEY_CONFIRM, constants.KEY_INTERACT, constants.KEY_SKIP):
                self._advance_dialogue()
            return
        if key == constants.KEY_INTERACT:
            self._interact()
            return
        self.keys_held.add(key)

    def on_key_release(self, key, modifiers):
        self.keys_held.discard(key)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.dialogue_manager.is_active:
            self._advance_dialogue()

    def _advance_dialogue(self):
        if self.dialogue_box.is_typing():
            self.dialogue_box.skip_typing()
            return
        ended = self.dialogue_manager.advance()
        if ended:
            self.dialogue_box.hide()
            if self.state == constants.STATE_INTRO:
                self._enter_corridor()
            return
        self.dialogue_box.show(self.dialogue_manager.current())

    def _enter_corridor(self):
        self.state = constants.STATE_EXPLORE
        self.room_manager.load_room(constants.ROOM_CORRIDOR)
        self.player = Player()
        self.player.center_x = self.room_manager.entry_x
        self.player.bottom = self.room_manager.floor_y
        self.keys_held.clear()
        self.tutorial.show()
        self.window.background_color = (236, 224, 204)

    def _interact(self):
        target = self.room_manager.get_nearby_interactable(self.player)
        if target is None:
            return
        if target.leads_to:
            self._change_room(target.leads_to)
            return
        if target.dialogue_id:
            if self.dialogue_manager.start(target.dialogue_id):
                self.dialogue_box.show(self.dialogue_manager.current())

    def _change_room(self, room_id):
        self.room_manager.load_room(room_id)
        self.dialogue_manager.load_room(room_id)
        self.player.center_x = self.room_manager.entry_x
        self.player.bottom = self.room_manager.floor_y
        self.keys_held.clear()
        self.prompt.visible = False
        self.tutorial.visible = False
