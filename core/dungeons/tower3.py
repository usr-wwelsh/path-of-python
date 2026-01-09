
import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene
from utility.resource_path import resource_path

class tower3(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        # Load dungeon data if not provided
        if dungeon_data is None:
            dungeon_data_path = os.path.abspath(resource_path(os.path.join("data", "dungeons", "tower3.json")))
            try:
                with open(dungeon_data_path, "r") as f:
                    dungeon_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading dungeon data from {dungeon_data_path}: {e}")
                dungeon_data = {}

        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data)
        self.name = "tower3"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.entities = []  # Initialize an empty list of entities
        self.effects = pygame.sprite.Group()  # Initialize the effects group
        self.arrow_rect = None
        self.arrow_screen_pos = (0, 0)

    def load_dungeon_data(self, dungeon_name):
        # This method is no longer strictly needed if dungeon_data is passed directly,
        # but kept for compatibility or if other parts of the code rely on it.
        dungeon_data_path = os.path.abspath(resource_path(os.path.join("data", "dungeons", f'{dungeon_name}.json')))

        try:
            with open(dungeon_data_path, "r") as f:
                dungeon_data = json.load(f)
            return dungeon_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dungeon data from {dungeon_data_path}: {e}")
            return {}

    def update(self, dt):
        # Update rectangle position for click detection
        self._calculate_rect_position()

        # Check if player is standing on the rectangle
        if self.arrow_rect and self.player.rect.colliderect(self.arrow_rect):
            self.game.scene_manager.set_scene("tower4")
            return True

        super().update(dt, self.entities)
        self.effects.update(dt)

    def handle_event(self, event):
        return super().handle_event(event)

    def draw(self, screen):
        super().draw(screen)
        # Draw the rectangle for debugging purposes, adjusting for camera
        if self.arrow_rect:
            draw_rect = self.arrow_rect.move(-self.camera_x, -self.camera_y)
            pygame.draw.rect(screen, (0, 0, 0), draw_rect, 0) # Black filled rectangle
            pygame.draw.rect(screen, (255, 255, 0), draw_rect, 1) # yellow outline rectangle

        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))

    def _calculate_rect_position(self):
        """Calculate and store the rectangle's world position"""
        tile_size = 64
        rect_size = 500

        # Calculate position at bottom-right of the map in world coordinates
        rect_world_x = 300
        rect_world_y = 300

        # Create rect for collision detection in world coordinates
        self.arrow_rect = pygame.Rect(
            int(rect_world_x - rect_size / 2),
            int(rect_world_y - rect_size / 2),
            rect_size,
            rect_size
        )
