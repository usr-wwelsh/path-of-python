
import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene
from entities.npc import NPC
from progression.quest_tracker import QuestTracker
from utility.resource_path import resource_path

class vault(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        # Load dungeon data if not provided
        if dungeon_data is None:
            dungeon_data_path = os.path.abspath(resource_path(os.path.join("data", "dungeons", "vault.json")))
            try:
                with open(dungeon_data_path, "r") as f:
                    dungeon_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading dungeon data from {dungeon_data_path}: {e}")
                dungeon_data = {}

        # Define NPC details
        npc_width = 64
        npc_height = 64
        # Update NPC coordinates to center of the map
        npc_x = 6400
        npc_y = 6400
        # Provide a specific sprite path for the Profit Scribe NPC
        self.maze_npc = NPC(game, npc_x, npc_y, npc_width, npc_height, (0, 255, 0), "archivist", "recursive_confessor_dialogue", sprite="graphics/player/base/gnome_m.png")
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data,friendly_entities=[self.maze_npc])
        self.name = "vault"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.effects = pygame.sprite.Group()  # Initialize the effects group
        self.entities = pygame.sprite.Group(self.enemies, self.friendly_entities)
        self.npc_screen_rect = None  # Initialize screen rect

        quest_tracker = QuestTracker()
        quest_tracker.update_quest_progress("bypass", "the biometric locks")

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
        super().update(dt, self.entities)  # Pass the entities list to the update method
        self.effects.update(dt) # Update the effects
        
        # Calculate NPC screen rect for mouse collision
        if self.maze_npc:
            self.npc_screen_rect = pygame.Rect(
                self.maze_npc.rect.x - self.camera_x,
                self.maze_npc.rect.y - self.camera_y,
                self.maze_npc.rect.width,
                self.maze_npc.rect.height
            )

    def draw(self, screen):
        super().draw(screen)
        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))
    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
            if self.npc_screen_rect and self.npc_screen_rect.collidepoint(event.pos):
                # Find the NPC in friendly_entities and interact with it
                for entity in self.friendly_entities:
                    if isinstance(entity, NPC) and entity.name == "archivist":
                        entity.interact(self.game.player)
                        break