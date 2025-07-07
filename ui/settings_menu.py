import pygame
from core.scene_manager import BaseScene
from core.music_manager import MusicManager
from config import settings
from core.utils import draw_text
from ui.button import Button
from ui.dropdown import Dropdown

class SettingsMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.dropdowns = []
        self.volume = self.game.music_manager.get_volume()
        self.dragging_volume_slider = False
        self.recreate_ui()

    def recreate_ui(self):
        """Clears and recreates all UI elements with current screen dimensions."""
        self.buttons.clear()
        self.dropdowns.clear()

        button_width = 250
        button_height = 50
        spacing = 60

        # Calculate total height of UI elements block for dynamic vertical centering
        # The total height is from the top of the first element to the bottom of the last element.
        # There are 8 spacing units between elements and the height of the last button.
        total_ui_block_height = (8 * spacing) + button_height 
        start_y = (settings.SCREEN_HEIGHT - total_ui_block_height) // 2

        # Resolution Dropdown
        resolution_options = [f"{w}x{h}" for w, h in settings.RESOLUTIONS]
        current_resolution = f"{settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT}"
        self.dropdowns.append(Dropdown(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height,
            resolution_options, self._set_resolution, default_option=current_resolution
        ))

        # Add instructional text for dropdown
        dropdown_x = settings.SCREEN_WIDTH // 2 - button_width // 2
        dropdown_y = start_y
        text_offset_x = button_width // 2 + 10 # Offset to the right of the dropdown
        text_offset_y_line1 = -10 # Above the dropdown
        text_offset_y_line2 = 10 # Below the dropdown

        self.resolution_instructions_line1_pos = (dropdown_x + button_width + 10, dropdown_y + button_height // 2 - 15)
        self.resolution_instructions_line2_pos = (dropdown_x + button_width + 10, dropdown_y + button_height // 2 + 5)


        # VSync Toggle
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing, button_width, button_height,
            f"VSync: {'On' if self.game.settings.VSYNC else 'Off'}", self._toggle_vsync
        ))

        # Borderless Toggle
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * spacing, button_width, button_height,
            f"Borderless: {'On' if self.game.settings.BORDERLESS else 'Off'}", self._toggle_borderless
        ))

        # Fullscreen Toggle
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * spacing, button_width, button_height,
            "Toggle Fullscreen", self._toggle_fullscreen
        ))

        # Music Volume Slider
        self.volume_slider_rect = pygame.Rect(
            settings.SCREEN_WIDTH // 2 - 100, start_y + 4 * spacing, 200, 20
        )
        self.volume_handle_rect = pygame.Rect(
            self.volume_slider_rect.x + self.volume * (self.volume_slider_rect.width - 10),
            self.volume_slider_rect.centery - 10, 20, 20
        )

        # Mute Button
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 6 * spacing, button_width, button_height,
            "Toggle Mute", self._toggle_mute
        ))

        # Next Song Button
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 7 * spacing, button_width, button_height,
            "Next Song", self._next_song
        ))

        # Back Button
        def back_button_action():
            if self.game.scene_manager.previous_scene_name == "title_screen":
                self.game.scene_manager.set_scene("title_screen")
            else:
                self.game.scene_manager.set_scene("pause_menu")

        back_button_text = "Back to Pause Menu"
        if self.game.scene_manager.previous_scene_name == "title_screen":
            back_button_text = "Back to Main Menu"

        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 8 * spacing, button_width, button_height,
            back_button_text, back_button_action
        ))

    def _set_resolution(self, resolution_str):
        width, height = map(int, resolution_str.split('x'))
        self.game.settings.SCREEN_WIDTH = width
        self.game.settings.SCREEN_HEIGHT = height
        self.game.apply_display_settings()
        self.recreate_ui()  # Recreate the UI with the new resolution
        self.game.logger.info(f"Resolution set to {width}x{height}")

    def _toggle_vsync(self):
        self.game.settings.VSYNC = not self.game.settings.VSYNC
        self.game.apply_display_settings()
        self.recreate_ui()
        self.game.logger.info(f"VSync: {self.game.settings.VSYNC}")

    def _toggle_borderless(self):
        self.game.settings.BORDERLESS = not self.game.settings.BORDERLESS
        self.game.apply_display_settings()
        self.recreate_ui()
        self.game.logger.info(f"Borderless: {self.game.settings.BORDERLESS}")

    def _toggle_fullscreen(self):
        self.game.settings.FULLSCREEN = not self.game.settings.FULLSCREEN
        self.game.apply_display_settings()
        self.recreate_ui()
        self.game.logger.info(f"Fullscreen: {self.game.settings.FULLSCREEN}")

    def _toggle_mute(self):
        self.game.music_manager.toggle_mute()
        self.volume = self.game.music_manager.get_volume() # Update volume after mute/unmute
        self.recreate_ui() # Recreate UI to update handle position if needed

    def _next_song(self):
        self.game.music_manager.play_next_song()

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                break
        for dropdown in self.dropdowns:
            if dropdown.handle_event(event):
                break

        # Handle volume slider dragging
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_handle_rect.collidepoint(event.pos):
                self.dragging_volume_slider = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_volume_slider = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_volume_slider:
                # Calculate new volume based on mouse position
                new_handle_x = max(self.volume_slider_rect.x, min(event.pos[0] - self.volume_handle_rect.width // 2, self.volume_slider_rect.right - self.volume_handle_rect.width))
                self.volume = (new_handle_x - self.volume_slider_rect.x) / (self.volume_slider_rect.width - self.volume_handle_rect.width)
                self.game.music_manager.set_volume(self.volume)
                self.volume_handle_rect.x = new_handle_x

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        # Position the "SETTINGS" title dynamically above the UI elements
        draw_text(screen, "SETTINGS", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, self.buttons[0].rect.y - 80, align="center")
        
        # Draw volume slider
        pygame.draw.rect(screen, settings.UI_SECONDARY_COLOR, self.volume_slider_rect, 2)
        pygame.draw.rect(screen, settings.UI_PRIMARY_COLOR, self.volume_handle_rect)
        draw_text(screen, f"Volume: {int(self.volume * 100)}%", settings.UI_FONT_SIZE_SMALL, settings.UI_PRIMARY_COLOR, self.volume_slider_rect.centerx, self.volume_slider_rect.y - 20, align="center")

        # Draw dropdown instructions with Unicode characters
        draw_text(screen, "↑↓ to scroll", settings.UI_FONT_SIZE_SMALL, settings.UI_PRIMARY_COLOR, self.resolution_instructions_line1_pos[0], self.resolution_instructions_line1_pos[1], align="left")
        draw_text(screen, "ENTER to select", settings.UI_FONT_SIZE_SMALL, settings.UI_PRIMARY_COLOR, self.resolution_instructions_line2_pos[0], self.resolution_instructions_line2_pos[1], align="left")

        for button in self.buttons:
            button.draw(screen)
        for dropdown in self.dropdowns:
            dropdown.draw(screen)

    def reinitialize_fonts(self):
        self.game.logger.info("Reinitializing fonts for SettingsMenu.")
        self.recreate_ui()

    def enter(self):
        self.game.logger.info("Entering Settings Menu.")
        self.recreate_ui()

    def exit(self):
        self.game.logger.info("Exiting Settings Menu.")

    def update(self, dt):
        pass