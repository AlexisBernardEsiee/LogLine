import arcade

from src import constants
from src.camera import WorldCamera
from src.entities.player import Player
from src.systems.audio_manager import AudioManager
from src.systems.dialogue_manager import DialogueManager
from src.systems.game_state import GameState
from src.systems.room_manager import RoomManager
from src.ui.death_effect import DeathEffect
from src.ui.debug_grid import DebugGrid
from src.ui.dialogue_box import DialogueBox
from src.ui.inspect_effect import InspectEffect
from src.ui.prompt import InteractionPrompt
from src.ui.tutorial_overlay import TutorialOverlay

HOUSE_THOUGHT_X = 1450


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
        self.death = DeathEffect()
        self.state = GameState()
        self._pending_tutorial = False
        self._pending_dialogue = None
        self._pending_death = None
        self._pending_reveal = None
        self._pending_give = None
        self.audio = AudioManager()
        self.dialogue_box = DialogueBox(audio_manager=self.audio)

    def setup(self, new_game=False):
        self.keys_held.clear()
        self._pending_tutorial = False
        self._pending_dialogue = None
        self._pending_death = None
        self._pending_reveal = None
        self._pending_give = None
        self.inspect.active = False
        self.death.active = False
        if new_game:
            self.state = GameState()
            self.state.save()
        else:
            self.state = GameState.load()
        self._enter_room(self.state.room_id, from_room_id=self.state.from_room_id)
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
        self.room_manager.draw(self.state)
        if self.room_manager.shows_world and self.player and not self.death.hiding_world:
            arcade.draw_sprite(self.player)
            if not self.death.blocking:
                self.prompt.draw()
                self.tutorial.draw()
        if not self.death.hiding_world:
            self.inspect.draw()
        self.death.draw()
        self.dialogue_box.draw()
        if not self.death.blocking:
            self.debug_grid.draw(self.room_manager, self.player)

    def on_update(self, delta_time):
        self.audio.update()
        self.dialogue_box.update(delta_time)
        self.inspect.update(delta_time)
        self.death.update(delta_time)

        if self.death.just_void:
            if not self._start_dialogue(self.death.spec.get("void_dialogue")):
                self._respawn_after_death()
                self.death.notify_void_done()
        if self.death.just_returned:
            self.audio.set_music_volume(0.4)
            aftermath = self.death.spec.get("aftermath_dialogue")
            if aftermath:
                self._start_dialogue(aftermath)

        if self.inspect.just_opened and self._pending_dialogue:
            self._start_dialogue(self._pending_dialogue)
            self._pending_dialogue = None

        if self.player is None or not self.room_manager.shows_world:
            return

        if self.death.blocking or self.dialogue_manager.is_active or self.inspect.active:
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
            if self.tutorial.visible:
                self.tutorial.mark_moved()
                self.state.set_flag("tutorial_done")

        self.player.update(delta_time)
        self._maybe_house_thought()
        nearby = self.room_manager.get_nearby_interactable(self.player, self.state)
        self.prompt.set_target(self.player, nearby)

    def on_key_press(self, key, modifiers):
        if key == constants.KEY_FULLSCREEN:
            self.window.set_fullscreen(not self.window.fullscreen)
            return
        if self.death.blocking and not self.dialogue_manager.is_active:
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
        if self.death.blocking and not self.dialogue_manager.is_active:
            return
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
        target = self.room_manager.get_interactable_at(world_x, world_y, self.state)
        if target is not None:
            self._interact_with(target)

    def _enter_room(self, room_id, from_room_id=None):
        self.room_manager.show(room_id, from_room_id=from_room_id)
        self.dialogue_manager.load_room(room_id)
        self._spawn_player()
        self.prompt.visible = False
        self.tutorial.visible = False
        self._pending_dialogue = None
        self._pending_death = None
        self.inspect.active = False
        self.inspect.texture = None
        self.state.room_id = room_id
        self.state.from_room_id = from_room_id
        self.state.save()
        on_enter = self.room_manager.consume_on_enter(self.state)
        if on_enter:
            self._pending_tutorial = (
                self.room_manager.tutorial and not self.state.flag("tutorial_done")
            )
            self._start_dialogue(on_enter)
        elif self.room_manager.tutorial and not self.state.flag("tutorial_done"):
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

    def _maybe_house_thought(self):
        if self.room_manager.current_room_id != constants.ROOM_CORRIDOR:
            return
        if self.state.flag("seen_house_thought"):
            return
        if self.player.center_x < HOUSE_THOUGHT_X:
            return
        self.state.set_flag("seen_house_thought")
        self._start_dialogue("house_thought")

    def _start_dialogue(self, scene_id):
        if not scene_id:
            return False
        if self.dialogue_manager.start(scene_id):
            self._apply_line(self.dialogue_manager.current())
            return True
        return False

    def _apply_line(self, line):
        if line is None:
            return
        self.dialogue_box.show(line)
        if "scene" in line:
            self.room_manager.set_scene(line["scene"])
        sfx = line.get("sfx")
        if sfx:
            self.audio.play_sfx(sfx, constants.PROJECT_ROOT / sfx)

    def _advance_dialogue(self):
        if self.dialogue_box.is_typing():
            self.dialogue_box.skip_typing()
            return
        ended = self.dialogue_manager.advance()
        if ended:
            self.dialogue_box.hide()
            self.room_manager.set_scene(constants.SCENE_ROOM)
            self.inspect.close()
            self._finish_interaction()
            if self.death.phase == "void":
                self._respawn_after_death()
                self.death.notify_void_done()
                return
            if self._pending_tutorial:
                self.tutorial.show()
                self._pending_tutorial = False
            return
        self._apply_line(self.dialogue_manager.current())

    def _finish_interaction(self):
        if self._pending_reveal:
            self.state.set_flag(self._pending_reveal)
            self._pending_reveal = None
        if self._pending_give:
            self.state.set_flag(self._pending_give)
            self._pending_give = None
        if self._pending_death:
            spec = self._pending_death
            self._pending_death = None
            self._begin_death(spec)

    def _begin_death(self, spec):
        extra = 1.0 if spec.get("effect") == "green_glitch" else 0.0
        extra += 0.35 * int(self.state.flags.get("death_count", 0))
        self.audio.set_music_volume(0.05)
        sfx = spec.get("sfx")
        if sfx:
            self.audio.play_sfx(sfx, constants.PROJECT_ROOT / sfx, volume_modifier=1.2)
        self.death.start(spec, extra_hold=extra)

    def _respawn_after_death(self):
        flag = self.death.spec.get("flag")
        if flag:
            self.state.set_flag(flag)
        self.state.bump_death()
        room_id = self.room_manager.current_room_id
        self.room_manager.show(room_id)
        self.dialogue_manager.load_room(room_id)
        self._spawn_player()
        self.prompt.visible = False
        self.keys_held.clear()

    def _interact(self):
        target = self.room_manager.get_nearby_interactable(self.player, self.state)
        self._interact_with(target)

    def _interact_with(self, target):
        if target is None:
            return
        if target.leads_to:
            if target.requires and not self.state.flag(target.requires):
                if target.locked_dialogue:
                    self._start_dialogue(target.locked_dialogue)
                return
            if target.sfx:
                self.audio.play_sfx(target.sfx, constants.PROJECT_ROOT / target.sfx)
            self._enter_room(target.leads_to, from_room_id=self.room_manager.current_room_id)
            return

        death = target.death
        already_died = death and self.state.flag(death.get("flag"))
        dialogue_id = target.done_dialogue if already_died else target.dialogue_id
        self._pending_reveal = target.reveals
        self._pending_give = target.gives
        self._pending_death = None if already_died else death

        if dialogue_id:
            if self._start_inspect(target):
                self._pending_dialogue = dialogue_id
                return
            self._start_dialogue(dialogue_id)
            return
        self._finish_interaction()

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
