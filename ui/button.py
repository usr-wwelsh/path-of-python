import pygame
from config.settings import UI_FONT, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, UI_ACCENT_COLOR
from utility.font_cache import get_font

class Button:
    def __init__(self, x, y, width, height, text, action, font_size=UI_FONT_SIZE_DEFAULT, color=UI_PRIMARY_COLOR, bg_color=UI_SECONDARY_COLOR, hover_color=UI_ACCENT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font_name = UI_FONT  # Store font name
        self.font_size = font_size  # Store font size
        self.font = get_font(self.font_name, self.font_size)  # Use font cache for stability
        self.color = color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False

    def reinitialize_font(self):
        """Recreates the font object for the button."""
        self.font = get_font(self.font_name, self.font_size)

    def draw(self, surface):
        current_bg_color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, current_bg_color, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 2)  # Border

        if isinstance(self.text, str):
            text_surface = self.font.render(self.text, True, self.color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        else:  # Assume it's a pygame.Surface (image)
            image_rect = self.text.get_rect(center=self.rect.center)
            surface.blit(self.text, image_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.action()
                return True
        return False