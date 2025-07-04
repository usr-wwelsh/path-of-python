import pygame
from core.utils import draw_text
from config.settings import UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, UI_BACKGROUND_COLOR, UI_ACCENT_COLOR, UI_FONT, UI_FONT_SIZE_DEFAULT

class Dropdown:
    def __init__(self, x, y, width, height, options, callback, default_option=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.callback = callback
        self.is_open = False
        if default_option and default_option in self.options:
            self.selected_option = default_option
        else:
            self.selected_option = options[0] if options else None
        self.font = pygame.font.Font(None, UI_FONT_SIZE_DEFAULT)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            elif self.is_open:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_option = option
                        self.is_open = False
                        self.callback(option)
                        return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, UI_SECONDARY_COLOR, self.rect)
        draw_text(screen, str(self.selected_option), UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, self.rect.centerx, self.rect.centery, align="center")

        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(screen, UI_SECONDARY_COLOR, option_rect)
                draw_text(screen, str(option), UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, option_rect.centerx, option_rect.centery, align="center")

    def reinitialize_font(self):
        self.font = pygame.font.Font(None, UI_FONT_SIZE_DEFAULT)