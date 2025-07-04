import pygame
from core.scene_manager import BaseScene
from config import settings
from core.utils import draw_text
from ui.button import Button
from ui.dropdown import Dropdown

class SettingsMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.dropdowns = []
        self.recreate_ui()

    def recreate_ui(self):
        """Clears and recreates all UI elements with current screen dimensions."""
        self.buttons.clear()
        self.dropdowns.clear()

        button_width = 250
        button_height = 50
        start_y = settings.SCREEN_HEIGHT // 2 - 150
        spacing = 60

        # Resolution Dropdown
        resolution_options = [f"{w}x{h}" for w, h in settings.RESOLUTIONS]
        current_resolution = f"{settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT}"
        self.dropdowns.append(Dropdown(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height,
            resolution_options, self._set_resolution, default_option=current_resolution
        ))

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

        # Back Button
        def back_button_action():
            if self.game.scene_manager.previous_scene_name == "title_screen":
                self.game.scene_manager.set_scene("title_screen")
            else:
                self.game.scene_manager.set_scene("pause_menu")

        back_button_text = "Back to Pause Menu"
        if self.game.scene_manager.previous_scene_name == "title_screen":
            back_button_text = "Back to Main Menu"

        # Back Button
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 5 * spacing, button_width, button_height,
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

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                break
        for dropdown in self.dropdowns:
            if dropdown.handle_event(event):
                break

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        draw_text(screen, "SETTINGS", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4, align="center")
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