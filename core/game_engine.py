from core.music_manager import MusicManager
import sys
import os

from ui.flesh_algorithm_terminal import FleshAlgorithmTerminal
sys.path.append(".")
import pygame
from config import settings # Import settings module directly
from config.constants import STATE_TITLE_SCREEN, STATE_GAMEPLAY, STATE_PAUSE_MENU, STATE_SETTINGS_MENU, STATE_INVENTORY, STATE_SKILL_TREE, STATE_DEVELOPER_INVENTORY
from core.input_handler import InputHandler
from core.scene_manager import SceneManager, BaseScene
from core.utils import draw_text
from ui.hud import HUD # Import HUD
from ui.inventory_screen import InventoryScreen # Import InventoryScreen
from ui.paste_tree_screen import PasteTreeScreen # Import PasteTreeScreen
from ui.dialogue_manager import DialogueManager
from progression.quests import QuestManager # Import QuestManager
from progression.quest_tracker import QuestTracker # Import QuestTracker
from ui.developer_inventory_screen import DeveloperInventoryScreen
import sys
import logging # Import logging module
import traceback # Import traceback module
from core.swamp_cave_dungeon import SwampCaveDungeon # Import SwampCaveDungeon
import json
import inspect # Import inspect module

class GameEngine:
    """Manages the main game loop, scenes, and core systems."""
    def __init__(self):
        # Center the window before initializing pygame
        if not settings.FULLSCREEN:
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            
        pygame.init()
        # Initialize the screen with basic settings first
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.game_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)) # Game is rendered to this surface
        
        # Configure logging
        logging.basicConfig(level=logging.DEBUG if settings.DEBUG_MODE else logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.music_manager = MusicManager()

        self.logger.info("GameEngine initialized.")

        self.settings = settings # Make settings accessible
        pygame.display.set_caption(self.settings.CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True

        # Load custom cursor image
        self.custom_cursor_image = pygame.image.load('graphics/gui/cursor.png').convert_alpha()

        self.input_handler = InputHandler()

        self.player = None # Initialize player to None
        self.hud = None # Initialize hud to None
        self.dialogue_manager = DialogueManager(self)
        self.flesh_algorithm_terminal = FleshAlgorithmTerminal(self)
        self.quest_manager = QuestManager('data/quests.json') # Initialize QuestManager
        self.quest_tracker = QuestTracker() # Initialize QuestTracker

        self.scene_manager = SceneManager(self) # Pass self (GameEngine instance) to SceneManager - MOVED THIS LINE UP

        # Apply display settings properly
        self.apply_display_settings()

        # Load scenes from data/scenes.json
        self.developer_inventory_screen = DeveloperInventoryScreen(self)
        self.scene_manager.add_scene(STATE_DEVELOPER_INVENTORY, self.developer_inventory_screen)
        self.load_scenes()

        self.scene_manager.set_scene(STATE_TITLE_SCREEN)

    def load_scenes(self):
        """Loads scenes from data/scenes.json."""
        with open('data/scenes.json', 'r') as f:
            self.scenes_data = json.load(f) # Store scenes_data as a self attribute

        self.scenes = {}
        for scene_data in self.scenes_data['scenes']: # Use self.scenes_data
            name = scene_data['name']
            class_path = scene_data['class']
            module_name, class_name = class_path.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            scene_class = getattr(module, class_name)

            scene_args = {'game': self}
            dungeon_data = None

            if name == "spawn_town":
                from core.spawn_town import SpawnTown
                scene = scene_class(self)
                self.spawn_town = scene
                self.player = scene.player # Set player from SpawnTown instance
                self.hud = scene.hud # Set HUD from SpawnTown instance
            else:
                # Check if the scene constructor expects player and hud
                if hasattr(scene_class, '__init__'):
                    sig = inspect.signature(scene_class.__init__)
                    if 'player' in sig.parameters and 'hud' in sig.parameters:
                        scene_args['player'] = self.player
                        scene_args['hud'] = self.hud

                    # Load dungeon_data if path is specified
                    if "dungeon_data_path" in scene_data:
                        dungeon_data_path = scene_data["dungeon_data_path"]
                        try:
                            with open(dungeon_data_path, "r") as df:
                                dungeon_data = json.load(df)
                            scene_args['dungeon_data'] = dungeon_data
                        except (FileNotFoundError, json.JSONDecodeError) as e:
                            self.logger.error(f"Error loading dungeon data for scene {name} from {dungeon_data_path}: {e}")
                            scene_args['dungeon_data'] = None # Ensure dungeon_data is None on error
                    
                    # Pass 'is_dark' parameter if it exists in scene_data AND the scene's __init__ accepts it
                    if "darkness" in scene_data and 'is_dark' in sig.parameters: # Re-added 'is_dark' in sig.parameters check
                        scene_args['is_dark'] = scene_data["darkness"]
                        self.logger.info(f"GameEngine: Passing is_dark: {scene_args['is_dark']} to scene {name} during initial load.")

                scene = scene_class(**scene_args)

            self.logger.info(f"Attempting to add scene: {name} with class {class_name}")
            self.scene_manager.add_scene(name, scene)

    def apply_display_settings(self):
        """Applies display settings from config.settings."""
        self.logger.info("Applying display settings.")
        self.logger.info(f"Fullscreen: {self.settings.FULLSCREEN}, Borderless: {self.settings.BORDERLESS}, Vsync: {self.settings.VSYNC}")

        # Center the window before reinitializing the display
        if not self.settings.FULLSCREEN:
            os.environ['SDL_VIDEO_CENTERED'] = '1'

        # Calculate flags based on settings
        flags = 0
        if self.settings.FULLSCREEN:
            flags |= pygame.FULLSCREEN
        if self.settings.VSYNC:
            flags |= pygame.DOUBLEBUF

        # Reinitialize the display with the correct settings
        try:
            self.screen = pygame.display.set_mode(
                (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT),
                flags,
                vsync=self.settings.VSYNC
            )
            # Also update the game surface to match the new resolution
            self.game_surface = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        except pygame.error as e:
            self.logger.error(f"Failed to set display mode: {e}")
            # Fallback to basic windowed mode if there's an error
            self.screen = pygame.display.set_mode(
                (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
            )
            self.game_surface = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        
        # Ensure fonts are initialized after display changes
        if not pygame.font.get_init():
            pygame.font.init()
            from utility.font_cache import clear_font_cache
            clear_font_cache()
            self.logger.info("Pygame font module re-initialized.")
        
        # Reinitialize fonts for UI elements across all scenes
        self.reinitialize_ui_fonts() # Call the new method here

        pygame.display.set_caption(self.settings.CAPTION)

    def reinitialize_ui_fonts(self):
        """Reinitializes fonts for UI elements in all loaded scenes."""
        self.logger.info("Reinitializing UI fonts for all scenes.")
        for scene_name, scene_obj in self.scene_manager.scenes.items():
            if hasattr(scene_obj, 'reinitialize_fonts'):
                self.logger.info(f"Reinitializing fonts for scene: {scene_name}")
                scene_obj.reinitialize_fonts()

    def run(self):
        """Runs the main game loop."""
        try:
            while self.running:
                dt = self.clock.tick(self.settings.FPS) / 1000.0 # Delta time in seconds

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.input_handler.handle_event(event)
                    self.scene_manager.handle_event(event)

                # Check if display is still valid before operations
                if not pygame.display.get_active():
                    self.logger.warning("Display surface is not active, reinitializing...")
                    self.apply_display_settings()

                self.scene_manager.update(dt)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'effects'):
                    self.scene_manager.current_scene.effects.update(dt)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'projectiles'):
                    self.scene_manager.current_scene.projectiles.update(dt, self.scene_manager.current_scene.player, self.scene_manager.current_scene.tile_map, self.scene_manager.current_scene.tile_size)

                # --- Rendering starts here ---
                
                # 1. Clear the game surface
                self.game_surface.fill((0, 0, 0))

                # 2. Draw all game elements to the game_surface
                self.scene_manager.draw(self.game_surface)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'effects'):
                    for sprite in self.scene_manager.current_scene.effects:
                        self.game_surface.blit(sprite.image, (sprite.rect.x - self.scene_manager.current_scene.camera_x, sprite.rect.y - self.scene_manager.current_scene.camera_y))
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'projectiles'):
                    for sprite in self.scene_manager.current_scene.projectiles:
                        sprite.draw(self.game_surface, self.scene_manager.current_scene.camera_x, self.scene_manager.current_scene.camera_y, self.scene_manager.current_scene.zoom_level)

                # Draw the custom cursor, centered on the mouse position
                mouse_pos = pygame.mouse.get_pos()
                cursor_x = mouse_pos[0] - self.custom_cursor_image.get_width() // 2
                cursor_y = mouse_pos[1] - self.custom_cursor_image.get_height() // 2
                self.game_surface.blit(self.custom_cursor_image, (cursor_x, cursor_y))
                
                

                self.input_handler.reset_inputs() # Reset input states for the next frame

                if self.settings.DEBUG_MODE:
                    debug_y_offset = 10
                    if self.settings.SHOW_FPS:
                        fps_text = f"FPS: {int(self.clock.get_fps())}"
                        draw_text(self.game_surface, fps_text, 18, (255, 255, 0), 10, debug_y_offset)
                        debug_y_offset += 20
                    if self.settings.SHOW_SCENE_NAME:
                        scene_name_text = f"Scene: {self.scene_manager.current_scene_name}"
                        draw_text(self.game_surface, scene_name_text, 18, (255, 255, 0), 10, debug_y_offset)
                        debug_y_offset += 20
                    if self.settings.SHOW_DELTA_TIME:
                        dt_text = f"DT: {dt:.4f}s"
                        draw_text(self.game_surface, dt_text, 18, (255, 255, 0), 10, debug_y_offset)
                        debug_y_offset += 20
                    if self.settings.SHOW_PLAYER_TILE_COORDS:
                        if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'player'):
                            player = self.scene_manager.current_scene.player
                            tile_x = int(player.rect.x / 32)
                            tile_y = int(player.rect.y / 32)
                            player_coords_text = f"Player Tile: ({tile_x}, {tile_y})"
                            draw_text(self.game_surface, player_coords_text, 18, (255, 255, 0), 10, debug_y_offset)
                            debug_y_offset += 20
                
                # 3. Clear the main screen and draw the scaled game_surface onto it
                try:
                    self.screen.fill((0, 0, 0)) # Black bars
                    # Calculate position to center the game_surface
                    screen_w, screen_h = self.screen.get_size()
                    surface_w, surface_h = self.game_surface.get_size()
                    top_left_x = (screen_w - surface_w) // 2
                    top_left_y = (screen_h - surface_h) // 2
                    
                    self.screen.blit(self.game_surface, (top_left_x, top_left_y))
                    pygame.display.flip()
                except pygame.error as e:
                    self.logger.error(f"Failed to fill or flip display: {e}")
                    self.apply_display_settings() # Try to reinitialize display
                    continue # Skip this frame if display is not ready

            self.quit_game()
        except Exception as e:
            self.logger.exception("An unhandled exception occurred during the game loop:")
            traceback.print_exc() # Print the full traceback
            self.quit_game()

    def quit_game(self):
        """Sets the running flag to False to exit the game loop."""
        self.running = False
        pygame.quit()
        # sys.exit() # Temporarily commented out for debugging