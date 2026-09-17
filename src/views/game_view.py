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
from src.ui.bookshelf import BookshelfOverlay
from src.ui.inspect_effect import InspectEffect
from src.ui.keypad import KeypadOverlay
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
        self.bookshelf = BookshelfOverlay()
        self.keypad = KeypadOverlay()
        self._keypad_target = None
        self.death = DeathEffect(constants.SPRITE_JAM_DEATH)
        self.state = GameState()
        self._pending_tutorial = False
        self._pending_dialogue = None
        self._pending_death = None
        self._choice_death = None
        self._choice_fall = None
        self._pending_fall = None
        self._pending_reveal = None
        self._pending_give = None
        self._pending_ending = False
        self._object_search = False
        self._pending_lustre_death = None
        self._fall = None
        self._door_fade_texture = None
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
        self._pending_fall = None
        self._pending_reveal = None
        self._pending_give = None
        self._pending_ending = False
        self._object_search = False
        self._pending_lustre_death = None
        self._fall = None
        self.inspect.active = False
        self.death.active = False
        if new_game:
            self.state.set_flag("seen_catalogue")
            self.state = GameState()
            self.state.save()
        else:
            self.state = GameState.load()
        self._enter_room(self.state.room_id, from_room_id=self.state.from_room_id)
        self._ensure_door_fade_texture()
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
                if not (self._fall and self._fall["phase"] in ("out", "hold")):
                    arcade.draw_sprite(self.player)
            self._draw_lustre()
            if not self.death.blocking and not self._fall and not self.lustre.blocking:
                self.prompt.draw()
                self.tutorial.draw()
        if not self.death.hiding_world:
            self.inspect.draw()
            self.bookshelf.draw()
            self.keypad.draw()
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
        if self.player and self.death.playing_pose:
            self.player.apply_death_pose(self.death.pose_index)
        self.lustre.update(delta_time)
        self.keypad.update(delta_time)
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

        if (
            self.death.blocking
            or self.dialogue_manager.is_active
            or self.inspect.active
            or self.lustre.blocking
            or self._overlay_active()
        ):
            self.player.speed_x = 0
            if not self.player.dying:
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
        self._apply_collisions()
        self._maybe_house_thought()
        self._maybe_auto_deaths()
        if self._maybe_auto_exits():
            return
        nearby = self.room_manager.get_nearby_interactable(self.player, self.state)
        if str(self.room_manager.current_room_id).startswith("vide_"):
            self.prompt.visible = False
        else:
            self.prompt.set_target(self.player, nearby)
        self._apply_search_pose(nearby)

    def on_key_press(self, key, modifiers):
        if self._overlay_active() and not self.dialogue_manager.is_active:
            self._overlay_key_press(key)
            return
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
            if self.dialogue_box.has_choices():
                if key == arcade.key.UP:
                    self.dialogue_box.move_choice(-1)
                    return

                if key == arcade.key.DOWN:
                    self.dialogue_box.move_choice(1)
                    return

                if key in (constants.KEY_CONFIRM, constants.KEY_SKIP):
                    choice_index = self.dialogue_box.get_selected_choice()
                    choice = self.dialogue_manager.get_choices()[choice_index]
                    self._handle_dialogue_choice(choice)
                    return
                
                return

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
        if self.keypad.active:
            self.keypad.on_mouse_motion(world_x, world_y)

    def on_mouse_press(self, x, y, button, modifiers):
        world_x, world_y = self.world_camera.to_world(x, y)
        if self._fall or self.lustre.blocking:
            return
        if self.death.blocking and not self.dialogue_manager.is_active:
            return
        if self.debug_grid.on_mouse_press(world_x, world_y, button):
            return
        if self._overlay_active() and not self.dialogue_manager.is_active:
            self._overlay_mouse_press(world_x, world_y)
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
        self.bookshelf.close()
        self.keypad.close()
        self._keypad_target = None
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
        x = self.room_manager.entry_x
        facing_right = self.room_manager.entry_facing_right
        for flag, spec in (getattr(self.room_manager, "spawn_if", None) or {}).items():
            if spec and self.state.flag(flag):
                x = spec.get("x", x)
                facing = spec.get("facing")
                if facing is not None:
                    facing_right = facing != "left"
                break
        self.player.place_on_floor(
            x,
            self.room_manager.floor_y,
            facing_right=facing_right,
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
        if line.get("key"):
            self.state.set_flag("key_revealed")
            self.state.set_flag("photo_examined")
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
        if self.audio:
            self.audio.stop_all_sfx()
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
        
    def _handle_dialogue_choice(self, choice):
        if choice.get("death"):
            self._pending_death = self._choice_death
        if choice.get("fall"):
            self._pending_fall = self._choice_fall

        choice_index = self.dialogue_box.get_selected_choice()
        self.dialogue_manager.choose(choice_index)

        if self.dialogue_manager.is_active:
            self._apply_line(self.dialogue_manager.current())
        else:
            self.dialogue_box.hide()
            self._finish_interaction()

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
        if self._pending_fall:
            room_id = self._pending_fall
            self._pending_fall = None
            self._start_fall(room_id)
        self._maybe_unlock_room()

    def _maybe_unlock_room(self):
        spec = getattr(self.room_manager, "unlock_if", None)
        if not spec:
            return
        flag = spec.get("flag")
        needed = spec.get("all") or []
        if not flag or self.state.flag(flag):
            return
        if needed and all(self.state.flag(name) for name in needed):
            self.state.set_flag(flag)

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
        if self.player is not None:
            self.player.apply_death_pose(0)

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
            facing_right = self.death.spec.get("respawn_facing", "right") != "left"
            self.player.place_on_floor(
                respawn_x,
                self.room_manager.floor_y,
                facing_right=facing_right,
            )
        self.prompt.visible = False
        self.keys_held.clear()
        self.state.room_id = room_id
        if self.death.spec.get("respawn_x") is not None:
            self.state.from_room_id = "died_lustre"
        self.state.save()

    def _interact(self):
        target = self.room_manager.get_nearby_interactable(self.player, self.state)
        self._interact_with(target)

    def _interact_with(self, target):
        if target is None:
            return
        if target.leads_to:
            if target.requires and not self.state.flag(target.requires):
                if target.keypad:
                    self._open_keypad(target)
                    return
                if target.locked_dialogue:
                    self._object_search = True
                    self._start_dialogue(target.locked_dialogue)
                return
            if target.dialogue_id:
                self._choice_fall = target.leads_to
                self._object_search = True
                self._start_dialogue(target.dialogue_id)
                return
            if target.sfx:
                self.audio.play_sfx(target.sfx, constants.PROJECT_ROOT / target.sfx)
            if target.transition == "fall":
                self._start_fall(target.leads_to)
                return
            self._start_door_fade(target.leads_to)
            return

        if target.bookshelf:
            self._open_bookshelf(target)
            return

        death = target.death
        already_died = death and self.state.flag(death.get("flag"))
        already_seen = (
            bool(target.done_flag and self.state.flag(target.done_flag))
            or bool(target.reveals and self.state.flag(target.reveals) and target.done_dialogue)
        )
        if already_died or already_seen:
            dialogue_id = target.done_dialogue
        else:
            dialogue_id = target.resolve_dialogue(self.state)
        self._pending_reveal = None if already_seen else target.reveals
        self._pending_give = target.gives
        self._pending_death = None
        self._choice_death = None if already_died else death
        self._object_search = True

        if dialogue_id:
            if self._start_inspect(target):
                self._pending_dialogue = dialogue_id
                return
            self._start_dialogue(dialogue_id)
            return
        self._finish_interaction()

    # Vues rapprochées (étagère, cadenas)

    def _overlay_active(self):
        return self.bookshelf.active or self.keypad.active

    def _open_bookshelf(self, target):
        self.keys_held.clear()
        if target.sfx:
            self.audio.play_sfx(target.sfx, constants.PROJECT_ROOT / target.sfx)
        self.bookshelf.open(target.bookshelf)

    def _read_selected_book(self):
        book = self.bookshelf.selected_book()
        if book is None:
            return
        self._pending_reveal = book.get("reveals")
        self._pending_give = None
        self._pending_death = None
        self._start_dialogue(book.get("dialogue"))

    def _open_keypad(self, target):
        self.keys_held.clear()
        self._keypad_target = target
        self.keypad.open(target.keypad)

    def _unlock_keypad_target(self):
        target = self._keypad_target
        self.keypad.close()
        self._keypad_target = None
        if target is None:
            return
        self.state.set_flag(target.requires)
        self._interact_with(target)

    def _overlay_key_press(self, key):
        if self.keypad.active:
            if key == constants.KEY_BACK:
                self.keypad.close()
                self._keypad_target = None
            elif self.keypad.on_key_press(key):
                self._unlock_keypad_target()
            return
        if key == constants.KEY_BACK:
            self.bookshelf.close()
        elif key in (constants.KEY_LEFT, arcade.key.LEFT, arcade.key.UP):
            self.bookshelf.move(-1)
        elif key in (constants.KEY_RIGHT, arcade.key.RIGHT, arcade.key.DOWN):
            self.bookshelf.move(1)
        elif key in (constants.KEY_INTERACT, constants.KEY_CONFIRM, constants.KEY_SKIP):
            self._read_selected_book()

    def _overlay_mouse_press(self, x, y):
        if self.keypad.active:
            if self.keypad.on_mouse_press(x, y):
                self._unlock_keypad_target()
            return
        index = self.bookshelf.book_at(x, y)
        if index is None:
            return
        self.bookshelf.selected = index
        self._read_selected_book()

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
            if str(self.room_manager.current_room_id).startswith("vide_"):
                searching = False
            elif self.inspect.active or self._object_search:
                searching = True
            else:
                if nearby is None:
                    nearby = self.room_manager.get_nearby_interactable(self.player, self.state)
                searching = self._target_is_search(nearby)

        self.player.searching = searching

        if self.player.speed_x == 0:
            self.player.apply_idle_pose()

    def _maybe_auto_exits(self):
        if self.player is None or self._fall or self.death.blocking or self.lustre.blocking:
            return False
        half_w = abs(self.player.width) / 2
        at_left = self.player.center_x <= half_w + 2
        at_right = self.player.center_x >= constants.SCREEN_WIDTH - half_w - 2
        for spec in getattr(self.room_manager, "auto_exits", []) or []:
            dest = spec.get("leads_to")
            if not dest:
                continue
            if spec.get("x_max") is not None and (at_left or self.player.center_x <= spec["x_max"]):
                self._start_door_fade(dest)
                return True
            if spec.get("x_min") is not None and (at_right or self.player.center_x >= spec["x_min"]):
                self._start_door_fade(dest)
                return True
        return False

    def _apply_collisions(self):
        if self.player is None:
            return
        x = self.player.center_x
        for left, right in self._collision_spans():
            if left < x < right:
                if self.player.speed_x < 0 or (self.player.speed_x == 0 and x >= (left + right) / 2):
                    self.player.center_x = right
                else:
                    self.player.center_x = left

    def _collision_spans(self):
        spans = []
        for spec in getattr(self.room_manager, "collisions", []) or []:
            flag = spec.get("if")
            if flag and not self.state.flag(flag):
                continue
            box = spec.get("hitbox") or spec.get("x")
            if not box or len(box) < 2:
                continue
            spans.append((box[0], box[1]))
        for item in self.room_manager.active_interactables(self.state):
            if not getattr(item, "blocks", False):
                continue
            left, right, _bottom, _top = item.hitbox
            spans.append((left, right))
        return spans

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
        self._fall = {"t": 0.0, "room": room_id, "phase": "out", "kind": "fall"}

    def _start_door_fade(self, room_id):
        self.keys_held.clear()
        if self.player is not None:
            self.player.speed_x = 0
        self._ensure_door_fade_texture()
        from_id = self.room_manager.current_room_id
        if str(from_id).startswith("vide_"):
            self._enter_room(room_id, from_room_id=from_id)
            self._fall = {"t": 0.0, "room": room_id, "phase": "in", "kind": "door"}
            return
        self._fall = {"t": 0.0, "room": room_id, "phase": "out", "kind": "door"}

    def _ensure_door_fade_texture(self):
        if self._door_fade_texture is not None:
            return
        path = constants.PROJECT_ROOT / constants.SPRITE_EMPTY_CORRIDOR
        if path.exists():
            self._door_fade_texture = arcade.load_texture(str(path))

    def _update_fall(self, delta_time):
        if not self._fall:
            return False
        self._fall["t"] += delta_time
        kind = self._fall.get("kind", "fall")
        out_t = constants.DOOR_FADE_OUT if kind == "door" else 1.15
        in_t = constants.DOOR_FADE_IN if kind == "door" else 0.9
        if self._fall["phase"] == "out" and self._fall["t"] >= out_t:
            dest = self._fall["room"]
            self._enter_room(dest, from_room_id=self.room_manager.current_room_id)
            if kind == "door" and str(dest).startswith("vide_"):
                self._fall = None
                return False
            self._fall = {"t": 0.0, "room": dest, "phase": "in", "kind": kind}
        elif self._fall["phase"] == "in" and self._fall["t"] >= in_t:
            self._fall = None
            return False
        return True

    def _draw_fall(self):
        if not self._fall:
            return
        kind = self._fall.get("kind", "fall")
        if kind == "door":
            out_t, in_t = constants.DOOR_FADE_OUT, constants.DOOR_FADE_IN
        else:
            out_t, in_t = 0.85, 0.9
        if self._fall["phase"] == "out":
            alpha = min(1.0, self._fall["t"] / max(out_t, 0.001))
        else:
            alpha = max(0.0, 1.0 - self._fall["t"] / max(in_t, 0.001))
        if alpha <= 0.02:
            return
        if kind == "door" and self._door_fade_texture is not None:
            arcade.draw_texture_rect(
                self._door_fade_texture,
                arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
                alpha=int(255 * alpha),
            )
            return
        color = (8, 8, 10) if kind == "door" else (4, 2, 6)
        arcade.draw_lrbt_rectangle_filled(
            0,
            constants.SCREEN_WIDTH,
            0,
            constants.SCREEN_HEIGHT,
            (*color, int(255 * alpha)),
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