import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene
from progression.quest_tracker import QuestTracker
from entities.npc import NPC
from utility.resource_path import resource_path

class firewall(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        # Load dungeon data if not provided
        if dungeon_data is None:
            dungeon_data_path = os.path.abspath(resource_path(os.path.join("data", "dungeons", "firewall.json")))
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
        npc_x = 1600
        npc_y = 1600
        # Provide a specific sprite path for the Profit Scribe NPC
        self.maze_npc = NPC(game, npc_x, npc_y, npc_width, npc_height, (0, 255, 0), "neural_bot", "neural_cathedral_interface", sprite="graphics/player/base/gnome_m.png")
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data, friendly_entities=[self.maze_npc])
        self.name = "firewall"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.entities = pygame.sprite.Group(self.enemies, self.friendly_entities)
        self.npc_screen_rect = None  # Initialize screen rect
        self.effects = pygame.sprite.Group()  # Initialize the effects group
        self.firewall_kill_count = 0
        self.quest_tracker = QuestTracker()

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
                    if isinstance(entity, NPC) and entity.name == "neural_bot":
                        entity.interact(self.game.player)
                        break

    def enemy_killed(self, enemy):
        # Check if the quest is already completed to avoid unnecessary processing
        silicon_communion_quest = self.quest_tracker.get_quest_by_name("Silicon Communion")
        if silicon_communion_quest and silicon_communion_quest.is_completed:
            return

        if enemy.name == 'firewall':
            self.firewall_kill_count += 1
            
            # Only trigger the quest update logic once when the count is reached
            if self.firewall_kill_count == 25:
                active_quests = self.quest_tracker.get_active_quests()
                if not active_quests:
                    return

                quest = active_quests[0]
                if quest.name == "Silicon Communion":
                    objective_updated = False
                    for objective in quest.objectives:
                        if objective.get('description_original') == "Survive the dogma firewalls":
                            objective['count'] = objective['required']
                            objective_updated = True
                            break
                    
                    if objective_updated:
                        if quest.check_completion():
                            self.quest_tracker.complete_quest(quest)
