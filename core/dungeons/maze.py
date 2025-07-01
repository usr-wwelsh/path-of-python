import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene
from entities.npc import NPC

class maze(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None, is_dark=False):
        # Define NPC details
        npc_width = 64
        npc_height = 64
        npc_x = 4290
        npc_y = 5367
        # Provide a specific sprite path for the Maze Wanderer
        maze_npc = NPC(game, npc_x, npc_y, npc_width, npc_height, (0, 255, 0), "Maze Wanderer", "maze_npc_dialogue", sprite="graphics/player/base/gnome_m.png")
        
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data, is_dark=is_dark, friendly_entities=[maze_npc])
        self.name = "maze"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.entities = []  # This list is now primarily for other scene-specific entities, not the NPC
        self.effects = pygame.sprite.Group()  # Initialize the effects group
        self.npc_screen_rect = None # Initialize npc_screen_rect

    def load_dungeon_data(self, dungeon_name):
        # This method is no longer strictly needed if dungeon_data is passed directly,
        # but kept for compatibility or if other parts of the code rely on it.
        dungeon_data_path = os.path.abspath(os.path.join(os.getcwd(), "data", "dungeons", f'{dungeon_name}.json'))
        try:
            with open(dungeon_data_path, "r") as f:
                dungeon_data = json.load(f)
            return dungeon_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dungeon data from {dungeon_data_path}: {e}")
            return {}

    def update(self, dt):
        super().update(dt, self.entities)  # Pass the entities list to the update method
        self.effects.update(dt) # Update the effects

    def draw(self, screen):
        super().draw(screen)
        # Draw friendly entities (NPCs) relative to the camera
        for entity in self.friendly_entities:
            # Calculate entity's screen position
            entity_screen_x = (entity.rect.x - self.camera_x) * self.zoom_level
            entity_screen_y = (entity.rect.y - self.camera_y) * self.zoom_level

            # Scale entity image
            scaled_entity_image = pygame.transform.scale(entity.image, (int(entity.rect.width * self.zoom_level), int(entity.rect.height * self.zoom_level)))
            scaled_rect = scaled_entity_image.get_rect(topleft=(int(entity_screen_x), int(entity_screen_y)))
            screen.blit(scaled_entity_image, scaled_rect)

            # Store the screen rectangle of the NPC
            if isinstance(entity, NPC) and entity.name == "Maze Wanderer":
                self.npc_screen_rect = scaled_rect

        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
            if self.npc_screen_rect and self.npc_screen_rect.collidepoint(event.pos):
                # Find the NPC in friendly_entities and interact with it
                for entity in self.friendly_entities:
                    if isinstance(entity, NPC) and entity.name == "Maze Wanderer":
                        entity.interact(self.game.player)
                        break
