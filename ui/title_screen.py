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
        self.animation_frame += 0.001
        if self.animation_frame > 120:
            self.animation_frame = 0

        self.x_offset += 0.01
        if self.x_offset > settings.SCREEN_WIDTH:
            self.x_offset = 0

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)

        # Load background images
        self.background_images = [
            pygame.image.load("graphics/dc-misc/num0.png").convert_alpha(),
            pygame.image.load("graphics/dc-misc/demon_num1.png").convert_alpha(),
            pygame.image.load("graphics/dc-misc/num1.png").convert_alpha(),


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
                    image = pygame.transform.scale(image, (image.get_width() * 5, image.get_height() * 5))
                    x = int(x_start - self.x_offset)
                    y = j * image.get_height() - settings.SCREEN_HEIGHT // 2
                    screen.blit(image, (x, y))
                    x_start += image.get_width()

        # Load the title image
        title_image = pygame.image.load("graphics/title.png").convert_alpha()
        # Scale the title image to fit the screen width while maintaining aspect ratio
        aspect_ratio = title_image.get_width() / title_image.get_height()
        title_scale_factor = 0.75  # Make the title image 75% smaller
        new_width = int(title_image.get_width() * title_scale_factor)
        new_height = int(title_image.get_height() * title_scale_factor)
        title_image = pygame.transform.scale(title_image, (new_width, new_height))
        title_rect = title_image.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4))
        screen.blit(title_image, title_rect)

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

    def recreate_ui(self):
        self.back_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT - 100, 200, 50,
            "Back", lambda: self.game.scene_manager.set_scene("title_screen")
        )

    def enter(self):
        self.game.logger.info("Entering Info Screen.")
        self.recreate_ui()

    def exit(self):
        self.game.logger.info("Exiting Info Screen.")

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        y_offset = settings.SCREEN_HEIGHT // 4
        for line in self.info_text:
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30
        self.back_button.draw(screen)
