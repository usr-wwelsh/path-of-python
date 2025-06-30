import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene
from entities.player import Player
from entities.enemy import Enemy
from entities.npc import NPC
from items.item import Item
from ui.hud import HUD
from config.constants import TILE_SIZE, KEY_INTERACT
import math

class Quest001Scene(BaseGameplayScene):
    def __init__(self, game, player=None, hud=None, dungeon_data=None):
        # Call BaseGameplayScene's init, passing dungeon_data for tileset name
        super().__init__(game, player, hud, tileset_name=dungeon_data.get('tileset', 'default'), dungeon_data=dungeon_data)
        self.game = game
        self.dungeon_data = dungeon_data
        self.tile_size = TILE_SIZE
        
        # Explicitly load map dimensions and tile map from dungeon_data
        # BaseGameplayScene does not set these directly from dungeon_data in its __init__
        self.tile_map = dungeon_data.get('tile_map', [])
        self.map_width = dungeon_data.get('width', 0)
        self.map_height = dungeon_data.get('height', 0)

        self.entities = []  # Initialize an empty list of entities
        self.npcs = pygame.sprite.Group() # NPCs are specific to this scene
        self.effects = pygame.sprite.Group() # Effects are specific to this scene
        self.items = pygame.sprite.Group() # Items are specific to this scene
        self.name = "Quest001Scene" # Set scene name

        if self.dungeon_data:
            # BaseGameplayScene's __init__ loads enemies if dungeon_data is passed.
            # We only need to load NPCs and items here.
            self.load_npcs(self.dungeon_data.get('npcs', []))
            self.load_items(self.dungeon_data.get('items', []))
            self.load_decorations(self.dungeon_data.get('decorations', []))
            
            # Set player spawn point - find the 'player_spawn' tile or the first 'floor' tile
            player_spawn_x, player_spawn_y = 0, 0
            spawn_found = False
            if self.tile_map:
                for y, row in enumerate(self.tile_map):
                    for x, tile_type in enumerate(row):
                        if tile_type == 'player_spawn':
                            player_spawn_x = x * self.tile_size
                            player_spawn_y = y * self.tile_size
                            spawn_found = True
                            break
                        elif tile_type == 'floor' and not spawn_found: # Fallback to first floor tile if no specific spawn
                            player_spawn_x = x * self.tile_size
                            player_spawn_y = y * self.tile_size
                            spawn_found = True # Mark as found, but keep looking for 'player_spawn'
                    if spawn_found and 'player_spawn' in row: # If player_spawn was found in this row, break outer loop
                        break
                    elif spawn_found and 'player_spawn' not in row: # If only floor was found, and no player_spawn in this row, break
                        break
            
            if self.player:
                self.player.rect.x = player_spawn_x
                self.player.rect.y = player_spawn_y
        else:
            self.game.logger.error("Quest001Scene: No dungeon data provided.")

    def load_npcs(self, npcs_data):
        """Loads NPCs from the dungeon data."""
        if not npcs_data: # If no NPC data, nothing to load
            print("Quest001Scene: No NPCs to load.")
            return

        # Calculate the center of the room in pixel coordinates
        # Assuming map_width and map_height are in tiles
        center_x_pixels = (self.map_width * self.tile_size) / 2
        center_y_pixels = (self.map_height * self.tile_size) / 2
        
        for npc_data in npcs_data:
            # Adjust for NPC sprite size to truly center it
            npc_width = TILE_SIZE 
            npc_height = TILE_SIZE 
            x_pos = center_x_pixels - (npc_width / 2)
            y_pos = center_y_pixels - (npc_height / 2)

            name = npc_data.get('name', "NPC")
            dialogue_id = npc_data.get('dialogue_id')
            sprite = npc_data.get('sprite')
            # Pass width, height, color, name, and dialogue_id to the NPC constructor
            npc = NPC(self.game, x_pos, y_pos, npc_width, npc_height, (0, 255, 0), name, dialogue_id, sprite)
            self.npcs.add(npc)
        print(f"Quest001Scene: Loaded {len(self.npcs)} NPCs.")

    def load_items(self, items_data):
        """Loads items from the dungeon data."""
        for item_data in items_data:
            item_name = item_data['name']
            x, y = item_data['x'], item_data['y']
            item = Item(item_name, x, y) # Assuming Item constructor takes name, x, y
            self.items.add(item)
        print(f"Quest001Scene: Loaded {len(self.items)} items.")

    def enter(self):
        self.game.player = self.player
        self.game.hud = self.hud
        self.game.current_map = self.tile_map
        # Reset the enemies_loaded flag
        # self.enemies_loaded = False # This is no longer needed, as the enemies are loaded in __init__
        # Combine all sprite groups for game.all_sprites
        self.game.all_sprites = pygame.sprite.Group(
            self.player,
            self.enemies, # From BaseGameplayScene
            self.projectiles, # From BaseGameplayScene
            self.portals, # From BaseGameplayScene
            self.friendly_entities, # From BaseGameplayScene
            self.npcs, # Specific to Quest001Scene
            self.items, # Specific to Quest001Scene
            self.effects # Specific to Quest001Scene
        )
        print(f"Quest001Scene: Number of enemies: {len(self.enemies)}")
        self.game.logger.info("Entered Quest001Scene scene.")

    def exit(self):
        self.game.logger.info("Exited Quest001Scene scene.")

    def handle_event(self, event):
        super().handle_event(event) # Call base class handle_event for common input

        if event.type == pygame.KEYDOWN:
            if event.key == KEY_INTERACT: # Handle interaction key
                if self.player:
                    # Check for interaction with NPCs
                    for npc_sprite in self.npcs:
                        npc_world_x = npc_sprite.rect.centerx
                        npc_world_y = npc_sprite.rect.centery
                        player_world_x = self.player.rect.centerx
                        player_world_y = self.player.rect.centery

                        distance = math.hypot(player_world_x - npc_world_x, player_world_y - npc_world_y)

                        # Define interaction distance (e.g., 1.5 tiles)
                        interaction_distance = TILE_SIZE * 2.5

                        if distance < interaction_distance:
                            # Start dialogue with this NPC using the NPC's own interact method
                            npc_sprite.interact(self.player)
                            break # Interact with only one NPC at a time
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left-click
            # Check for NPC interaction
            for npc_sprite in self.npcs:
                # Calculate NPC's screen position
                npc_screen_x = (npc_sprite.rect.x - self.camera_x) * self.zoom_level
                npc_screen_y = (npc_sprite.rect.y - self.camera_y) * self.zoom_level

                # Create a rect for the NPC at its screen position
                npc_screen_rect = pygame.Rect(npc_screen_x, npc_screen_y,
                                              npc_sprite.rect.width * self.zoom_level,
                                              npc_sprite.rect.height * self.zoom_level)

                if npc_screen_rect.collidepoint(event.pos):
                    npc_sprite.interact(self.player) # Pass the player object
                    return # Consume event if NPC is interacted with

    def update(self, dt):
        super().update(dt) # Call base class update for player, enemies, projectiles, portals, friendly_entities, camera
        
        # Update scene-specific entities
        self.npcs.update(dt) # NPCs might need their own update logic
        self.effects.update(dt) # Update effects
        
        # Check for player-item collisions
        collided_items = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in collided_items:
            self.player.inventory.add_item(item)
            self.game.logger.info(f"Player picked up {item.name}")

    def draw(self, screen):
        super().draw(screen) # Call base class draw for map, player, enemies, friendly_entities, portals, projectiles, HUD, dialogue
# Draw decorations
        for decoration in self.decorations:
            screen_x = decoration['x'] * self.tile_size - self.camera_x * self.zoom_level
            screen_y = decoration['y'] * self.tile_size - self.camera_y * self.zoom_level
            scaled_image = pygame.transform.scale(decoration['image'], (int(decoration['image'].get_width() * self.zoom_level * 2), int(decoration['image'].get_height() * self.zoom_level * 2)))
            screen.blit(scaled_image, (screen_x, screen_y))
        
        # Draw scene-specific entities (NPCs, items, and effects)
        for npc_sprite in self.npcs:
            # Calculate sprite's position relative to the camera
            npc_x = (npc_sprite.rect.x - self.camera_x) * self.zoom_level
            npc_y = (npc_sprite.rect.y - self.camera_y) * self.zoom_level
            scaled_npc_image = pygame.transform.scale(npc_sprite.image, (int(npc_sprite.image.get_width() * self.zoom_level), int(npc_sprite.image.get_height() * self.zoom_level)))
            screen.blit(scaled_npc_image, (npc_x, npc_y))

        for item_sprite in self.items:
            # Calculate sprite's position relative to the camera
            item_x = (item_sprite.rect.x - self.camera_x) * self.zoom_level
            item_y = (item_sprite.rect.y - self.camera_y) * self.zoom_level
            scaled_item_image = pygame.transform.scale(item_sprite.image, (int(item_sprite.image.get_width() * self.zoom_level), int(item_sprite.image.get_height() * self.zoom_level)))
            screen.blit(scaled_item_image, (item_x, item_y))

        for effect_sprite in self.effects:
            # Calculate sprite's position relative to the camera
            effect_x = (effect_sprite.rect.x - self.camera_x) * self.zoom_level
            effect_y = (effect_sprite.rect.y - self.camera_y) * self.zoom_level
            scaled_effect_image = pygame.transform.scale(effect_sprite.image, (int(effect_sprite.image.get_width() * self.zoom_level), int(effect_sprite.image.get_height() * self.zoom_level)))
            screen.blit(scaled_effect_image, (effect_x, effect_y))