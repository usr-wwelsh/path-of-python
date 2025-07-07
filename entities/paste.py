import pygame
import math

class Paste(pygame.sprite.Sprite):
    def __init__(self, x, y, amount):
        super().__init__()
        self.amount = amount
        self.radius = 12  # Reduced size to half
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        # Neon Green color for cyberpunk look
        neon_green = (39, 255, 10)

        # Create the base circle
        pygame.draw.circle(self.image, neon_green, (self.radius, self.radius), self.radius)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1000  # Adjust as needed
        self.magnet_range = 150  # Adjust as needed
        self.spiraling = False
        self.spiral_angle = 0
        self.spiral_radius = 50
        self.spiral_count = 0
        self.picked_up = False # Add a picked_up flag

        # Only "drop" if the amount is 1000 or more
        if self.amount < 1000:
            self.picked_up = True

    def update(self, dt, player):
        if self.picked_up:
            return # If already picked up, don't update

        distance = math.hypot(self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery)

        if not self.spiraling:
            # Move towards the player if within magnet range
            if distance < self.magnet_range:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                if distance > 0:
                    dx /= distance
                    dy /= distance
                self.rect.x += dx * self.speed * dt
                self.rect.y += dy * self.speed * dt

                if distance < 60:  # Start spiraling when close enough
                    self.spiraling = True
                    self.spiral_center = player.rect.center
        else:
            # Spiral around the player
            self.spiral_angle += 5 * dt * 100  # Adjust speed as needed
            self.spiral_radius -= 10 * dt # Reduce radius each spiral

            self.rect.centerx = self.spiral_center[0] + math.cos(self.spiral_angle) * self.spiral_radius
            self.rect.centery = self.spiral_center[1] + math.sin(self.spiral_angle) * self.spiral_radius

            if self.spiral_radius <= 0:
                self.spiral_count += 1
                self.spiral_radius = 50 # Reset radius
                if self.spiral_count >= 3:
                    self.spiraling = False # Stop spiraling after 3 times

    def draw(self, screen, camera_x, camera_y, zoom_level):
        if self.picked_up: # Only draw if not picked up
            return
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        screen.blit(self.image, (screen_x, screen_y))