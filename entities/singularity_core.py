import pygame
import os
import random
import math
from config.constants import TILE_SIZE

class SingularityCore(pygame.sprite.Sprite):
    def __init__(self, target, source, duration=2000, damage_multiplier=10.0, pull_radius=5 * TILE_SIZE):
        super().__init__()
        self.target = target
        self.source = source
        self.duration = duration  # Duration of the singularity in milliseconds
        self.damage_multiplier = damage_multiplier  # Multiplier for the damage dealt
        self.pull_radius = pull_radius  # Radius in which enemies are pulled
        self.start_time = pygame.time.get_ticks()
        self.image = pygame.Surface([10, 10])  # Placeholder image
        self.image.fill((0, 0, 0))  # Black color
        self.rect = self.image.get_rect(center=self.target.rect.center)
        self.initial_position = self.target.rect.center  # Store initial position

    def update(self, dt):
        """Updates the singularity effect, pulling in enemies and dealing damage after a delay."""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time

        if elapsed_time > self.duration:
            self.detonate()
            self.kill()  # Remove the singularity effect
        else:
            self.pull_enemies(dt)

    def pull_enemies(self, dt):
        """Pulls nearby enemies towards the singularity."""
        # Iterate over all enemies in the current scene
        for sprite in self.source.game.current_scene.enemies:
            # Ensure it's an Enemy and not the source or the target
            if isinstance(sprite, pygame.sprite.Sprite) and sprite != self.source and sprite != self.target:
                # Calculate distance to the enemy
                dx, dy = self.rect.centerx - sprite.rect.centerx, self.rect.centery - sprite.rect.centery
                dist = math.hypot(dx, dy)

                if dist < self.pull_radius:
                    # Normalize direction vector
                    dx, dy = dx / dist, dy / dist
                    # Calculate movement towards the singularity
                    move_x = dx * 50 * dt  # Adjust speed as needed
                    move_y = dy * 50 * dt

                    # Apply movement
                    sprite.rect.x += move_x
                    sprite.rect.y += move_y

    def detonate(self):
        """Deals damage to the target and nearby enemies."""
        # Calculate the damage amount
        damage_amount = self.target.max_life * self.damage_multiplier
        print(f"Singularity Core detonated, dealing {damage_amount} damage!")
        # Deal damage to the target
        self.target.take_damage(damage_amount)

        # Deal damage to nearby enemies
        for sprite in self.source.game.current_scene.enemies:
            # Ensure it's an Enemy and not the source or the target
            if isinstance(sprite, pygame.sprite.Sprite) and sprite != self.source and sprite != self.target:
                # Calculate distance to the enemy
                dx, dy = self.rect.centerx - sprite.rect.centerx, self.rect.centery - sprite.rect.centery
                dist = math.hypot(dx, dy)

                if dist < self.pull_radius:
                    # Deal damage to the enemy
                    sprite.take_damage(damage_amount)
                    print(f"Singularity Core dealt {damage_amount} damage to {sprite.name}!")