import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene
from progression.quest_tracker import QuestTracker
from entities.npc import NPC

class feast_hall2(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        self.enemies = pygame.sprite.Group() # Initialize enemies group
        self.friendly_entities = pygame.sprite.Group()  # Initialize friendly entities group
        self.entities = pygame.sprite.Group(self.enemies, self.friendly_entities) # Initialize the entities group
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data, friendly_entities=self.friendly_entities)
        self.name = "feast_hall2"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.effects = pygame.sprite.Group()  # Initialize the effects group
        
        self.quest_tracker = QuestTracker()
        self.quest_tracker.update_quest_progress("Interrupt", "the Sacrificial Algorithm")
        self.prisoners_spawned = False # Track if prisoners have been spawned

        if self.dungeon_data:
            self.load_enemies(self.dungeon_data.get('enemies', []))

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

    def spawn_prisoners(self):
        # Define prisoner NPC properties
        prisoner_color = (100, 100, 255)  # Example color
        prisoner_width = 64 # Double the width
        prisoner_height = 64 # Double the height
        
        # Calculate center of the map
        center_x = (self.map_width * 64) // 2  # Assuming tile size is 64
        center_y = (self.map_height * 64) // 2  # Assuming tile size is 64

        # Example spawn locations around the center
        spawn_locations = [
            (center_x - 64, center_y - 64),
            (center_x + 64, center_y - 64),
            (center_x, center_y),
            (center_x - 64, center_y + 64),
            (center_x + 64, center_y + 64),
        ]

        for i, (x, y) in enumerate(spawn_locations):
            if i == 2:  # The center NPC
                prisoner = NPC(self.game, x, y, prisoner_width, prisoner_height, prisoner_color, name="Prisoner", dialogue_id="tithing_prisoners_dialogue")
            else:
                prisoner = NPC(self.game, x, y, prisoner_width, prisoner_height, prisoner_color, name="Prisoner", dialogue_id="prisoner_dialogue")
            self.friendly_entities.add(prisoner) # Add to friendly_entities group
        self.prisoners_spawned = True

    def update(self, dt):
        super().update(dt, self.entities)  # Pass the entities list to the update method
        self.effects.update(dt) # Update the effects

        # Check if the "Kill 4 High Comptroller" objective is completed
        quest = self.quest_tracker.get_quest_by_name("The Last Tithing")
        if quest:
            kill_comptroller_objective = next((obj for obj in quest.objectives if obj['description_original'] == "Kill 4 High Comptroller"), None)
            if kill_comptroller_objective and kill_comptroller_objective["count"] >= kill_comptroller_objective["required"] and not self.prisoners_spawned:
                self.spawn_prisoners()

    def draw(self, screen):
        super().draw(screen)
        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse click
                # Get the mouse position in world coordinates
                world_x = (event.pos[0] + self.camera_x * self.zoom_level) / self.zoom_level
                world_y = (event.pos[1] + self.camera_y * self.zoom_level) / self.zoom_level

                # Check for interaction with friendly entities
                for entity in self.friendly_entities:
                    if isinstance(entity, NPC) and entity.rect.collidepoint(world_x, world_y):
                        # Start dialogue with this NPC
                        entity.interact(self.game.player)
                        break  # Interact with only one NPC at a time
