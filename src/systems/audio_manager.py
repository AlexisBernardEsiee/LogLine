from __future__ import annotations

import time
from pathlib import Path

import arcade

from src import constants


class AudioManager:
    """Gestionnaire central de l'audio (musiques et bruitages)."""

    def __init__(self) -> None:
        self.music_player = None
        self.current_music_sound: arcade.Sound | None = None
        self.music_volume: float = 0.5
        self.sfx_volume: float = 0.7
        self.sounds_cache: dict[str, arcade.Sound] = {}
        self._music_path: Path | None = None
        self._music_loop = False
        self._music_was_playing = False
        self._sfx_players: dict[str, object] = {}
        self._last_typewriter_time = 0.0

    def play_music(self, path: str | Path, volume: float = 0.5, loop: bool = True) -> None:
        """Joue une musique de fond. En streaming pour ne pas bloquer au chargement."""
        self.stop_music()
        self._music_path = Path(path)
        self._music_loop = loop
        self.music_volume = volume
        self._start_stream()

    def _start_stream(self) -> None:
        if self._music_path is None or not self._music_path.exists():
            if self._music_path is not None:
                print(f"[AudioManager] Fichier audio introuvable : {self._music_path}")
            return
        try:
            sound = arcade.Sound(self._music_path, streaming=True)
            self.current_music_sound = sound
            self.music_player = sound.play(volume=self.music_volume, loop=False)
            self._music_was_playing = False
        except Exception as e:
            print(f"[AudioManager] Erreur lors de la lecture de {self._music_path} : {e}")

    def stop_music(self) -> None:
        """Arrête la musique d'ambiance en cours."""
        self._music_loop = False
        self._music_was_playing = False
        if self.music_player:
            try:
                self.music_player.pause()
            except Exception as e:
                print(f"[AudioManager] Erreur lors de l'arrêt de la musique : {e}")
            self.music_player = None
            self.current_music_sound = None

    def update(self) -> None:
        if not self._music_loop or self.music_player is None:
            return
        playing = bool(getattr(self.music_player, "playing", False))
        if playing:
            self._music_was_playing = True
            return
        if self._music_was_playing:
            self._start_stream()

    def set_music_volume(self, volume: float) -> None:
        """Ajuste le volume de la musique en cours (0.0 à 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_player:
            self.music_player.volume = self.music_volume

    def play_sfx(self, name: str, sound_path: str | Path | None = None, volume_modifier: float = 1.0) -> None:
        """Joue un effet sonore (SFX) court."""
        if self._is_glitch(name, sound_path):
            volume_modifier = min(float(volume_modifier), constants.DIALOGUE_GLITCH_VOLUME_CAP)
            self.stop_sfx(name)

        if name not in self.sounds_cache and sound_path:
            path = Path(sound_path)
            if path.exists():
                self.sounds_cache[name] = arcade.Sound(path)

        if name in self.sounds_cache:
            try:
                vol = max(0.0, min(1.0, self.sfx_volume * volume_modifier))
                self._sfx_players[name] = self.sounds_cache[name].play(volume=vol)
            except Exception as e:
                print(f"[AudioManager] Erreur lors de la lecture du SFX '{name}' : {e}")

    def stop_sfx(self, name: str) -> None:
        player = self._sfx_players.pop(name, None)
        if player is None:
            return
        try:
            player.pause()
        except Exception:
            pass
    
    def stop_all_sfx(self) -> None:
        """Arrête tous les effets sonores (SFX) en cours de lecture."""
        for name in list(self._sfx_players.keys()):
            self.stop_sfx(name)

    def stop_glitch(self) -> None:
        for name in list(self._sfx_players):
            if self._is_glitch(name, None):
                self.stop_sfx(name)

    def play_typewriter_sound(self) -> None:
        """Joue un son léger de touche de clavier pour le défilement du texte."""
        if self._glitch_playing():
            return
        now = time.monotonic()
        if now - self._last_typewriter_time < constants.DIALOGUE_TYPEWRITER_INTERVAL:
            return
        player = self._sfx_players.get("typing")
        if player is not None and getattr(player, "playing", False):
            return
        self._last_typewriter_time = now
        sound_path = constants.PROJECT_ROOT / "assets" / "sounds" / "clic.mp3"
        self.play_sfx("typing", sound_path, volume_modifier=constants.DIALOGUE_TYPEWRITER_VOLUME)

    def _glitch_playing(self) -> bool:
        for name, player in self._sfx_players.items():
            if self._is_glitch(name, None) and player is not None and getattr(player, "playing", False):
                return True
        return False

    @staticmethod
    def _is_glitch(name: str, sound_path: str | Path | None) -> bool:
        blob = f"{name} {sound_path or ''}".lower()
        return "tremblement" in blob or "erreur" in blob
