import pygame
import json
import os
from entities.npc import NPC
from core.base_gameplay_scene import BaseGameplayScene
from progression.quest_tracker import QuestTracker
import random
from utility.resource_path import resource_path

class tower4(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        # Load dungeon data if not provided
        if dungeon_data is None:
            dungeon_data_path = os.path.abspath(resource_path(os.path.join("data", "dungeons", "tower4.json")))
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
        npc_x = 2560
        npc_y = 2560
        # Provide a specific sprite path for the Profit Scribe NPC
        self.maze_npc = NPC(game, npc_x, npc_y, npc_width, npc_height, (0, 255, 0), "Charlie the Calm", "charlie_tower_dialogue", sprite="graphics/player/base/gnome_m.png")
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data, friendly_entities=[self.maze_npc])
        self.npc_screen_rect = None
        self.name = "tower4"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.entities = pygame.sprite.Group(self.enemies, self.friendly_entities)
        self.effects = pygame.sprite.Group()
        quest_tracker = QuestTracker()
        quest_tracker.update_quest_progress("defend", "the Broadcast Station")
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 30000  # 30 seconds in milliseconds
        self.spawning_active = False
        self.last_spawn_time = 0
        self.initial_spawn_done = False

    def load_dungeon_data(self, dungeon_name):
        dungeon_data_path = os.path.abspath(resource_path(os.path.join("data", "dungeons", f'{dungeon_name}.json')))

        try:
            with open(dungeon_data_path, "r") as f:
                dungeon_data = json.load(f)
            return dungeon_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dungeon data from {dungeon_data_path}: {e}")
            return {}

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if self.maze_npc:
            self.npc_screen_rect = pygame.Rect(
                self.maze_npc.rect.x - self.camera_x,
                self.maze_npc.rect.y - self.camera_y,
                self.maze_npc.rect.width,
                self.maze_npc.rect.height
            )

        if self.maze_npc and self.maze_npc.dialogue_finished and not self.initial_spawn_done:
            self.maze_npc.dialogue_finished = False
            self.game.hud.start_countdown(300000)  # 5 minutes in milliseconds
            self.spawning_active = True
            self.initial_spawn_done = True
            self.last_spawn_time = current_time
            self.start_enemy_spawn()  # Initial spawn immediately

        if self.spawning_active:
            if current_time - self.last_spawn_time >= self.enemy_spawn_interval:
                self.start_enemy_spawn()
                self.last_spawn_time = current_time

        super().update(dt, self.entities)
        if self.game.hud.countdown_active and self.game.hud.countdown_duration <= 100:
            self.game.quest_tracker.update_quest_progress("kill", "the Choir Disruptors")
            self.game.quest_tracker.update_quest_progress("keep_alive", "for 5 minutes")
            self.spawning_active = False
        self.effects.update(dt)

    def start_enemy_spawn(self):
        enemy_types = ["choir_disruptor", "high_comptroller"]
        spawn_positions = [(240, 240), (4480, 4480), (2400, 2720), (3000, 2400)]

        from combat.enemy_factory import EnemyFactory
        self.enemy_factory = EnemyFactory(self.game)

        for _ in range(20):
            enemy_type = random.choice(enemy_types)
            position = random.choice(spawn_positions)
            enemy = self.enemy_factory.create_enemy(enemy_type, position[0], position[1])
            self.entities.add(enemy)
            self.enemies.add(enemy)

    def draw(self, screen):
        super().draw(screen)
        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.npc_screen_rect and self.npc_screen_rect.collidepoint(event.pos):
                for entity in self.friendly_entities:
                    if isinstance(entity, NPC) and entity.name == "Charlie the Calm":
                        entity.interact(self.game.player)
                        break