import arcade

from src import constants
from src.camera import WorldCamera
from src.entities.player import Player
from src.systems.dialogue_manager import DialogueManager
from src.systems.room_manager import RoomManager
from src.ui.debug_grid import DebugGrid
from src.ui.dialogue_box import DialogueBox
from src.ui.inspect_effect import InspectEffect
from src.ui.prompt import InteractionPrompt
from src.ui.tutorial_overlay import TutorialOverlay
from src.systems.audio_manager import AudioManager


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.keys_held = set()
        self.world_camera = WorldCamera(self.window)
        self.room_manager = RoomManager()
        self.dialogue_manager = DialogueManager()
        self.prompt = InteractionPrompt()
        self.tutorial = TutorialOverlay()
        self.debug_grid = DebugGrid()
        self.inspect = InspectEffect()
        self._pending_tutorial = False
        self._pending_dialogue = None
        self.audio = AudioManager()
        self.dialogue_box = DialogueBox(audio_manager=self.audio)


    def setup(self):
        self.keys_held.clear()
        self._pending_tutorial = False
        self._pending_dialogue = None
        self.inspect.active = False
        self._enter_room(constants.ROOM_CORRIDOR)
        self.audio.play_music(
            constants.PROJECT_ROOT / "assets" / "sounds" / "ambiance.mp3",
            volume=0.4,
            loop=True,
        )

    def on_show_view(self):
        self.window.background_color = constants.LETTERBOX_COLOR
        self.world_camera.fit_to_window()

    def on_resize(self, width, height):
        self.world_camera.fit_to_window()

    def on_draw(self):
        self.world_camera.begin_frame()
        self.room_manager.draw()
        if self.room_manager.shows_world and self.player:
            arcade.draw_sprite(self.player)
            self.prompt.draw()
            self.tutorial.draw()
        self.inspect.draw()
        self.dialogue_box.draw()
        self.debug_grid.draw(self.room_manager, self.player)

    def on_update(self, delta_time):
        self.dialogue_box.update(delta_time)
        self.inspect.update(delta_time)
        if self.inspect.just_opened and self._pending_dialogue:
            self._start_dialogue(self._pending_dialogue)
            self._pending_dialogue = None

        if self.player is None or not self.room_manager.shows_world:
            return

        if self.dialogue_manager.is_active or self.inspect.active:
            self.player.speed_x = 0
            self.player.update(delta_time)
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
        if key == constants.KEY_FULLSCREEN:
            self.window.set_fullscreen(not self.window.fullscreen)
            return
        if key == constants.KEY_GRID:
            self.debug_grid.toggle()
            return
        if key == constants.KEY_COPY_HITBOX and self.debug_grid.visible:
            self.debug_grid.copy_last()
            return
        if self.inspect.active and not self.inspect.closing and not self.dialogue_manager.is_active:
            if key in (constants.KEY_CONFIRM, constants.KEY_INTERACT, constants.KEY_SKIP):
                self.inspect.skip_open()
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
        world_x, world_y = self.world_camera.to_world(x, y)
        self.debug_grid.on_mouse_motion(world_x, world_y)

    def on_mouse_press(self, x, y, button, modifiers):
        world_x, world_y = self.world_camera.to_world(x, y)
        if self.debug_grid.on_mouse_press(world_x, world_y, button):
            return
        if self.inspect.active and not self.inspect.closing and not self.dialogue_manager.is_active:
            self.inspect.skip_open()
            return
        if self.dialogue_manager.is_active:
            self._advance_dialogue()
            return
        if not self.room_manager.shows_world:
            return
        target = self.room_manager.get_interactable_at(world_x, world_y)
        if target is not None:
            self._interact_with(target)

    def _enter_room(self, room_id, from_room_id=None):
        self.room_manager.show(room_id, from_room_id=from_room_id)
        self.dialogue_manager.load_room(room_id)
        self._spawn_player()
        self.prompt.visible = False
        self.tutorial.visible = False
        self._pending_dialogue = None
        self.inspect.active = False
        self.inspect.texture = None
        on_enter = self.room_manager.consume_on_enter()
        if on_enter:
            self._pending_tutorial = self.room_manager.tutorial
            self._start_dialogue(on_enter)
        elif self.room_manager.tutorial:
            self.tutorial.show()

    def _spawn_player(self):
        if self.player is None:
            self.player = Player()
        self.player.place_on_floor(
            self.room_manager.entry_x,
            self.room_manager.floor_y,
            facing_right=self.room_manager.entry_facing_right,
        )
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
            self.inspect.close()
            if self._pending_tutorial:
                self.tutorial.show()
                self._pending_tutorial = False
            return
        self._apply_line(self.dialogue_manager.current())

    def _interact(self):
        target = self.room_manager.get_nearby_interactable(self.player)
        self._interact_with(target)

    def _interact_with(self, target):
        if target is None:
            return
        if target.leads_to:
            self._enter_room(target.leads_to, from_room_id=self.room_manager.current_room_id)
            return
        if target.dialogue_id:
            if self._start_inspect(target):
                self._pending_dialogue = target.dialogue_id
                return
            self._start_dialogue(target.dialogue_id)

    def _start_inspect(self, target):
        if not target.inspect:
            return False
        effect = target.inspect.get("effect", "fade_zoom")
        zoom = target.inspect.get("zoom")
        duration = target.inspect.get("duration")
        if effect == "fade_zoom":
            texture = self.room_manager.current_background_texture()
            return self.inspect.start_from_decor(
                texture, target.hitbox, zoom=zoom, duration=duration
            )
        if effect == "sprite":
            return self.inspect.start_from_sprite(
                target.inspect.get("sprite"),
                target.hitbox,
                zoom=zoom,
                duration=duration,
            )
        return False
