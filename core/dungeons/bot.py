import pygame
import json
import os
from core.scene_manager import SceneManager
from core.base_gameplay_scene import BaseGameplayScene
from progression.quest_tracker import QuestTracker

class bot(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data)
        self.name = "bot"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.entities = []
        self.effects = pygame.sprite.Group()
        self.arrow_rect = None
        self.arrow_screen_pos = (0, 0)

        quest_tracker = QuestTracker()
        quest_tracker.update_quest_progress("infiltrate", "the vault of tithes")

    def load_dungeon_data(self, dungeon_name):
        dungeon_data_path = os.path.abspath(os.path.join(os.getcwd(), "data", "dungeons", f'{dungeon_name}.json'))
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
            SceneManager.get_instance().transition_to_scene("vault")
            return True

        super().update(dt, self.entities)
        self.effects.update(dt)

    def handle_event(self, event):
        return super().handle_event(event)

    def draw(self, screen):
        super().draw(screen)
        # Draw the rectangle for debugging purposes
        if self.arrow_rect:
            pygame.draw.rect(screen, (255, 0, 0), self.arrow_rect, 2)

        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))

    def _calculate_rect_position(self):
        """Calculate and store the rectangle's screen position"""
        tile_size = 64
        rect_size = 150

        # Calculate position at bottom-right of the map
        rect_map_x = (self.map_width * tile_size) - (tile_size // 2) - 1050
        rect_map_y = (self.map_height * tile_size) - (tile_size // 2) - 1000

        # Convert to screen coordinates
        screen_x = rect_map_x - self.camera_x
        screen_y = rect_map_y - self.camera_y

        # Create rect for click detection
        self.arrow_rect = pygame.Rect(
            int(screen_x - rect_size / 2),
            int(screen_y - rect_size / 2),
            rect_size,
            rect_size
        )
