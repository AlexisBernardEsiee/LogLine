import arcade

from src import constants
from src.entities.player import Player
from src.systems.dialogue_manager import DialogueManager
from src.systems.room_manager import RoomManager
from src.ui.debug_grid import DebugGrid
from src.ui.dialogue_box import DialogueBox
from src.ui.prompt import InteractionPrompt
from src.ui.tutorial_overlay import TutorialOverlay


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.keys_held = set()
        self.room_manager = RoomManager()
        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox()
        self.prompt = InteractionPrompt()
        self.tutorial = TutorialOverlay()
        self.debug_grid = DebugGrid()
        self._pending_tutorial = False

    def setup(self):
        self.keys_held.clear()
        self._pending_tutorial = False
        self._enter_room(constants.ROOM_CORRIDOR)

    def on_show_view(self):
        self.window.background_color = (8, 8, 10)

    def on_draw(self):
        self.clear()
        self.room_manager.draw()
        if self.room_manager.shows_world and self.player:
            arcade.draw_sprite(self.player)
            self.prompt.draw()
            self.tutorial.draw()
        self.dialogue_box.draw()
        self.debug_grid.draw(self.room_manager, self.player)

    def on_update(self, delta_time):
        self.dialogue_box.update(delta_time)
        if self.player is None or not self.room_manager.shows_world:
            return

        if self.dialogue_manager.is_active:
            self.player.speed_x = 0
            self.player.update(delta_time)
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
        if key == constants.KEY_GRID:
            self.debug_grid.toggle()
            return
        if key == constants.KEY_COPY_HITBOX and self.debug_grid.visible:
            self.debug_grid.copy_last()
            return
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

    def on_mouse_motion(self, x, y, dx, dy):
        self.debug_grid.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.debug_grid.on_mouse_press(x, y, button):
            return
        if self.dialogue_manager.is_active:
            self._advance_dialogue()

    def _enter_room(self, room_id):
        self.room_manager.show(room_id)
        self.dialogue_manager.load_room(room_id)
        self._spawn_player()
        self.prompt.visible = False
        self.tutorial.visible = False
        on_enter = self.room_manager.consume_on_enter()
        if on_enter:
            self._pending_tutorial = self.room_manager.tutorial
            self._start_dialogue(on_enter)
        elif self.room_manager.tutorial:
            self.tutorial.show()

    def _spawn_player(self):
        if self.player is None:
            self.player = Player()
        self.player.place_on_floor(self.room_manager.entry_x, self.room_manager.floor_y)
        self.keys_held.clear()

    def _start_dialogue(self, scene_id):
        if self.dialogue_manager.start(scene_id):
            self._apply_line(self.dialogue_manager.current())

    def _apply_line(self, line):
        if line is None:
            return
        self.dialogue_box.show(line)
        if "scene" in line:
            self.room_manager.set_scene(line["scene"])

    def _advance_dialogue(self):
        if self.dialogue_box.is_typing():
            self.dialogue_box.skip_typing()
            return
        ended = self.dialogue_manager.advance()
        if ended:
            self.dialogue_box.hide()
            self.room_manager.set_scene(constants.SCENE_ROOM)
            if self._pending_tutorial:
                self.tutorial.show()
                self._pending_tutorial = False
            return
        self._apply_line(self.dialogue_manager.current())

    def _interact(self):
        target = self.room_manager.get_nearby_interactable(self.player)
        if target is None:
            return
        if target.leads_to:
            self._enter_room(target.leads_to)
            return
        if target.dialogue_id:
            self._start_dialogue(target.dialogue_id)
