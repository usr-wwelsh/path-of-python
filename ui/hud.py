import pygame
from config.settings import SCREEN_WIDTH
from config.settings import SCREEN_HEIGHT
from config.settings import UI_FONT
from config.settings import UI_FONT_SIZE_DEFAULT
from config.settings import UI_PRIMARY_COLOR
from config.settings import UI_SECONDARY_COLOR
from config.settings import RED
from config.settings import BLUE
from config.settings import GREEN
from config.settings import UI_BACKGROUND_COLOR
from config.constants import KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4, KEY_POTION_1, KEY_POTION_2, KEY_POTION_3, KEY_POTION_4
from core.utils import draw_text
from ui.minimap import Minimap
from progression.quest_tracker import QuestTracker, QuestTrackerHUD # Removed Quest, as it's not directly used here
import json
import os

class HUD:
    def __init__(self, player, scene):
        self.player = player
        self.minimap = Minimap(self.player, [], scene) # Initialize with an empty entity list for now
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT)
        self.quest_tracker = QuestTracker() # Get the singleton instance
        self.quest_tracker_hud = QuestTrackerHUD(self.quest_tracker) # Instantiated QuestTrackerHUD
        self.skill_tree_data = self.load_skill_tree_data()
        self.original_screen_width = SCREEN_WIDTH
        self.original_screen_height = SCREEN_HEIGHT
        self.last_paste_count = 0
        self.show_prompt = False
        self.prompt_start_time = 0
        self.level_up_button_rect = pygame.Rect(0, 0, 0, 0)

    def load_skill_tree_data(self):
        skill_tree_path = os.path.join(os.getcwd(), "data", "skill_tree.json")
        try:
            with open(skill_tree_path, "r") as f:
                skill_tree_data = json.load(f)
            return skill_tree_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading skill tree data: {e}")
            return {"skills": []}

    def update(self, dt, entities):
        self.minimap.update(entities, self.player.game.current_scene)
        self.player.experience = self.player.experience  # Dummy change to force XP redraw

    def draw(self, screen):
        current_screen_width, current_screen_height = screen.get_size()
        width_scale = current_screen_width / self.original_screen_width
        height_scale = current_screen_height / self.original_screen_height

        # Draw Health Bar
        self._draw_bar(screen, 10 * width_scale, current_screen_height - (40 * height_scale), 300 * width_scale, 30 * height_scale, self.player.current_life, self.player.max_life, RED, "HP")

        # Draw Energy Shield Bar
        self._draw_bar(screen, 10 * width_scale, current_screen_height - (65 * height_scale), 300 * width_scale, 30 * height_scale, self.player.current_energy_shield, self.player.max_energy_shield, (100, 100, 200), "ES")

        # Draw Mana Bar
        self._draw_bar(screen, current_screen_width - (310 * width_scale), current_screen_height - (40 * height_scale), 300 * width_scale, 30 * height_scale, self.player.current_mana, self.player.max_mana, BLUE, "MP")
        # Draw Paste
        # draw_text(screen, f"Paste: {self.player.paste}", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, current_screen_width // 2, current_screen_height - (90 * height_scale), align="center")
        paste_x = current_screen_width // 2 - (150 * width_scale)
        paste_y = 10 * height_scale + 25 * height_scale + 5 * height_scale
        paste_width = 300 * width_scale
        paste_height = 20 * height_scale
        self._draw_bar(screen, paste_x, paste_y, paste_width, paste_height, self.player.paste % 50000, 50000, GREEN, "Profit Paste")
        paste_count = self.player.paste // 50000

        if paste_count > self.last_paste_count:
            self.show_prompt = True
            self.prompt_start_time = pygame.time.get_ticks()
            self.last_paste_count = paste_count

        draw_text(screen, str(paste_count), UI_FONT_SIZE_DEFAULT, RED, paste_x + paste_width + 10 * width_scale, paste_y + paste_height // 2, align="midleft")

        # Draw Skill Bar (Placeholder)
        #self._draw_skill_bar(screen)

        # Draw Potion Slots (Placeholder)
        #self._draw_potion_slots(screen)

        # Draw Minimap
        if not self.player.game.current_scene.is_dark: # Only draw minimap if scene is not dark
            self.minimap.draw(screen)
        # Draw Level/Experience Gauge
        self._draw_experience_gauge(screen, width_scale, height_scale)
        
        # Draw Level Up Button if player has skill points
        if self.player.level - self.player.spent_level_points > 0:
            self._draw_level_up_button(screen, width_scale, height_scale)

        # Draw Summon Spiders Cooldown Gauge only if player has the skill
        if self.player.has_skill("summon_spiders"):
            self._draw_skill_cooldown_gauge(screen, self.player.summon_spiders_skill, "Summon Spiders", current_screen_width // 2 - (150 * width_scale), current_screen_height - (100 * height_scale), width_scale, height_scale)
        # Draw Summon Skeletons Cooldown Gauge only if player has the skill
        if self.player.has_skill("summon_skeleton"):
            self._draw_skill_cooldown_gauge(screen, self.player.summon_skeletons_skill, "Summon Skeletons", current_screen_width // 2 - (150 * width_scale), current_screen_height - (70 * height_scale), width_scale, height_scale)

        # Draw Minion Counts
        self.quest_tracker_hud.draw(screen) # Call QuestTrackerHUD's draw method
        self._draw_minion_counts(screen, width_scale, height_scale)

        # Display the prompt
        if self.show_prompt:
            time_elapsed = pygame.time.get_ticks() - self.prompt_start_time
            if time_elapsed < 10000:
                text_size = 62
                text = "PRESS P TO OPEN THE PROFIT PASTE SKILL TREE."
                # Draw black border
                draw_text(screen, text, text_size, (0, 0, 0), current_screen_width // 2 - 2, current_screen_height // 2 - 2, align="center")
                draw_text(screen, text, text_size, (0, 0, 0), current_screen_width // 2 - 2, current_screen_height // 2 + 2, align="center")
                draw_text(screen, text, text_size, (0, 0, 0), current_screen_width // 2 + 2, current_screen_height // 2 - 2, align="center")
                draw_text(screen, text, text_size, (0, 0, 0), current_screen_width // 2 + 2, current_screen_height // 2 + 2, align="center")
                # Draw green text
                draw_text(screen, text, text_size, GREEN, current_screen_width // 2, current_screen_height // 2, align="center")
            else:
                self.show_prompt = False

    def _draw_bar(self, screen, x, y, width, height, current_value, max_value, color, label):
        # Background bar
        pygame.draw.rect(screen, UI_BACKGROUND_COLOR, (x, y, width, height))
        # Foreground bar
        if max_value > 0:
            fill_width = (current_value / max_value) * width
            pygame.draw.rect(screen, color, (x, y, fill_width, height))
        # Border
        pygame.draw.rect(screen, UI_PRIMARY_COLOR, (x, y, width, height), 2)
        # Text
        if label == "Profit Paste":
            text = f"{label}"
        else:
            text = f"{label}: {int(current_value)}/{int(max_value)}" # Define text here
        draw_text(screen, text, UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, x + width // 2, y + height // 2, align="center")

    def _draw_skill_bar(self, screen):
        bar_x = SCREEN_WIDTH - 250  # Position on the right
        bar_y = SCREEN_HEIGHT - 100  # Position at the bottom
        slot_size = 50
        spacing = 10

        #draw_text(screen, "Skills:", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, bar_x - 60, bar_y + slot_size // 2, align="midright")

        for i, skill_id in enumerate(self.player.skills):
            slot_rect = pygame.Rect(bar_x + i * (slot_size + spacing), bar_y, slot_size, slot_size)
            pygame.draw.rect(screen, UI_SECONDARY_COLOR, slot_rect)
            pygame.draw.rect(screen, UI_PRIMARY_COLOR, slot_rect, 2)
            # Display key binding for skill slot
            skill_keys = [KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4]
            #key_name = pygame.key.name(skill_keys[i]).upper()
            #draw_text(screen, key_name, UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")
            skill = next((s for s in self.skill_tree_data["skills"] if s["id"] == skill_id), None)
            if skill:
                draw_text(screen, skill["name"], UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")
            else:
                draw_text(screen, "None", UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")

    def _draw_potion_slots(self, screen):
        bar_x = SCREEN_WIDTH // 2 + 100
        bar_y = SCREEN_HEIGHT - 50
        slot_size = 40
        spacing = 10

        draw_text(screen, "Potions:", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, bar_x - 60, bar_y + slot_size // 2, align="midright")

        for i in range(4):
            slot_rect = pygame.Rect(bar_x + i * (slot_size + spacing), bar_y, slot_size, slot_size)
            pygame.draw.rect(screen, UI_SECONDARY_COLOR, slot_rect)
            pygame.draw.rect(screen, UI_PRIMARY_COLOR, slot_rect, 2)
            # Display key binding for potion slot
            potion_keys = [KEY_POTION_1, KEY_POTION_2, KEY_POTION_3, KEY_POTION_4]
            key_name = pygame.key.name(potion_keys[i]).upper()
            draw_text(screen, key_name, UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")

    def _draw_experience_gauge(self, screen, width_scale, height_scale):
        current_screen_width, _ = screen.get_size()
        gauge_x = current_screen_width // 2 - (150 * width_scale) # Centered at the top
        gauge_y = 10 * height_scale
        gauge_width = 300 * width_scale
        gauge_height = 25 * height_scale

        # Background bar
        pygame.draw.rect(screen, UI_BACKGROUND_COLOR, (gauge_x, gauge_y, gauge_width, gauge_height))

        # Calculate XP for next level
        xp_for_next_level = self.player.level * 100
        
        # Foreground bar
        if xp_for_next_level > 0:
            fill_width = (self.player.experience / xp_for_next_level) * gauge_width
            pygame.draw.rect(screen, (0, 200, 255), (gauge_x, gauge_y, fill_width, gauge_height)) # Light blue for XP

        # Border
        pygame.draw.rect(screen, UI_PRIMARY_COLOR, (gauge_x, gauge_y, gauge_width, gauge_height), 2)

        # Text: Level and XP
        xp_remaining = xp_for_next_level - self.player.experience
        text = f"Level: {self.player.level} | XP: {int(self.player.experience)}/{int(xp_for_next_level)} ({int(xp_remaining)} left)"
        draw_text(screen, text, UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, gauge_x + gauge_width // 2, gauge_y + gauge_height // 2, align="center")

    def _draw_skill_cooldown_gauge(self, screen, skill_instance, skill_name, x, y, width_scale, height_scale, width=300, height=25):
        current_time = pygame.time.get_ticks()
        time_since_last_use = current_time - skill_instance.last_used
        
        scaled_width = width * width_scale
        scaled_height = height * height_scale

        # Background bar
        pygame.draw.rect(screen, UI_BACKGROUND_COLOR, (x, y, scaled_width, scaled_height))

        # Foreground bar (cooldown progress)
        if time_since_last_use < skill_instance.cooldown:
            cooldown_progress = time_since_last_use / skill_instance.cooldown
            fill_width = cooldown_progress * scaled_width
            pygame.draw.rect(screen, (255, 165, 0), (x, y, fill_width, scaled_height)) # Orange for cooldown

            # Cooldown text
            remaining_time_ms = skill_instance.cooldown - time_since_last_use
            remaining_time_s = max(0, remaining_time_ms / 1000)
            text = f"{skill_name} Cooldown: {remaining_time_s:.1f}s"
        else:
            text = f"{skill_name} Ready!"
            pygame.draw.rect(screen, GREEN, (x, y, scaled_width, scaled_height)) # Green when ready

        # Border
        pygame.draw.rect(screen, UI_PRIMARY_COLOR, (x, y, scaled_width, scaled_height), 2)

        # Text
        draw_text(screen, text, UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, x + scaled_width // 2, y + scaled_height // 2, align="center")
    def _draw_minion_counts(self, screen, width_scale, height_scale):
        current_screen_width, current_screen_height = screen.get_size()
        minion_count_x = current_screen_width - (10 * width_scale)
        minion_count_y = current_screen_height - (100 * height_scale)
        
        # Get active friendly entities from the current scene
        friendly_entities = self.player.game.current_scene.friendly_entities

        spider_count = 0
        skeleton_count = 0

        for entity in friendly_entities:
            if hasattr(entity, 'owner') and entity.owner == self.player.summon_spiders_skill:
                spider_count += 1
            elif hasattr(entity, 'owner') and entity.owner == self.player.summon_skeletons_skill:
                skeleton_count += 1

        if self.player.has_skill("summon_spiders"):
            draw_text(screen, f"Spiders: {spider_count}", UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, minion_count_x, minion_count_y, align="bottomright")
            minion_count_y -= (20 * height_scale) # Move up for next count

        if self.player.has_skill("summon_skeleton"):
            draw_text(screen, f"Skeletons: {skeleton_count}", UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, minion_count_x, minion_count_y, align="bottomright")

    def _draw_level_up_button(self, screen, width_scale, height_scale):
        current_screen_width, current_screen_height = screen.get_size()
        button_x = current_screen_width // 2 + (160 * width_scale)  # Position to the right of the level bar
        button_y = 10 * height_scale  # Same Y as the level bar
        button_size = int(25 * height_scale)

        # White background
        pygame.draw.rect(screen, (255, 255, 255), (button_x, button_y, button_size, button_size))
        # Green plus sign
        pygame.draw.line(screen, (0, 255, 0), (button_x + button_size // 2, button_y + button_size // 4), (button_x + button_size // 2, button_y + button_size * 3 // 4), 3)
        pygame.draw.line(screen, (0, 255, 0), (button_x + button_size // 4, button_y + button_size // 2), (button_x + button_size * 3 // 4, button_y + button_size // 2), 3)

        self.level_up_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.player.skill_points > 0 and self.level_up_button_rect.collidepoint(event.pos):
                self.player.game.scene_manager.set_scene("level_up_screen", self.player, self)