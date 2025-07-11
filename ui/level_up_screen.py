import pygame
import pygame.gfxdraw
import json
import os
import random
import math
from core.scene_manager import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, UI_BACKGROUND_COLOR
from core.utils import draw_text

class LevelUpScreen(BaseScene):
    def __init__(self, game, player, hud, friendly_entities=None):
        super().__init__(game)
        self.player = player
        self.hud = hud
        self.friendly_entities = friendly_entities if friendly_entities is not None else []
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT)
        self.small_font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT - 10)
        self.glitch_font = pygame.font.SysFont("Courier New", 15)
        self.background_chars = []
        self.stat_buttons = []
        self.level_up_points = self.player.level - self.player.spent_level_points if self.player else 0
        self.generate_background_chars()
        self.generate_stat_buttons()
        self.right_mouse_down = False

    

    def generate_background_chars(self):
        """Generates a background of AI-themed characters."""
        characters = "01 "  # Reduced character set for a cleaner look
        num_chars = 200  # Reduced number of characters
        base_color = (0, 150, 0)  # Dark green for AI/code aesthetic

        for _ in range(num_chars):
            color_variation = random.randint(-20, 20)
            r = max(0, min(255, base_color[0] + color_variation))
            g = max(0, min(255, base_color[1] + color_variation))
            b = max(0, min(255, base_color[2] + color_variation))

            self.background_chars.append({
                "char": random.choice(characters),
                "pos": (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                "color": (r, g, b),
                "speed": random.uniform(0.2, 1.0)
            })

    def generate_stat_buttons(self):
        button_width = 200
        button_height = 40
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 3
        spacing = 50

        self.stat_buttons = [
            {"stat": "max_life", "label": "Health", "rect": pygame.Rect(start_x, start_y, button_width, button_height)},
            {"stat": "max_mana", "label": "Mana", "rect": pygame.Rect(start_x, start_y + spacing, button_width, button_height)},
            {"stat": "max_energy_shield", "label": "Energy Shield", "rect": pygame.Rect(start_x, start_y + 2 * spacing, button_width, button_height)},
            {"stat": "damage", "label": "Damage", "rect": pygame.Rect(start_x, start_y + 3 * spacing, button_width, button_height)},
            {"stat": "all", "label": "????", "rect": pygame.Rect(start_x, start_y + 4 * spacing, button_width, button_height)},
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_l:
                self.game.scene_manager.set_scene(self.game.scene_manager.previous_scene_name)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.stat_buttons:
                if button["rect"].collidepoint(event.pos):
                    if event.button == 3:
                        self.right_mouse_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                self.right_mouse_down = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.stat_buttons:
                if button["rect"].collidepoint(event.pos):
                    if button["stat"] == "all":
                        if event.button == 1 and self.level_up_points > 0:  # Left click
                            self.increase_all_stats()
                            self.level_up_points -= 1
                            self.player.spent_level_points += 1
                        elif event.button == 3 and self.level_up_points >= 10:  # Right click
                            while self.right_mouse_down and self.level_up_points >= 10:
                                for _ in range(10):
                                    self.increase_all_stats()
                                self.level_up_points -= 10
                                self.player.spent_level_points += 10
                                
                    elif event.button == 1 and self.level_up_points > 0:  # Left click
                        self.increase_stat(button["stat"])
                        self.level_up_points -= 1
                        self.player.spent_level_points += 1
                    elif event.button == 3 and self.level_up_points > 0:  # Right click
                        while self.right_mouse_down and self.level_up_points > 0:
                            self.increase_stat(button["stat"])
                            self.level_up_points -= 1
                            self.player.spent_level_points += 1
                            pygame.time.delay(50)
                        
    def increase_all_stats(self):
        self.increase_stat("max_life")
        self.increase_stat("max_mana")
        self.increase_stat("max_energy_shield")
        self.increase_stat("damage")
    def increase_stat(self, stat):
        if stat == "max_life":
            self.player.max_life += 200
            self.player.current_life += 200
        elif stat == "max_mana":
            self.player.max_mana += 200
            self.player.current_mana += 200
        elif stat == "max_energy_shield":
            self.player.max_energy_shield += 150
            self.player.current_energy_shield += 150
        elif stat == "damage":
            if hasattr(self.player, "base_damage"):
                self.player.base_damage += 10
                if hasattr(self.player, "unlocked_skills"):
                    for skill_id in self.player.unlocked_skills:
                        if skill_id == "arc" and hasattr(self.player, "arc_skill"):
                            self.player.arc_skill.bonus_damage += 10
                        elif skill_id == "cleave" and hasattr(self.player, "cleave_skill"):
                            self.player.cleave_skill.bonus_damage_min += 10
                            self.player.cleave_skill.bonus_damage_max += 10
                        elif skill_id == "cyclone" and hasattr(self.player, "cyclone_skill"):
                            self.player.cyclone_skill.bonus_damage_min += 10
                            self.player.cyclone_skill.bonus_damage_max += 10
                        elif skill_id == "ice_nova" and hasattr(self.player, "ice_nova_skill"):
                            self.player.ice_nova_skill.bonus_damage_min += 10
                            self.player.ice_nova_skill.bonus_damage_max += 10
                        elif skill_id == "summon_skeleton" and hasattr(self.player, "summon_skeletons_skill"):
                            self.player.summon_skeletons_skill.bonus_skeleton_damage += 20
                        elif skill_id == "summon_spiders" and hasattr(self.player, "summon_spiders_skill"):
                            self.player.summon_spiders_skill.bonus_spider_damage += 20
            else:
                print("Player does not have base_damage attribute")
        self.generate_stat_buttons()
        print(f"Increased {stat} by 10")

    def draw_glitch_text(self, screen, text, size, color, x, y, align="topleft"):
        """Draws text with a glitch effect."""
        for i in range(3):  # Draw multiple times with slight offsets
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            glitch_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw_text(screen, text, size, glitch_color, x + offset_x, y + offset_y, align=align)
        draw_text(screen, text, size, color, x, y, align=align)  # Draw the original text on top

    def update(self, dt, entities=None):
        for char in self.background_chars:
            char["pos"] = (char["pos"][0], (char["pos"][1] + char["speed"]) % SCREEN_HEIGHT)
            if char["pos"][1] < 1:  # Reset if it goes off screen
                char["pos"] = (random.randint(0, SCREEN_WIDTH), 0)

    def draw_stat_bars(self, screen):
        """Draws bar graphs for player stats."""
        bar_width = 50
        bar_height = 150
        bar_spacing = 75
        start_x = SCREEN_WIDTH // 6
        start_y = SCREEN_HEIGHT // 2

        stats = {
            "Health": self.player.max_life,
            "Mana": self.player.max_mana,
            "Energy Shield": self.player.max_energy_shield,
            "Damage": self.player.total_damage
        }

        for i, (stat_name, stat_value) in enumerate(stats.items()):
            x = start_x + i * bar_spacing
            y = start_y

            # Calculate bar height based on stat value (normalize for better visualization)
            max_stat_value = max(self.player.max_life, self.player.max_mana, self.player.max_energy_shield, self.player.total_damage)
            if max_stat_value == 0:
                bar_fill_height = 0
            else:
                bar_fill_height = int((stat_value / max_stat_value) * bar_height)

            # Draw the bar background
            pygame.draw.rect(screen, UI_SECONDARY_COLOR, (x, y, bar_width, bar_height))

            # Draw the filled bar
            bar_color = (0, 128, 255)  # Blue color for the bars
            pygame.draw.rect(screen, bar_color, (x, y + bar_height - bar_fill_height, bar_width, bar_fill_height))

            # Display stat name and value
            text_color = UI_PRIMARY_COLOR
            text_surface = self.small_font.render(f"{stat_name}: {stat_value}", True, text_color)
            text_rect = text_surface.get_rect(center=(x + bar_width // 2, y + bar_height + 20))
            screen.blit(text_surface, text_rect)

    def draw_radar_chart(self, screen):
        """Draws a radar chart for player stats."""
        center_x = SCREEN_WIDTH * 3 // 4
        center_y = SCREEN_HEIGHT // 2
        radius = 100
        num_stats = 4
        angles = [2 * math.pi * i / num_stats for i in range(num_stats)]

        stats = {
            "Health": self.player.max_life,
            "Mana": self.player.max_mana,
            "Energy Shield": self.player.max_energy_shield,
            "Damage": self.player.total_damage
        }

        # Normalize stats
        max_stat_value = max(self.player.max_life, self.player.max_mana, self.player.max_energy_shield, self.player.total_damage)
        if max_stat_value == 0:
            normalized_stats = [0] * num_stats
        else:
            normalized_stats = [stat_value / max_stat_value for stat_value in stats.values()]

        # Calculate points for the radar chart
        points = []
        for i, angle in enumerate(angles):
            x = center_x + radius * normalized_stats[i] * math.cos(angle)
            y = center_y + radius * normalized_stats[i] * math.sin(angle)
            points.append((x, y))

        # Draw the radar chart polygon
        pygame.draw.polygon(screen, (255, 255, 0), points, 2)

        # Draw the axes
        for i, angle in enumerate(angles):
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            pygame.draw.line(screen, UI_SECONDARY_COLOR, (center_x, center_y), (x, y), 1)

            # Display stat name and value
            stat_name = list(stats.keys())[i]
            stat_value = stats[stat_name]
            text_color = UI_PRIMARY_COLOR
            text_surface = self.small_font.render(f"{stat_name}: {stat_value}", True, text_color)
            text_rect = text_surface.get_rect(center=(x + 20 * math.cos(angle), y + 20 * math.sin(angle)))
            screen.blit(text_surface, text_rect)

    def draw_scatter_plot(self, screen):
        """Draws a scatter plot for player stats."""
        plot_width = 200
        plot_height = 150
        start_x = SCREEN_WIDTH // 6
        start_y = SCREEN_HEIGHT * 3 // 4

        stats = {
            "Health": self.player.max_life,
            "Mana": self.player.max_mana,
            "Energy Shield": self.player.max_energy_shield,
            "Damage": self.player.total_damage
        }

        # Normalize stats to fit within the plot area
        max_stat_value = max(self.player.max_life, self.player.max_mana, self.player.max_energy_shield, self.player.total_damage)
        if max_stat_value == 0:
            normalized_stats = {}
            for stat_name in stats:
                normalized_stats[stat_name] = 0
        else:
            normalized_stats = {}
            for stat_name, stat_value in stats.items():
                normalized_stats[stat_name] = stat_value / max_stat_value

        # Draw the plot background
        pygame.draw.rect(screen, UI_SECONDARY_COLOR, (start_x, start_y, plot_width, plot_height), 1)

        # Draw the data points
        point_color = (0, 255, 0)  # Green color for the points
        for i, (stat_name, stat_value) in enumerate(normalized_stats.items()):
            x = start_x + int(stat_value * plot_width)
            y = start_y + int((1 - stat_value) * plot_height)  # Invert y-axis for plot
            pygame.draw.circle(screen, point_color, (x, y), 5)

            # Display stat name
            text_color = UI_PRIMARY_COLOR
            text_surface = self.small_font.render(stat_name, True, text_color)
            text_rect = text_surface.get_rect(center=(x, start_y + plot_height + 10))
            screen.blit(text_surface, text_rect)

    def draw(self, screen):
        screen.fill((0, 0, 5))

        # Draw background characters
        for char in self.background_chars:
            draw_text(screen, char["char"], 15, char["color"], char["pos"][0], char["pos"][1])

        # Title with glitch effect
        title = "Level Up: System Enhancement"
        self.draw_glitch_text(screen, title, UI_FONT_SIZE_DEFAULT + 15, (255, 0, 255), SCREEN_WIDTH // 2, 50, align="center")

        # Level up points with a more technical label
        self.draw_glitch_text(screen, f"Enhancement Points Available: {self.level_up_points}", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, 100, align="center")

        # Draw stat buttons
        for button in self.stat_buttons:
            pygame.draw.rect(screen, UI_SECONDARY_COLOR, button["rect"])
            pygame.draw.rect(screen, UI_PRIMARY_COLOR, button["rect"], 2)
            self.draw_glitch_text(screen, button["label"], UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, button["rect"].centerx, button["rect"].centery, align="center")
            
            # Only show skills that match player's class
            if button["stat"] == "damage" and hasattr(self.player, "unlocked_skills"):
                skill_damages = []
                for skill_id in self.player.unlocked_skills:
                    if skill_id == "arc" and hasattr(self.player, "arc_skill"):
                        skill_damages.append(f"Arc: {self.player.arc_skill.base_damage}")
                    elif skill_id == "cleave" and hasattr(self.player, "cleave_skill"):
                        skill_damages.append(f"Cleave: {self.player.cleave_skill.base_damage['min']}-{self.player.cleave_skill.base_damage['max']}")
                    elif skill_id == "cyclone" and hasattr(self.player, "cyclone_skill"):
                        skill_damages.append(f"Cyclone: {self.player.cyclone_skill.base_damage['min']}-{self.player.cyclone_skill.base_damage['max']}")
                    elif skill_id == "ice_nova" and hasattr(self.player, "ice_nova_skill"):
                        skill_damages.append(f"Ice Nova: {self.player.ice_nova_skill.base_damage_min}-{self.player.ice_nova_skill.base_damage_max}")
                    elif skill_id == "summon_skeleton" and hasattr(self.player, "summon_skeletons_skill"):
                        skill_damages.append(f"Summon Skeleton: {self.player.summon_skeletons_skill.skeleton_damage}")
                    elif skill_id == "summon_spiders" and hasattr(self.player, "summon_spiders_skill"):
                        skill_damages.append(f"Summon Spiders: {self.player.summon_spiders_skill.spider_damage}")
                
                skill_damage_text = ", ".join(skill_damages)
                skill_damage_surface = self.small_font.render(skill_damage_text, True, UI_PRIMARY_COLOR)
                skill_damage_rect = skill_damage_surface.get_rect(topleft=(button["rect"].right + 10, button["rect"].top))
                screen.blit(skill_damage_surface, skill_damage_rect)

        # Draw stat bars
        self.draw_stat_bars(screen)

        # Draw radar chart
        self.draw_radar_chart(screen)

        # Draw scatter plot
        self.draw_scatter_plot(screen)