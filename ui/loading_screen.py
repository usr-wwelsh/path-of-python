import pygame
import time
import random
import math # Keep math for potential future use, or remove if not strictly needed for rounded rects


class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.messages = [
            "Preparing...",
            "The Profit Engine is rising...",
            "Use the teleporter in spawn town...",
            "Number keys for ALL dialog...",
            "We not pretending to load i promise..."
        ]
        self.current_message_index = 0
        self.start_time = time.time()
        self.duration = 10  # seconds, reduced for faster demonstration
        self.message_display_time = 2 # seconds per message
        self.last_message_change_time = time.time()

        # Reverting to original approach for screen dimensions, font size, and colors
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.FONT_SIZE = 36 # Default font size
        self.FONT_COLOR = (255, 255, 255) # White
        self.BACKGROUND_COLOR = (0, 0, 0) # Black

        pygame.display.set_caption("")
        
        # Load and set the window icon from an .ico file
        try:
            icon_path = "icon.ico" # Placeholder path for the icon file
            icon_surface = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_surface)
        except pygame.error as e:
            print(f"Could not load icon: {e}")
            # Fallback to a transparent icon if loading fails
            empty_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            pygame.display.set_icon(empty_surface)

        # Using default pygame font as get_font caused import error
        self.title_font = pygame.font.Font(None, 72) # Larger font for title
        self.message_font = pygame.font.Font(None, self.FONT_SIZE) # Standard font for messages

        # Colors for aesthetics (can be defined here without external imports)
        self.PRIMARY_COLOR = (100, 150, 255) # A nice blue
        self.SECONDARY_COLOR = (50, 100, 200) # Darker blue
        self.ACCENT_COLOR = (255, 200, 0) # Gold/Yellow for highlights

        self.loading_dots = 0
        self.last_dot_change_time = time.time()
        self.dot_interval = 0.5 # seconds

    def update(self):
        current_time = time.time()

        # Update loading message
        if current_time - self.last_message_change_time > self.message_display_time:
            self.current_message_index = (self.current_message_index + 1) % len(self.messages)
            self.last_message_change_time = current_time
        
        # Update loading dots animation
        if current_time - self.last_dot_change_time > self.dot_interval:
            self.loading_dots = (self.loading_dots + 1) % 4 # 0, 1, 2, 3 dots
            self.last_dot_change_time = current_time

    def draw(self):
        self.screen.fill(self.BACKGROUND_COLOR)

        # Draw Game Title
        game_title = "PATH OF PYTHON" 
        title_surface = self.title_font.render(game_title, True, self.ACCENT_COLOR)
        title_rect = title_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(title_surface, title_rect)

        # Draw loading message with animated dots
        message_text = self.messages[self.current_message_index] + "." * self.loading_dots
        text_surface = self.message_font.render(message_text, True, self.PRIMARY_COLOR)
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text_surface, text_rect)

        # Draw a professional progress bar
        elapsed_time = time.time() - self.start_time
        progress = min(elapsed_time / self.duration, 1.0)
        
        bar_width = int(self.SCREEN_WIDTH * 0.7)
        bar_height = 30
        bar_x = (self.SCREEN_WIDTH - bar_width) // 2
        bar_y = self.SCREEN_HEIGHT // 2 + 50
        bar_radius = 10 # For rounded corners

        # Background of the progress bar (darker shade)
        pygame.draw.rect(self.screen, self.SECONDARY_COLOR, (bar_x, bar_y, bar_width, bar_height), border_radius=bar_radius)

        # Filled part of the progress bar (primary color)
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.PRIMARY_COLOR, (bar_x, bar_y, fill_width, bar_height), border_radius=bar_radius)

        # Progress percentage text
        percentage_text = f"{int(progress * 100)}%"
        percentage_surface = self.message_font.render(percentage_text, True, self.FONT_COLOR)
        percentage_rect = percentage_surface.get_rect(center=(self.SCREEN_WIDTH // 2, bar_y + bar_height + 30))
        self.screen.blit(percentage_surface, percentage_rect)

        pygame.display.flip()
        

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.update()
            self.draw()
            

            if time.time() - self.start_time > self.duration:
                running = False
                pygame.display.set_caption("Path of Python")