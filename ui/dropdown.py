import pygame
from core.utils import draw_text
from config.settings import UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, UI_BACKGROUND_COLOR, UI_ACCENT_COLOR, UI_FONT, UI_FONT_SIZE_DEFAULT
from utility.font_cache import get_font

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
        self.font = get_font(None, UI_FONT_SIZE_DEFAULT)  # Use font cache for stability
        self.highlighted_option_index = 0
        self.max_visible_options = 10  # Limit to 10 visible options
        self.scroll_offset = 0 # Index of the first visible option

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                # Reset highlighted option and scroll offset when opening/closing with mouse
                if self.is_open:
                    try:
                        self.highlighted_option_index = self.options.index(self.selected_option)
                    except ValueError:
                        self.highlighted_option_index = 0
                    self.scroll_offset = max(0, min(self.highlighted_option_index - self.max_visible_options // 2, len(self.options) - self.max_visible_options))
                return True
            elif self.is_open: # Clicked outside dropdown while open, close it
                self.is_open = False
                return True
        elif event.type == pygame.KEYDOWN and self.is_open:
            if event.key == pygame.K_UP:
                self.highlighted_option_index = (self.highlighted_option_index - 1) % len(self.options)
                if self.highlighted_option_index < self.scroll_offset:
                    self.scroll_offset = self.highlighted_option_index
                return True
            elif event.key == pygame.K_DOWN:
                self.highlighted_option_index = (self.highlighted_option_index + 1) % len(self.options)
                if self.highlighted_option_index >= self.scroll_offset + self.max_visible_options:
                    self.scroll_offset = self.highlighted_option_index - self.max_visible_options + 1
                return True
            elif event.key == pygame.K_RETURN:
                if self.options:
                    self.selected_option = self.options[self.highlighted_option_index]
                    self.is_open = False
                    self.callback(self.selected_option)
                return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, UI_SECONDARY_COLOR, self.rect)
        draw_text(screen, str(self.selected_option), UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, self.rect.centerx, self.rect.centery, align="center")

        if self.is_open:
            # Draw only visible options
            for i, option in enumerate(self.options[self.scroll_offset:self.scroll_offset + self.max_visible_options]):
                option_index_in_full_list = self.scroll_offset + i
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                
                # Highlight the currently selected option
                if option_index_in_full_list == self.highlighted_option_index:
                    pygame.draw.rect(screen, UI_ACCENT_COLOR, option_rect) # Use accent color for highlight
                else:
                    pygame.draw.rect(screen, UI_SECONDARY_COLOR, option_rect)
                
                draw_text(screen, str(option), UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, option_rect.centerx, option_rect.centery, align="center")

    def reinitialize_font(self):
        self.font = get_font(None, UI_FONT_SIZE_DEFAULT)