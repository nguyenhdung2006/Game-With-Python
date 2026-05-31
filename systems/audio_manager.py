"""Safe optional audio playback for future local SFX and music assets."""

from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_ROOT = PROJECT_ROOT / "assets" / "audio"
AUDIO_EXTENSIONS = (".ogg", ".wav", ".mp3")


class AudioManager:
    """Load optional audio lazily and no-op safely when playback is unavailable."""

    def __init__(self, preferences=None, audio_root=None):
        self.preferences = preferences if preferences is not None else {}
        self.audio_root = Path(audio_root) if audio_root is not None else DEFAULT_AUDIO_ROOT
        self.sfx_root = self.audio_root / "sfx"
        self.music_root = self.audio_root / "music"
        self.sound_cache = {}
        self.current_music_name = None
        self.enabled = self.initialize_mixer()

    def initialize_mixer(self):
        """Initialize Pygame mixer without making audio hardware mandatory."""
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            return pygame.mixer.get_init() is not None
        except pygame.error:
            return False

    def play_sfx(self, name):
        """Play one optional SFX asset once, or return False when unavailable."""
        if not self.enabled:
            return False

        asset_path = self.find_asset(self.sfx_root, name)
        if asset_path is None:
            return False

        try:
            sound = self.sound_cache.get(asset_path)
            if sound is None:
                sound = pygame.mixer.Sound(str(asset_path))
                self.sound_cache[asset_path] = sound
            sound.set_volume(self.sfx_volume())
            sound.play()
            return True
        except (OSError, pygame.error):
            return False

    def play_music(self, name, loops=-1):
        """Start one optional music track, or return False when unavailable."""
        if not self.enabled:
            return False

        asset_path = self.find_asset(self.music_root, name)
        if asset_path is None:
            return False

        try:
            pygame.mixer.music.load(str(asset_path))
            pygame.mixer.music.set_volume(self.music_volume())
            pygame.mixer.music.play(loops)
            self.current_music_name = name
            return True
        except (OSError, pygame.error):
            return False

    def refresh_volumes(self):
        """Apply updated settings to cached sounds and the active music channel."""
        for sound in self.sound_cache.values():
            try:
                sound.set_volume(self.sfx_volume())
            except pygame.error:
                pass
        if not self.enabled:
            return
        try:
            pygame.mixer.music.set_volume(self.music_volume())
        except pygame.error:
            pass

    def stop_music(self):
        """Stop the shared music channel safely."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        self.current_music_name = None

    def sfx_volume(self):
        """Return effective SFX volume after applying master volume."""
        return clamp_volume(self.preferences.get("master_volume", 1.0)) * clamp_volume(
            self.preferences.get("sfx_volume", 1.0)
        )

    def music_volume(self):
        """Return effective music volume after applying master volume."""
        return clamp_volume(self.preferences.get("master_volume", 1.0)) * clamp_volume(
            self.preferences.get("music_volume", 1.0)
        )

    def find_asset(self, folder, name):
        """Resolve a simple asset name without requiring any file to exist."""
        if not isinstance(name, str) or not name:
            return None
        for extension in AUDIO_EXTENSIONS:
            asset_path = folder / f"{name}{extension}"
            if asset_path.is_file():
                return asset_path
        return None


def clamp_volume(value):
    """Clamp runtime volume reads even if preferences were edited externally."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return 1.0
    return max(0.0, min(1.0, float(value)))


def play_audio_event(owner, name):
    """Play a one-shot hook through an entity's optional audio manager."""
    audio_manager = getattr(owner, "audio_manager", None)
    if audio_manager is not None:
        audio_manager.play_sfx(name)
