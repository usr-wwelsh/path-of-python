import pygame
import json
import os
from core.scene_manager import BaseScene
from config.settings import UI_FONT, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_BACKGROUND_COLOR
from ui.menus import Button
from progression.quest_tracker import QuestTracker
from progression.paste_tree_manager import PasteTreeManager

class SaveMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.text_color = UI_PRIMARY_COLOR
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT)

        # Initialize buttons without fixed positions, positions will be set in reposition_elements
        self.back_button = Button(0, 0, 200, 50, "Back", self.go_back)
        self.save_button = Button(0, 0, 200, 50, "Save Game", self.save_game)
        self.load_button = Button(0, 0, 200, 50, "Load Game", self.load_game)

        self.save_files = self.load_save_files()
        self.selected_save = None
        self.previous_scene_name = None

        # Store save file rects for collision detection
        self.save_file_rects = []
        self.title_rect = None # To store the rect for the "Save Menu" title

        # Initial positioning
        self.reposition_elements()

    def enter(self):
        self.game.logger.info("Entering Save Menu.")
        self.previous_scene_name = self.game.scene_manager.current_scene_name
        self.reposition_elements() # Recalculate positions on entry

    def exit(self):
        self.game.logger.info("Exiting Save Menu.")

    def reposition_elements(self):
        current_screen_width, current_screen_height = pygame.display.get_surface().get_size()

        # Calculate dynamic widths for centering
        max_save_file_width = 0
        if self.save_files:
            for save_file in self.save_files:
                temp_surface = self.font.render(save_file, True, self.text_color)
                max_save_file_width = max(max_save_file_width, temp_surface.get_width())
        else:
            max_save_file_width = 200 # Default width if no save files

        # Determine the widest element for horizontal centering
        menu_center_x = current_screen_width // 2

        # Calculate vertical positions for the main content block
        save_list_height = len(self.save_files) * 30

        # Define vertical spacing
        spacing_title_to_list = 30
        spacing_list_to_save_btn = 30
        spacing_save_to_load_btn = 50

        # Calculate total height of the main interactive block (save list + save/load buttons)
        main_block_height = save_list_height + spacing_list_to_save_btn + self.save_button.rect.height + \
                            spacing_save_to_load_btn + self.load_button.rect.height

        # Calculate the top-left y for the main block to be vertically centered
        # This will be the starting point for the save list
        main_block_start_y = (current_screen_height - main_block_height) // 2

        # Position "Save Menu" title
        # Center the title above the main block
        title_y = main_block_start_y - spacing_title_to_list - UI_FONT_SIZE_DEFAULT
        self.title_rect = self.font.render("Save Menu", True, self.text_color).get_rect(center=(menu_center_x, title_y + UI_FONT_SIZE_DEFAULT // 2))

        current_y = main_block_start_y

        # Position save list items and store their rects
        self.save_file_rects = []
        save_list_x = (current_screen_width - max_save_file_width) // 2 # Center the list itself
        for i, save_file in enumerate(self.save_files):
            save_rect = pygame.Rect(save_list_x, current_y + i * 30, max_save_file_width, 30)
            self.save_file_rects.append(save_rect)

        current_y += save_list_height + spacing_list_to_save_btn

        # Position Save Game button
        self.save_button.rect.topleft = (menu_center_x - self.save_button.rect.width // 2, current_y)
        current_y += self.save_button.rect.height + spacing_save_to_load_btn

        # Position Load Game button
        self.load_button.rect.topleft = (menu_center_x - self.load_button.rect.width // 2, current_y)
        # The current_y is now at the bottom of the load button, but we don't need it for the back button if it's anchored to the bottom.

        # Position Back button
        # Keep it near the bottom, but also horizontally centered
        self.back_button.rect.topleft = (menu_center_x - self.back_button.rect.width // 2, current_screen_height - 100)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.reposition_elements() # Recalculate positions on window resize
        self.back_button.handle_event(event)
        self.save_button.handle_event(event)
        self.load_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, save_rect in enumerate(self.save_file_rects): # Use stored rects for collision
                if save_rect.collidepoint(mouse_pos):
                    self.selected_save = self.save_files[i]
                    print(f"Selected save: {self.selected_save}") # Debugging

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(UI_BACKGROUND_COLOR)

        # Draw "Save Menu" title
        text_surface = self.font.render("Save Menu", True, self.text_color)
        screen.blit(text_surface, self.title_rect)

        self.back_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)

        # Draw save list
        for i, save_file in enumerate(self.save_files):
            text_color = (0, 255, 0) if save_file == self.selected_save else self.text_color
            save_surface = self.font.render(save_file, True, text_color)
            # Use the stored rect for drawing
            screen.blit(save_surface, self.save_file_rects[i])

    def save_game(self):
        player = self.game.player
        save_data = {
            "class": player.class_name,
            "stats": player.stats,
            "skills": player.skills,
            "level": player.level,
            "x": player.rect.x,
            "y": player.rect.y,
            # Add paste tree data
            "paste_tree": {
                "acquired_paste_nodes": player.acquired_paste_nodes,
                "paste": player.paste
            }
        }

        # Save quest tracker data
        quest_tracker = QuestTracker()
        save_data["quest_tracker"] = {
            "active_quests": [
                {
                    "name": quest.name,
                    "description": quest.description,
                    "objectives": quest.objectives,
                    "tilemap_scene_name": quest.tilemap_scene_name,
                    "is_completed": quest.is_completed,
                    "is_unlocked": quest.is_unlocked
                }
                for quest in quest_tracker.active_quests
            ],
            "completed_quests": [
                {
                    "name": quest.name,
                    "description": quest.description,
                    "objectives": quest.objectives,
                    "tilemap_scene_name": quest.tilemap_scene_name,
                    "is_completed": quest.is_completed,
                    "is_unlocked": quest.is_unlocked
                }
                for quest in quest_tracker.completed_quests
            ],
            "current_active_quest_index": quest_tracker.current_active_quest_index
        }

        # Determine the next available save slot
        save_number = 1
        while os.path.exists(os.path.join("saves", f"save_{save_number}.json")):
            save_number += 1

        filename = f"save_{save_number}.json"
        filepath = os.path.join("saves", filename)
        with open(filepath, "w") as f:
            json.dump(self._convert_save_data(save_data), f)
        self.game.logger.info(f"Game saved to {filepath}")

    def _convert_save_data(self, data):
        if isinstance(data, set):
            return list(data)
        elif isinstance(data, dict):
            return {key: self._convert_save_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_save_data(item) for item in data]
        else:
            return data

    def load_game(self):
        if self.selected_save:
            filepath = os.path.join("saves", self.selected_save)
            with open(filepath, "r") as f:
                save_data = json.load(f)

            player = self.game.player
            class_name = save_data["class"]
            class_data = self.game.scene_manager.scenes["character_selection"].classes[class_name] # Access class data from character selection scene
            player.set_class(class_name, class_data.get("stats", {}))

            player.apply_stats(save_data["stats"])
            player.skills = save_data["skills"]
            player.level = save_data["level"]
            player.paste = save_data.get("paste_tree", {}).get("paste", 0)
            player.rect.x = save_data["x"]
            player.rect.y = save_data["y"]

            # Load paste tree data
            if "paste_tree" in save_data:
                player.acquired_paste_nodes = save_data.get("paste_tree", {}).get("acquired_paste_nodes", [])

            # Ensure current life, mana, energy shield are capped at max
            player.current_life = min(player.current_life, player.max_life)
            player.current_mana = min(player.current_mana, player.max_mana)
            player.current_energy_shield = min(player.current_energy_shield, player.max_energy_shield)

            # Load quest tracker data
            quest_tracker = QuestTracker()
            if "quest_tracker" not in save_data:
                # Initialize a fresh quest tracker if no data is found
                quest_tracker._set_initial_active_quest()
            else:
                quest_data = save_data.get("quest_tracker", {})
                active_quests_data = quest_data.get("active_quests", [])
                completed_quests_data = quest_data.get("completed_quests", [])
                current_active_quest_index = quest_data.get("current_active_quest_index", -1)

                # Clear existing quests
                quest_tracker.active_quests = []
                quest_tracker.completed_quests = []
                quest_tracker.current_active_quest_index = current_active_quest_index

                # Load active quests
                for quest_data in active_quests_data:
                    quest = QuestTracker().all_quests[QuestTracker().current_active_quest_index]
                    quest.name = quest_data["name"]
                    quest.description = quest_data["description"]
                    quest.objectives = quest_data["objectives"]
                    quest.tilemap_scene_name = quest_data["tilemap_scene_name"]
                    quest.is_completed = quest_data["is_completed"]
                    quest.is_unlocked = quest_data["is_unlocked"]
                    quest_tracker.active_quests.append(quest)

                # Load completed quests
                for quest_data in completed_quests_data:
                    for quest in quest_tracker.all_quests:
                        if quest.name == quest_data["name"]:
                            quest.name = quest_data["name"]
                            quest.description = quest_data["description"]
                            quest.objectives = quest_data["objectives"]
                            quest.tilemap_scene_name = quest_data["tilemap_scene_name"]
                            quest.is_completed = quest_data["is_completed"]
                            quest.is_unlocked = quest_data["is_unlocked"]
                            quest_tracker.completed_quests.append(quest)

            self.game.scene_manager.set_scene("spawn_town")
            self.game.logger.info(f"Game loaded from {filepath}")
        else:
            print("No save selected")

    def load_save_files(self):
        save_files = []
        for filename in os.listdir("saves"):
            if filename.startswith("save_") and filename.endswith(".json"):
                save_files.append(filename)
        return save_files

    def go_back(self):
        self.game.scene_manager.set_scene(self.previous_scene_name)