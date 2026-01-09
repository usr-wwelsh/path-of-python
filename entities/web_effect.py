import pygame
from config.constants import TILE_SIZE
import os
from utility.resource_path import resource_path

class WebEffect(pygame.sprite.Sprite):
    def __init__(self, game, x, y, slow_amount, entangle_duration):
        super().__init__()
        self.game = game
        self.slow_amount = slow_amount
        self.entangle_duration = entangle_duration
        self.creation_time = pygame.time.get_ticks()
        self.duration = 5000 # Web lasts for 5 seconds (adjust as needed)

        # Load web graphic
        try:
            self.image = pygame.image.load(resource_path(os.path.join("graphics", "effect", "web.png"))).convert_alpha()
        except FileNotFoundError:
            print("Web effect image not found! Using a placeholder.")
            self.image = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2))
            self.image.fill((128, 128, 128)) # Gray placeholder

        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 2)) # Scale to a reasonable size
        self.rect = self.image.get_rect(center=(x, y))
        self.game.current_scene.effects.add(self) # Add to effects group
        self.affected_enemies = set() # Keep track of affected enemies

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.duration:
            self.kill() # Remove web after its duration

        # Apply effects to enemies within the web's radius
        for enemy in self.game.current_scene.enemies:
            if self.rect.colliderect(enemy.rect) and enemy not in self.affected_enemies:
                # Apply slow and entangle (entangle can be a stronger/different slow)
                if hasattr(enemy, 'apply_slow'):
                    enemy.apply_slow(self.slow_amount, self.entangle_duration) # Using slow for entangle for now
                    self.affected_enemies.add(enemy)