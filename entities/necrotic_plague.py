import pygame
import os
import random
from config.constants import TILE_SIZE

class NecroticPlague(pygame.sprite.Sprite):
    def __init__(self, target, source, duration=10000, damage_percentage=0.10):
        super().__init__()
        self.target = target
        self.source = source
        self.duration = duration  # Duration of the plague in milliseconds
        self.damage_percentage = damage_percentage  # Percentage of max HP dealt per second
        self.start_time = pygame.time.get_ticks()
        self.stack_count = 1  # Initial stack count
        self.last_tick_time = pygame.time.get_ticks()

    def update(self, dt):
        """Updates the plague effect, dealing damage over time."""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time

        if elapsed_time > self.duration:
            self.kill()  # Remove the plague effect

        # Deal damage every second
        if current_time - self.last_tick_time >= 1000:
            damage_amount = self.target.health * self.damage_percentage * self.stack_count
            self.target.take_damage(damage_amount)
            print(f"Necrotic Plague dealt {damage_amount} damage to {self.target.name} (stack {self.stack_count})")
            self.last_tick_time = current_time

    def spread_plague(self, nearby_enemies):
        """Spreads the plague to nearby enemies."""
        # Implement the logic to spread the plague to nearby enemies here
        # This will likely involve creating new NecroticPlague objects and adding them to the nearby enemies
        print("Spreading necrotic plague to nearby enemies!")

    def increase_stack(self):
        """Increases the stack count of the plague."""
        self.stack_count += 1
        print(f"Necrotic Plague stack increased to {self.stack_count}!")