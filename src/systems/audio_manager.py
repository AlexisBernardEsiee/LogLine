from __future__ import annotations

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

    def play_music(self, path: str | Path, volume: float = 0.5, loop: bool = True) -> None:
        """Joue une musique de fond en boucle."""
        self.stop_music()

        sound_path = Path(path)
        if not sound_path.exists():
            print(f"[AudioManager] Fichier audio introuvable : {sound_path}")
            return

        try:
            sound = arcade.Sound(sound_path)
            self.music_volume = volume
            self.music_player = sound.play(volume=self.music_volume, loop=loop)
            self.current_music_sound = sound
        except Exception as e:
            print(f"[AudioManager] Erreur lors de la lecture de {sound_path} : {e}")

    def stop_music(self) -> None:
        """Arrête la musique d'ambiance en cours."""
        if self.music_player:
            try:
                self.music_player.stop()
            except Exception:
                pass
            self.music_player = None
            self.current_music_sound = None

    def set_music_volume(self, volume: float) -> None:
        """Ajuste le volume de la musique en cours (0.0 à 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_player:
            self.music_player.volume = self.music_volume

    def play_sfx(self, name: str, sound_path: str | Path | None = None, volume_modifier: float = 1.0) -> None:
        """Joue un effet sonore (SFX) court."""
        if name not in self.sounds_cache and sound_path:
            path = Path(sound_path)
            if path.exists():
                self.sounds_cache[name] = arcade.Sound(path)

        if name in self.sounds_cache:
            try:
                vol = max(0.0, min(1.0, self.sfx_volume * volume_modifier))
                self.sounds_cache[name].play(volume=vol)
            except Exception as e:
                print(f"[AudioManager] Erreur lors de la lecture du SFX '{name}' : {e}")
    
    def play_typewriter_sound(self) -> None:
        """Joue un son léger de touche de clavier pour le défilement du texte."""
        sound_path = Path("assets/sounds/clic.mp3")
        self.play_sfx("typing", sound_path, volume_modifier=0.3)