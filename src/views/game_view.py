import arcade
import random

from src import constants
from src.camera import WorldCamera
from src.entities.player import Player
from src.systems.dialogue_manager import DialogueManager
from src.systems.game_state import GameState
from src.systems.room_manager import RoomManager
from src.ui.death_effect import DeathEffect
from src.ui.debug_grid import DebugGrid
from src.ui.dialogue_box import DialogueBox
from src.ui.inspect_effect import InspectEffect
from src.ui.lustre import LustreProp
from src.ui.prompt import InteractionPrompt
from src.ui.tutorial_overlay import TutorialOverlay
from src.views.pause_view import PauseView

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
        self.lustre = LustreProp()
        self.death = DeathEffect(constants.SPRITE_JAM_DEATH)
        self.state = GameState()
        self._pending_tutorial = False
        self._pending_dialogue = None
        self._pending_death = None
        self._pending_reveal = None
        self._pending_give = None
        self._pending_ending = False
        self._object_search = False
        self._pending_lustre_death = None
        self._fall = None
        self._void_glitch_rects = []
        self._void_glitch_t = 0.0
        self.audio = None
        self.dialogue_box = DialogueBox(audio_manager=None)

    def setup(self, new_game=False):
        self.audio = self.window.audio
        self.dialogue_box.audio = self.window.audio
        self.keys_held.clear()
        self._pending_tutorial = False
        self._pending_dialogue = None
        self._pending_death = None
        self._pending_reveal = None
        self._pending_give = None
        self._pending_ending = False
        self._object_search = False
        self._pending_lustre_death = None
        self._fall = None
        self.inspect.active = False
        self.death.active = False
        if new_game:
            self.state = GameState()
            self.state.save()
        else:
            self.state = GameState.load()
        self._enter_room(self.state.room_id, from_room_id=self.state.from_room_id)
        if self.state.room_id != constants.ROOM_VOID:
            self._play_world_music()

    def on_show_view(self):
        self.window.background_color = constants.LETTERBOX_COLOR
        self.world_camera.fit_to_window()
        self.audio = self.window.audio
        self.dialogue_box.audio = self.window.audio
        
        # Stop la musique du menu avant de lancer le son d'ambiance
        self.audio.stop_music()
        self.audio.play_music(
            constants.PROJECT_ROOT / "assets" / "sounds" / "ambiance1.mp3",
            volume=0.4,
            loop=True,
        )

    def on_resize(self, width, height):
        self.world_camera.fit_to_window()

    def on_draw(self):
        self.world_camera.begin_frame()
        self.room_manager.draw(self.state)
        if self.room_manager.shows_world:
            if self.player and not self.death.hide_player:
                if not (self._fall and self._fall["phase"] == "out"):
                    arcade.draw_sprite(self.player)
            self._draw_lustre()
            if not self.death.blocking and not self._fall and not self.lustre.blocking:
                self.prompt.draw()
                self.tutorial.draw()
        if not self.death.hiding_world:
            self.inspect.draw()
        self._draw_void_glitch()
        self.death.draw()
        self._draw_fall()
        self.dialogue_box.draw()
        if not self.death.blocking and not self._fall:
            self.debug_grid.draw(self.room_manager, self.player)

    def on_update(self, delta_time):
        if self.audio:
            self.audio.update()
        self.dialogue_box.update(delta_time)
        self.inspect.update(delta_time)
        self.death.update(delta_time)
        self.lustre.update(delta_time)
        if self.lustre.just_landed and self._pending_lustre_death:
            spec = self._pending_lustre_death
            self._pending_lustre_death = None
            self._begin_death(spec, skip_sfx=True)

        if self.death.just_void:
            scene = self.death.spec.get("void_scene")
            if scene:
                self.room_manager.set_scene(scene)
            if self._start_dialogue(self.death.spec.get("void_dialogue")):
                pass
            elif not self.death.spec.get("void_hold"):
                self._respawn_after_death()
                self.death.notify_void_done()
        if self.death.just_hold_done:
            self._respawn_after_death()
            self.death.notify_void_done()
        if self.death.just_returned:
            if self.room_manager.current_room_id != constants.ROOM_VOID:
                self._play_world_music()
            aftermath = self.death.spec.get("aftermath_dialogue")
            if aftermath:
                self._start_dialogue(aftermath)

        if self.inspect.just_opened and self._pending_dialogue:
            self._start_dialogue(self._pending_dialogue)
            self._pending_dialogue = None

        if self._update_fall(delta_time):
            return

        if self.player is None or not self.room_manager.shows_world:
            return

        if self.death.blocking or self.dialogue_manager.is_active or self.inspect.active or self.lustre.blocking:
            self.player.speed_x = 0
            self._apply_search_pose()
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
        self._maybe_auto_deaths()
        nearby = self.room_manager.get_nearby_interactable(self.player, self.state)
        self.prompt.set_target(self.player, nearby)
        self._apply_search_pose(nearby)

    def on_key_press(self, key, modifiers):
        if key == constants.KEY_BACK:
            if self._fall or self.lustre.blocking or (self.death.blocking and not self.dialogue_manager.is_active):
                return
            self._pause()
            return
        if self._fall or self.lustre.blocking:
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
        if self._fall or self.lustre.blocking:
            return
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

    def _pause(self):
        self.keys_held.clear()
        if self.player is not None:
            self.player.speed_x = 0
        self.window.show_view(PauseView(self))

    def _enter_room(self, room_id, from_room_id=None):
        self.room_manager.show(room_id, from_room_id=from_room_id)
        self.dialogue_manager.load_room(room_id)
        self._spawn_player()
        self.prompt.visible = False
        self.tutorial.visible = False
        self._pending_dialogue = None
        self._pending_death = None
        self._pending_lustre_death = None
        self._object_search = False
        self.inspect.active = False
        self.inspect.texture = None
        self.lustre.configure(self.room_manager.lustre_prop)
        if self.state.flag("died_lustre"):
            self.lustre.hide()
        self.state.room_id = room_id
        self.state.from_room_id = from_room_id
        self.state.save()
        if room_id == constants.ROOM_VOID:
            self.audio.play_music(constants.SOUND_VOID, volume=0.38, loop=True)
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
        if line.get("inspect_sprite"):
            self.inspect.set_sprite(line["inspect_sprite"])
        if line.get("ending"):
            self._pending_ending = True
        sfx = line.get("sfx") or ""
        if "tremblement" not in sfx and "erreur" not in sfx:
            self.audio.stop_glitch()
        if sfx:
            self.audio.play_sfx(
                sfx,
                constants.PROJECT_ROOT / sfx,
                volume_modifier=float(line.get("sfx_volume", 1.0)),
            )

    def _advance_dialogue(self):
        if self.dialogue_box.is_typing():
            self.dialogue_box.skip_typing()
            return
        ended = self.dialogue_manager.advance()
        if ended:
            self.dialogue_box.hide()
            self.audio.stop_glitch()
            self.room_manager.set_scene(constants.SCENE_ROOM)
            self.inspect.close()
            self._object_search = False
            if self._pending_ending:
                self._pending_ending = False
                self._start_ending()
                return
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

    def _begin_death(self, spec, skip_sfx=False):
        extra = 1.0 if spec.get("effect") == "green_glitch" else 0.0
        extra += 0.35 * int(self.state.flags.get("death_count", 0))
        if spec.get("effect") == "silence":
            extra = 0.0
            self.audio.stop_music()
            self.audio.stop_glitch()
        else:
            self.audio.set_music_volume(0.05)
        sfx = spec.get("sfx")
        if sfx and not skip_sfx:
            modifier = float(spec.get("sfx_volume", 0.7))
            self.audio.play_sfx(sfx, constants.PROJECT_ROOT / sfx, volume_modifier=modifier)
        self.death.start(spec, extra_hold=extra)

    def _play_world_music(self):
        path = getattr(constants, "SOUND_AMBIANCE", None) or (
            constants.PROJECT_ROOT / "assets" / "sounds" / "ambiance_2.mp3"
        )
        self.audio.play_music(path, volume=0.4, loop=True)

    def _respawn_after_death(self):
        flag = self.death.spec.get("flag")
        if flag:
            self.state.set_flag(flag)
        self.state.bump_death()
        room_id = self.room_manager.current_room_id
        self.room_manager.set_scene(constants.SCENE_ROOM)
        self.room_manager.show(room_id)
        self.lustre.configure(self.room_manager.lustre_prop)
        if self.state.flag("died_lustre"):
            self.lustre.hide()
        self.dialogue_manager.load_room(room_id)
        self._spawn_player()
        respawn_x = self.death.spec.get("respawn_x")
        if respawn_x is not None and self.player:
            self.player.place_on_floor(
                respawn_x,
                self.room_manager.floor_y,
                facing_right=True,
            )
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
                    self._object_search = True
                    self._start_dialogue(target.locked_dialogue)
                return
            if target.sfx:
                self.audio.play_sfx(target.sfx, constants.PROJECT_ROOT / target.sfx)
            if target.transition == "fall":
                self._start_fall(target.leads_to)
                return
            self._enter_room(target.leads_to, from_room_id=self.room_manager.current_room_id)
            return

        death = target.death
        already_died = death and self.state.flag(death.get("flag"))
        already_seen = bool(target.reveals and self.state.flag(target.reveals) and target.done_dialogue)
        dialogue_id = target.done_dialogue if (already_died or already_seen) else target.dialogue_id
        self._pending_reveal = None if already_seen else target.reveals
        self._pending_give = target.gives
        self._pending_death = None if already_died else death
        self._object_search = True

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
            texture = self.room_manager.current_background_texture(self.state)
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
<<<<<<< HEAD
        return False
=======
        return False

    def _target_is_search(self, target):
        if target is None:
            return False
        if target.kind in ("door", "hole"):
            return bool(target.requires and not self.state.flag(target.requires))
        return True

    def _apply_search_pose(self, nearby=None):
        if self.player is None:
            return
        searching = False
        if not self.death.blocking and self.room_manager.current_room_id != constants.ROOM_VOID:
            if self.inspect.active or self._object_search:
                searching = True
            else:
                if nearby is None:
                    nearby = self.room_manager.get_nearby_interactable(self.player, self.state)
                searching = self._target_is_search(nearby)
        self.player.searching = searching
        if self.player.speed_x == 0:
            self.player.apply_idle_pose()

    def _maybe_auto_deaths(self):
        if self.player is None or self.death.blocking or self.lustre.blocking:
            return
        for spec in self.room_manager.auto_deaths:
            requires = spec.get("requires")
            if requires:
                names = requires if isinstance(requires, (list, tuple)) else [requires]
                if any(not self.state.flag(name) for name in names):
                    continue
            if spec.get("unless") and self.state.flag(spec["unless"]):
                continue
            zone = spec.get("x", [0, 0])
            if len(zone) < 2:
                continue
            if zone[0] <= self.player.center_x <= zone[1]:
                death = spec.get("death") or {}
                if death.get("id") == "lustre" and self.lustre.texture:
                    self._start_lustre_fall(death)
                else:
                    self._begin_death(death)
                return

    def _start_lustre_fall(self, spec):
        self.keys_held.clear()
        if self.player is not None:
            self.player.speed_x = 0
        self._pending_lustre_death = spec
        self.audio.stop_music()
        sfx = spec.get("sfx")
        if sfx:
            self.audio.play_sfx(
                sfx,
                constants.PROJECT_ROOT / sfx,
                volume_modifier=float(spec.get("sfx_volume", 0.85)),
            )
        self.lustre.start_fall()

    def _draw_lustre(self):
        if self.room_manager.current_room_id != constants.ROOM_OFFICE:
            return
        if self.state.flag("died_lustre") and self.lustre.phase not in ("falling", "landed"):
            return
        self.lustre.draw()

    def _start_fall(self, room_id):
        self.keys_held.clear()
        if self.player is not None:
            self.player.speed_x = 0
        self.audio.stop_music()
        self._fall = {"t": 0.0, "room": room_id, "phase": "out"}

    def _update_fall(self, delta_time):
        if not self._fall:
            return False
        self._fall["t"] += delta_time
        if self._fall["phase"] == "out" and self._fall["t"] >= 1.15:
            self._enter_room(self._fall["room"], from_room_id=self.room_manager.current_room_id)
            self._fall = {"t": 0.0, "room": self._fall["room"], "phase": "in"}
        elif self._fall["phase"] == "in" and self._fall["t"] >= 0.9:
            self._fall = None
            return False
        return True

    def _draw_fall(self):
        if not self._fall:
            return
        if self._fall["phase"] == "out":
            alpha = min(1.0, self._fall["t"] / 0.85)
        else:
            alpha = max(0.0, 1.0 - self._fall["t"] / 0.9)
        if alpha <= 0.02:
            return
        arcade.draw_lrbt_rectangle_filled(
            0,
            constants.SCREEN_WIDTH,
            0,
            constants.SCREEN_HEIGHT,
            (4, 2, 6, int(255 * alpha)),
        )

    def _draw_void_glitch(self):
        if self.room_manager.current_room_id != constants.ROOM_VOID:
            return
        if self.death.blocking:
            return
        self._void_glitch_t += 1
        if self._void_glitch_t % 8 == 1:
            self._void_glitch_rects = []
            for _ in range(16):
                width = random.randint(6, 70)
                height = random.randint(3, 16)
                left = random.randint(0, max(1, constants.SCREEN_WIDTH - width))
                bottom = random.randint(0, max(1, constants.SCREEN_HEIGHT - height))
                self._void_glitch_rects.append((left, bottom, width, height))
        for left, bottom, width, height in self._void_glitch_rects:
            arcade.draw_lbwh_rectangle_filled(
                left, bottom, width, height, (48, 255, 92, 28)
            )

    def _start_ending(self):
        self.audio.stop_music()
        self.audio.stop_glitch()
        from src.views.fin_view import FinView

        self.window.show_view(FinView())
>>>>>>> origin/main
