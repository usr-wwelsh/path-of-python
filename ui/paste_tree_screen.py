import pygame
import json
import os
import random
import math
from core.scene_manager import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, UI_BACKGROUND_COLOR
from core.utils import draw_text
from progression.paste_tree_manager import PasteTreeManager

class PasteTreeScreen(BaseScene):
    def __init__(self, game, player, hud, friendly_entities=None):
        super().__init__(game)
        self.player = player
        self.hud = hud
        self.friendly_entities = friendly_entities if friendly_entities is not None else []
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT)
        self.small_font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT - 10)
        self.glitch_font = pygame.font.SysFont("Courier New", 15)
        self.paste_tree_data = self.load_paste_tree_data()
        self.current_paste_tree = self.get_player_paste_tree()
        self.nodes = self.current_paste_tree.get("nodes", [])
        self.selected_node_index = 0
        self.node_positions = []
        self.background_chars = []
        self.generate_node_positions()
        self.generate_background_chars()
        self.paste_tree_manager = PasteTreeManager(game) # Initialize PasteTreeManager

    def load_paste_tree_data(self):
        paste_tree_path = os.path.join(os.getcwd(), "data", "paste_trees.json")
        try:
            with open(paste_tree_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading paste tree data: {e}")
            return {}

    def get_player_paste_tree(self):
        player_class = self.player.class_name.lower()
        return self.paste_tree_data.get(player_class, {"name": "Generic Paste Tree", "nodes": []})

    def generate_node_positions(self):
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = min(center_x, center_y) - 150
        angle_step = 360 / len(self.nodes) if self.nodes else 0

        for i, node in enumerate(self.nodes):
            angle = math.radians(i * angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions.append((x, y))

    def generate_background_chars(self):
        for _ in range(500):
            self.background_chars.append({
                "char": random.choice("0123456789!@#$%^&*()_+-=[]{}|;':,./<>?"),
                "pos": (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                "color": (random.randint(20, 50), random.randint(20, 80), random.randint(20, 50)),
                "speed": random.uniform(0.5, 2.0)
            })

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.game.scene_manager.set_scene("spawn_town")
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.selected_node_index = (self.selected_node_index + 1) % len(self.nodes)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.selected_node_index = (self.selected_node_index - 1) % len(self.nodes)
            elif event.key == pygame.K_RETURN:
                self.buy_selected_node()

    def buy_selected_node(self):
        if not self.nodes:
            return
        node = self.nodes[self.selected_node_index]
        node_id = node["id"]
        node_cost = 50000

        if self.player.paste >= node_cost:
            if node_id not in self.player.acquired_paste_nodes:
                self.player.paste -= node_cost
                # Use the PasteTreeManager to acquire the node
                self.paste_tree_manager.acquire_node(self.player, node_id)
                # Add a glorious visual effect for acquisition
            else:
                print(f"Player already has paste node: {node_id}")
        else:
            print("Not enough paste to buy this node!")

    def update(self, dt, entities=None):
        for char in self.background_chars:
            char["pos"] = (char["pos"][0], (char["pos"][1] + char["speed"]) % SCREEN_HEIGHT)
            if char["pos"][1] < 1: # Reset if it goes off screen
                 char["pos"] = (random.randint(0, SCREEN_WIDTH), 0)


    def draw(self, screen):
        screen.fill((0, 0, 5))

        for char in self.background_chars:
            draw_text(screen, char["char"], 15, char["color"], char["pos"][0], char["pos"][1])

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        # Draw connecting lines
        for i, pos in enumerate(self.node_positions):
            next_pos = self.node_positions[(i + 1) % len(self.node_positions)]
            pygame.draw.line(screen, (50, 50, 80), pos, next_pos, 1)
            pygame.draw.line(screen, (50, 50, 80), pos, (center_x, center_y), 1)


        # Draw nodes
        for i, (node, pos) in enumerate(zip(self.nodes, self.node_positions)):
            node_id = node["id"]
            is_acquired = node_id in self.player.acquired_paste_nodes
            is_selected = i == self.selected_node_index
            
            color = (100, 100, 100)
            if is_acquired:
                color = (0, 255, 0)
            elif self.player.paste >= 50000:
                color = (200, 200, 200)

            if is_selected:
                size = 30
                pygame.draw.circle(screen, (255, 255, 0), pos, size + 5, 2)
                # Pulsing effect for selection
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 10
                pygame.draw.circle(screen, (255, 255, 0, 100), pos, size + pulse, 2)
            else:
                size = 20

            pygame.draw.circle(screen, color, pos, size)
            if is_acquired:
                pygame.draw.circle(screen, (255,255,255), pos, size-5, 2)


        # Draw selected node info
        if self.nodes:
            selected_node = self.nodes[self.selected_node_index]
            draw_text(screen, selected_node["name"], UI_FONT_SIZE_DEFAULT + 5, (255, 255, 0), center_x, center_y - 50, align="center")
            
            # Glitchy description
            desc_text = selected_node["description"]
            for i, char in enumerate(desc_text):
                if random.random() < 0.05:
                    char = random.choice("!@#$%^&*")
                    color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))
                else:
                    color = UI_PRIMARY_COLOR
                
                char_surf = self.small_font.render(char, True, color)
                screen.blit(char_surf, (center_x - (self.small_font.size(desc_text)[0] / 2) + self.small_font.size(desc_text[:i])[0] + random.randint(-1,1), center_y + random.randint(-1,1)))


        # Draw title and paste count with corrupted style
        title = self.current_paste_tree["name"]
        corrupted_title = "".join([random.choice(title + " 01") if random.random() < 0.1 else c for c in title])
        draw_text(screen, corrupted_title, UI_FONT_SIZE_DEFAULT + 15, (255, 0, 255), SCREEN_WIDTH // 2, 50, align="center")
        
        paste_text = f"PR0F1T P4ST3: {int(self.player.paste / 50000)}"
        corrupted_paste = "".join([random.choice(paste_text + " 01") if random.random() < 0.1 else c for c in paste_text])
        draw_text(screen, corrupted_paste, UI_FONT_SIZE_DEFAULT, (0, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, align="center")
