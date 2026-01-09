import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import pygame
from core.game_engine import GameEngine
from utility.resource_path import resource_path
from core.scene_manager import SceneManager
from entities.player import Player
from ui.title_screen import TitleScreen, InfoScreen
from ui.menus import Button
from core.IntroScene import IntroScene  # Import the IntroScene
from ui.loading_screen import LoadingScreen

if __name__ == "__main__":
    try:
        # Set SDL_VIDEO_CENTERED before pygame.init() for proper window centering
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        print("Initializing pygame...")
        pygame.init()
        pygame.mixer.init()
        screen = pygame.display.set_mode((800, 600))  # Temporary screen for loading
        pygame.mouse.set_visible(False)  # Hide the system cursor

        if "-dev" not in sys.argv:
            print("Loading screen...")
            loading_screen = LoadingScreen(screen)
            loading_screen.run()

        print("Loading music...")
        pygame.mixer.music.load(resource_path("data/corrupted.wav"))
        pygame.mixer.music.play(-1) # -1 means loop indefinitely

        print("Creating game engine...")
        game = GameEngine()
        scene_manager = game.scene_manager

        print("Initializing scenes...")
        # Initialize TitleScreen and set it as the initial scene
        title_screen = TitleScreen(game)
        info_screen = InfoScreen(game)
        intro_scene = IntroScene(game)  # Initialize the IntroScene
        game.info_screen = info_screen
        scene_manager.add_scene("intro_scene", intro_scene)  # Add the IntroScene to the SceneManager
        from config.constants import STATE_TITLE_SCREEN

        print("Starting game loop...")
        game.run()
        pygame.quit()
        print("Game exited normally.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "="*50)
        input("Press Enter to exit...")
        try:
            pygame.quit()
        except:
            pass
        sys.exit(1)