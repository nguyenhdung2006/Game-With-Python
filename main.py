import os
import pygame

from managers.game_state import DUNGEON_MODE, MODE_SELECT, SETTINGS_MODE, SOLO_MODE, TEAM_MODE_LOCKED, GameState
from modes.dungeon_mode import DungeonMode
from modes.solo_mode import SoloMode
from settings import FPS, HEIGHT, WIDTH
from systems.settings_store import SettingsStore
from ui.mode_select import draw_mode_select, draw_team_locked
from ui.settings_menu import SettingsMenu


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Anime Stickman Combat - Phase 41")
    clock = pygame.time.Clock()
    scene_surface = pygame.Surface((WIDTH, HEIGHT))

    game_state = GameState()
    settings_store = SettingsStore()
    settings_menu = SettingsMenu(settings_store)
    dungeon_mode = None
    solo_mode = None

    running = True
    while running:
        # Delta time is the number of seconds since the last frame.
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state.is_mode_select():
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_1:
                        solo_mode = SoloMode(settings_store.settings)
                        game_state.enter_solo_mode()
                    elif event.key == pygame.K_2:
                        dungeon_mode = DungeonMode(settings_store.settings)
                        game_state.enter_dungeon_mode()
                    elif event.key == pygame.K_3:
                        game_state.enter_team_mode_locked()
                    elif event.key == pygame.K_4:
                        game_state.enter_settings()
                elif game_state.current == SOLO_MODE:
                    if event.key == pygame.K_ESCAPE:
                        solo_mode = None
                        game_state.enter_mode_select()
                    elif solo_mode is not None:
                        solo_mode.handle_event(event)
                elif game_state.is_dungeon_mode():
                    if event.key == pygame.K_ESCAPE:
                        dungeon_mode = None
                        game_state.enter_mode_select()
                    elif dungeon_mode is not None:
                        dungeon_mode.handle_event(event)
                elif game_state.is_settings():
                    if event.key == pygame.K_ESCAPE:
                        game_state.enter_mode_select()
                    else:
                        settings_menu.handle_event(event)
                elif game_state.is_placeholder_screen() and event.key == pygame.K_ESCAPE:
                    game_state.enter_mode_select()
            elif game_state.current == SOLO_MODE and solo_mode is not None:
                solo_mode.handle_event(event)

        keys = pygame.key.get_pressed()
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
        elif game_state.current == MODE_SELECT:
            draw_mode_select(screen)

        pygame.display.flip()

        # This lets automated checks run one frame without opening a long-lived window.
        if os.environ.get("PYGAME_AUTO_QUIT") == "1" or os.environ.get("PYGAME_PHASE1_TEST") == "1":
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
