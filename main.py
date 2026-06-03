import os
import pygame

from managers.game_state import DUNGEON_MODE, GUIDE_MODE, MODE_SELECT, PREVIEW_MODE, SETTINGS_MODE, SOLO_MODE, TEAM_MODE_LOCKED, GameState
from modes.dungeon_mode import DungeonMode
from modes.solo_mode import SoloMode
from settings import FPS, HEIGHT, WIDTH
from systems.audio_manager import AudioManager
from systems.display_manager import DisplayManager
from systems.input_manager import InputManager
from systems.settings_store import SettingsStore
from ui.mode_select import draw_mode_select, draw_team_locked
from ui.game_guide import draw_game_guide
from ui.game_preview import draw_game_preview
from ui.settings_menu import SettingsMenu


def main():
    pygame.init()

    settings_store = SettingsStore()
    display_manager = DisplayManager()
    screen = display_manager.apply_fullscreen(settings_store.get("fullscreen_enabled"))
    pygame.display.set_caption("Anime Combat Project")
    clock = pygame.time.Clock()
    scene_surface = pygame.Surface((WIDTH, HEIGHT))

    game_state = GameState()
    audio_manager = AudioManager(settings_store.settings)
    input_manager = InputManager(settings_store.settings)
    settings_menu = SettingsMenu(
        settings_store,
        audio_manager,
        input_manager,
        display_manager.handle_setting_changed,
    )
    audio_manager.play_music("menu")
    dungeon_mode = None
    solo_mode = None

    running = True
    while running:
        # Delta time is the number of seconds since the last frame.
        target_fps = settings_store.get("target_fps")
        dt = min(clock.tick(target_fps or FPS) / 1000, 1 / 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state.is_mode_select():
                    if input_manager.event_matches("back", event):
                        running = False
                    elif input_manager.event_matches("select_solo", event):
                        audio_manager.play_sfx("menu_select")
                        audio_manager.play_music("solo")
                        solo_mode = SoloMode(settings_store.settings, audio_manager, input_manager)
                        game_state.enter_solo_mode()
                    elif input_manager.event_matches("select_dungeon", event):
                        audio_manager.play_sfx("menu_select")
                        audio_manager.play_music("dungeon")
                        dungeon_mode = DungeonMode(settings_store.settings, audio_manager, input_manager)
                        game_state.enter_dungeon_mode()
                    elif input_manager.event_matches("select_team", event):
                        audio_manager.play_sfx("menu_select")
                        game_state.enter_team_mode_locked()
                    elif input_manager.event_matches("select_settings", event):
                        audio_manager.play_sfx("menu_select")
                        game_state.enter_settings()
                    elif input_manager.event_matches("select_guide", event):
                        audio_manager.play_sfx("menu_select")
                        game_state.enter_guide()
                    elif input_manager.event_matches("select_preview", event):
                        audio_manager.play_sfx("menu_select")
                        game_state.enter_preview()
                elif game_state.current == SOLO_MODE:
                    if input_manager.event_matches("back", event):
                        solo_mode = None
                        audio_manager.play_music("menu")
                        game_state.enter_mode_select()
                    elif solo_mode is not None:
                        solo_mode.handle_event(event)
                elif game_state.is_dungeon_mode():
                    if input_manager.event_matches("back", event):
                        dungeon_mode = None
                        audio_manager.play_music("menu")
                        game_state.enter_mode_select()
                    elif dungeon_mode is not None:
                        dungeon_mode.handle_event(event)
                elif game_state.is_settings():
                    if input_manager.event_matches("back", event):
                        audio_manager.play_music("menu")
                        game_state.enter_mode_select()
                    else:
                        settings_menu.handle_event(event)
                elif game_state.is_guide() and input_manager.event_matches("back", event):
                    audio_manager.play_music("menu")
                    game_state.enter_mode_select()
                elif game_state.is_preview() and input_manager.event_matches("back", event):
                    audio_manager.play_music("menu")
                    game_state.enter_mode_select()
                elif game_state.is_placeholder_screen() and input_manager.event_matches("back", event):
                    audio_manager.play_music("menu")
                    game_state.enter_mode_select()
            elif game_state.current == SOLO_MODE and solo_mode is not None:
                solo_mode.handle_event(event)

        keys = pygame.key.get_pressed()
        screen = display_manager.surface
        if game_state.current == DUNGEON_MODE and dungeon_mode is not None:
            dungeon_mode.update(keys, dt)
            dungeon_mode.draw(screen, scene_surface)
        elif game_state.current == SOLO_MODE and solo_mode is not None:
            solo_mode.update(keys, dt)
            solo_mode.draw(screen, scene_surface)
        elif game_state.current == TEAM_MODE_LOCKED:
            draw_team_locked(screen)
        elif game_state.current == SETTINGS_MODE:
            settings_menu.draw(screen)
        elif game_state.current == GUIDE_MODE:
            draw_game_guide(screen, input_manager)
        elif game_state.current == PREVIEW_MODE:
            draw_game_preview(screen, input_manager)
        elif game_state.current == MODE_SELECT:
            draw_mode_select(screen, input_manager)

        pygame.display.flip()

        # This lets automated checks run one frame without opening a long-lived window.
        if os.environ.get("PYGAME_AUTO_QUIT") == "1" or os.environ.get("PYGAME_PHASE1_TEST") == "1":
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
