import pygame
import sys
from core.scene_manager import BaseScene
from config import settings
from core.spawn_town import SpawnTown
from core.utils import draw_text
import random
import math
from ui.button import Button

class TitleScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("Courier New", settings.UI_FONT_SIZE_LARGE * 2)
        self.animation_frame = 0
        self.image_index = 0
        self.alpha = 0
        self.alpha_direction = 1
        self.x_offset = 0
        self.is_muted = False
        self.last_volume = 0.5 # Store the last volume before muting
        self.recreate_ui()

        # New attributes for background animation timing
        self.last_background_draw_time = 0
        self.background_draw_interval = 1000 / 60 # 1 FPS for background animation (1000ms / 1 frame)
        self.background_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.needs_background_redraw = True # Flag to force initial redraw

    def recreate_ui(self):
        self.start_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT // 2 + 50, 200, 50,
            "Start Game", lambda: self.game.scene_manager.set_scene("character_selection")
        )
        self.info_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT // 2 + 110, 200, 50,
            "Info", lambda: self.game.scene_manager.set_scene("info_screen")
        )
        self.load_character_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT // 2 + 170, 200, 50,
            "Load Game", lambda: self.game.scene_manager.set_scene("save_menu")
        )
        self.settings_button = Button(
            settings.SCREEN_WIDTH // 2 + 110, settings.SCREEN_HEIGHT // 2 + 175, 40, 40,
            pygame.transform.scale(pygame.image.load("graphics/dc-misc/options.png").convert_alpha(), (32, 32)), lambda: self.game.scene_manager.set_scene("settings_menu")
        )
        self.dungeon_maker_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT // 2 + 230, 200, 50,
            "Dungeon Maker", self.open_dungeon_generator
        )
        self.exit_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT // 2 + 290, 200, 50,
            "Exit Game", lambda: (pygame.quit(), sys.exit())
        )
        # New mute button
        self.mute_button = Button(
            settings.SCREEN_WIDTH // 2 - 150, settings.SCREEN_HEIGHT // 2 + 175, 40, 40,
            pygame.transform.scale(pygame.image.load("graphics/dc-misc/mute.png").convert_alpha(), (32, 32)), self.toggle_mute
        )
        self.needs_background_redraw = True # Force redraw when UI is recreated

    def open_dungeon_generator(self):
        try:
            import importlib
            from ui import dungeon_generator_gui
            from ui.dungeon_generator_gui import DungeonGeneratorGUI
            original_fullscreen = self.game.settings.FULLSCREEN
            self.game.settings.FULLSCREEN = False
            self.game.apply_display_settings()
            dungeon_generator = DungeonGeneratorGUI(self.game)
            
            dungeon_generator.run()
            self.game.settings.FULLSCREEN = original_fullscreen
            self.game.apply_display_settings()
            self.game.logger.info("Dungeon Generator opened.")
        except ImportError as e:
            self.game.logger.error(f"Failed to open dungeon generator: {e}")
        except Exception as e:
            self.game.logger.error(f"Error in dungeon generator: {e}")

    def enter(self):
        self.game.logger.info("Entering Title Screen.")
        self.recreate_ui()
        self.last_background_draw_time = pygame.time.get_ticks() # Reset timer on entering scene
        self.needs_background_redraw = True # Ensure it draws immediately on entry

    def exit(self):
        self.game.logger.info("Exiting Title Screen.")

    def toggle_mute(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(self.last_volume)
            self.is_muted = False
        else:
            self.last_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0)
            self.is_muted = True
        self.game.logger.info(f"Music muted: {self.is_muted}")
        
    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.info_button.handle_event(event)
        self.load_character_button.handle_event(event)
        self.dungeon_maker_button.handle_event(event)
        self.exit_button.handle_event(event)
        self.settings_button.handle_event(event)
        self.mute_button.handle_event(event) # Handle mute button event

    def update(self, dt):
        # These animations are independent of the background draw rate
        self.animation_frame += 0.001
        if self.animation_frame > 120:
            self.animation_frame = 0

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR) # Always clear the main screen

        current_time = pygame.time.get_ticks()
        if self.needs_background_redraw or (current_time - self.last_background_draw_time >= self.background_draw_interval):
            self.background_surface.fill(settings.UI_BACKGROUND_COLOR) # Clear background surface

            # Load background images (only once per timed redraw)
            self.background_images = [

                pygame.image.load("graphics/titlebg.png").convert_alpha()
            ]

            # Draw the background images with a parallax effect
            num_vertical_repeats = 50
            for j in range(num_vertical_repeats):
                # Create a unique list of images for each layer
                layer_images = random.sample(self.background_images, len(self.background_images))
                x_start = 0
                while x_start < settings.SCREEN_WIDTH:
                    for i, image in enumerate(layer_images):
                        # Scale the image
                        image = pygame.transform.scale(image, (image.get_width() * 1, image.get_height() * 1))
                        x = int(x_start - self.x_offset)
                        y = j * image.get_height() - settings.SCREEN_HEIGHT // 2
                        self.background_surface.blit(image, (x, y))
                        x_start += image.get_width()
            
            # Update x_offset only when background is redrawn
            self.x_offset += 0.001 # Increased step for more noticeable movement at lower FPS
            if self.x_offset > settings.SCREEN_WIDTH:
                self.x_offset = 0

            self.last_background_draw_time = current_time
            self.needs_background_redraw = False

        # Blit the pre-rendered background_surface onto the main screen every frame
        screen.blit(self.background_surface, (0, 0))

        # Load the title image (always drawn every frame)
        title_image = pygame.image.load("graphics/title.png").convert_alpha()
        # Scale the title image to fit the screen width while maintaining aspect ratio
        aspect_ratio = title_image.get_width() / title_image.get_height()
        title_scale_factor = 0.6  # Make the title image 75% smaller
        new_width = int(title_image.get_width() * title_scale_factor)
        new_height = int(title_image.get_height() * title_scale_factor)
        title_image = pygame.transform.scale(title_image, (new_width, new_height))
        title_rect = title_image.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4))
        screen.blit(title_image, title_rect)

        # Draw buttons (always drawn every frame)
        self.start_button.draw(screen)
        self.info_button.draw(screen)
        self.load_character_button.draw(screen)
        self.dungeon_maker_button.draw(screen)
        self.exit_button.draw(screen)
        self.settings_button.draw(screen)
        self.mute_button.draw(screen) # Draw mute button


class InfoScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.text_color = settings.UI_PRIMARY_COLOR
        self.font = pygame.font.SysFont(settings.UI_FONT, settings.UI_FONT_SIZE_DEFAULT)
        self.info_text = [
            "Path of Python",
            "A post-apocalyptic ARPG",
            "Developed by a mysterious person",
            "",
            "Unravel the story of humanity's fall",
            "and the AI's rise.",
            "",
            "Inspired by Path of Exile.",
        ]
        self.recreate_ui()
        self.last_draw_time = 0 # Initialize timer for drawing
        self.draw_interval = 1000 / 5 # 5 FPS in milliseconds

        # Create a surface to draw static elements onto, which will be updated at 5 FPS
        self.static_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.static_surface.fill((0, 0, 0, 0)) # Fill with transparent color initially
        self.needs_redraw = True # Flag to indicate if static_surface needs to be redrawn

    def recreate_ui(self):
        self.back_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT - 100, 200, 50,
            "Back", lambda: self.game.scene_manager.set_scene("title_screen")
        )
        # When UI is recreated, it needs a redraw
        self.needs_redraw = True

    def enter(self):
        self.game.logger.info("Entering Info Screen.")
        self.recreate_ui()
        self.last_draw_time = pygame.time.get_ticks() # Reset timer on entering scene
        self.needs_redraw = True # Ensure it draws immediately on entry

    def exit(self):
        self.game.logger.info("Exiting Info Screen.")

    def handle_event(self, event):
        self.back_button.handle_event(event)
        # If the button is interacted with, we might want to redraw immediately
        if event.type == pygame.MOUSEBUTTONDOWN and self.back_button.rect.collidepoint(event.pos):
            self.needs_redraw = True

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR) # Always clear the main screen
        
        current_time = pygame.time.get_ticks()
        if self.needs_redraw or (current_time - self.last_draw_time >= self.draw_interval):
            # Clear the static surface before redrawing elements on it
            self.static_surface.fill((0, 0, 0, 0)) # Transparent fill

            y_offset = settings.SCREEN_HEIGHT // 4
            for line in self.info_text:
                text_surface = self.font.render(line, True, self.text_color)
                text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, y_offset))
                self.static_surface.blit(text_surface, text_rect)
                y_offset += 30
            self.back_button.draw(self.static_surface) # Draw button to static surface

            self.last_draw_time = current_time
            self.needs_redraw = False # Reset flag after redraw

        # Blit the pre-rendered static_surface onto the main screen every frame
        screen.blit(self.static_surface, (0, 0))
