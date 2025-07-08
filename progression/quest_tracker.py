import json
import os
import pygame
from config.settings import UI_FONT, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, GREEN
import random
from core.utils import draw_text

class QuestTracker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QuestTracker, cls).__new__(cls)
            # Initialize only once
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.all_quests = []
        self.active_quests = [] # This will now typically hold only one quest
        self.completed_quests = []
        self.current_active_quest_index = -1 # -1 means no quest is active yet
        self._load_quests("data/quests.json")
        self._set_initial_active_quest()
        self.quest_completed_display_active = False
        self.quest_completed_display_timer = 0
        self.QUEST_COMPLETED_DISPLAY_DURATION = 3000 # Milliseconds
        self._initialized = True

    def _load_quests(self, filepath):
        try:
            # Get the absolute path to the directory where this script is located
            script_dir = os.path.dirname(__file__)
            # Construct the absolute path to the quests.json file
            absolute_filepath = os.path.join(script_dir, '..', filepath)
            absolute_filepath = os.path.normpath(absolute_filepath)

            with open(absolute_filepath, 'r') as f:
                quests_data = json.load(f)
                for q_data in quests_data['quests']: # Corrected: Access the 'quests' key
                    parsed_objectives = []
                    for obj_data in q_data.get('objectives', []):
                        description = obj_data.get('description', '')
                        
                        obj_type = "unknown"
                        obj_target = ""
                        obj_required = 1
                        obj_count = 0 # Always start at 0 for new quests

                        # Simple parsing logic for common objective types
                        desc_lower = description.lower()
                        if desc_lower.startswith("kill "):
                            parts = description.split(" ", 2)
                            if len(parts) > 2 and parts[1].isdigit():
                                obj_type = "kill"
                                obj_required = int(parts[1])
                                obj_target = parts[2]
                            else:
                                obj_type = "kill"
                                obj_target = description[len("kill "):]
                                obj_required = 1
                        elif desc_lower.startswith("talk to "):
                            obj_type = "talk"
                            obj_target = description[len("talk to "):].strip()
                            obj_required = 1
                        elif desc_lower.startswith("save "):
                            obj_type = "save"
                            obj_target = description[len("save "):]
                            obj_required = 1
                        elif desc_lower.startswith("find "):
                            obj_type = "find"
                            obj_target = description[len("find "):]
                            obj_required = 1
                        elif desc_lower.startswith("disable "):
                            obj_type = "disable"
                            obj_target = description[len("disable "):]
                            obj_required = 1
                        elif desc_lower.startswith("extract "):
                            obj_type = "extract"
                            obj_target = description[len("extract "):]
                            obj_required = 1
                        elif desc_lower.startswith("ambush "):
                            obj_type = "ambush"
                            obj_target = description[len("ambush "):]
                            obj_required = 1
                        elif desc_lower.startswith("burn "):
                            obj_type = "burn"
                            obj_target = description[len("burn "):]
                            obj_required = 1
                        elif desc_lower.startswith("infiltrate "):
                            obj_type = "infiltrate"
                            obj_target = description[len("infiltrate "):]
                            obj_required = 1
                        elif desc_lower.startswith("bypass "):
                            obj_type = "bypass"
                            obj_target = description[len("bypass "):]
                            obj_required = 1
                        elif desc_lower.startswith("retrieve "):
                            obj_type = "retrieve"
                            obj_target = description[len("retrieve "):]
                            obj_required = 1
                        elif desc_lower.startswith("navigate "):
                            obj_type = "navigate"
                            obj_target = description[len("navigate "):]
                            obj_required = 1
                        elif desc_lower.startswith("defend "):
                            obj_type = "defend"
                            obj_target = description[len("defend "):]
                            obj_required = 1
                        elif desc_lower.startswith("escape "):
                            obj_type = "escape"
                            obj_target = description[len("escape "):]
                            obj_required = 1
                        elif desc_lower.startswith("disguise "):
                            obj_type = "disguise"
                            obj_target = description[len("disguise "):]
                            obj_required = 1
                        elif desc_lower.startswith("plant "):
                            obj_type = "plant"
                            obj_target = description[len("plant "):]
                            obj_required = 1
                        elif desc_lower.startswith("descend into "):
                            obj_type = "descend"
                            obj_target = description[len("descend into "):]
                            obj_required = 1
                        elif desc_lower.startswith("destroy "):
                            parts = description.split(" ", 2)
                            if len(parts) > 2 and parts[1].isdigit():
                                obj_type = "destroy"
                                obj_required = int(parts[1])
                                obj_target = parts[2]
                            else:
                                obj_type = "destroy"
                                obj_target = description[len("destroy "):]
                                obj_required = 1
                        elif desc_lower.startswith("locate "):
                            obj_type = "locate"
                            obj_target = description[len("locate "):]
                            obj_required = 1
                        elif desc_lower.startswith("override "):
                            obj_type = "override"
                            obj_target = description[len("override "):]
                            obj_required = 1
                        elif desc_lower.startswith("survive "):
                            parts = description.split(" ", 2)
                            if len(parts) > 2 and parts[1].isdigit():
                                obj_type = "survive"
                                obj_required = int(parts[1])
                                obj_target = parts[2]
                            else:
                                obj_type = "survive"
                                obj_target = description[len("survive "):]
                                obj_required = 1
                        elif desc_lower.startswith("free "):
                            parts = description.split(" ", 2)
                            if len(parts) > 2 and parts[1].isdigit():
                                obj_type = "free"
                                obj_required = int(parts[1])
                                obj_target = parts[2]
                            else:
                                obj_type = "free"
                                obj_target = description[len("free "):]
                                obj_required = 1
                        elif desc_lower.startswith("convince "):
                            obj_type = "convince"
                            obj_target = description[len("convince "):]
                            obj_required = 1
                        elif desc_lower.startswith("sabotage "):
                            obj_type = "sabotage"
                            obj_target = description[len("sabotage "):]
                            obj_required = 1
                        elif desc_lower.startswith("hold the line "):
                            obj_type = "hold"
                            obj_target = description[len("hold the line "):]
                            obj_required = 1
                        elif desc_lower.startswith("talk to "):
                            obj_type = "talk"
                            obj_target = description[len("talk to "):]
                            obj_required = 1
                        elif desc_lower.startswith("breach "):
                            obj_type = "breach"
                            obj_target = description[len("breach "):]
                            obj_required = 1
                        elif desc_lower.startswith("download "):
                            obj_type = "download"
                            obj_target = description[len("download "):]
                            obj_required = 1
                        elif desc_lower.startswith("ascend "):
                            obj_type = "ascend"
                            obj_target = description[len("ascend "):]
                            obj_required = 1
                        elif desc_lower.startswith("collapse "):
                            obj_type = "collapse"
                            obj_target = description[len("collapse "):]
                            obj_required = 1
                        elif desc_lower.startswith("protect "):
                            obj_type = "protect"
                            obj_target = description[len("protect "):]
                            obj_required = 1
                        elif desc_lower.startswith("retreat "):
                            obj_type = "retreat"
                            obj_target = description[len("retreat "):]
                            obj_required = 1
                        elif desc_lower.startswith("interrupt "):
                            obj_type = "interrupt"
                            obj_target = description[len("interrupt "):]
                            obj_required = 1
                        elif desc_lower.startswith("save at least "):
                            parts = description.split(" ", 3)
                            if len(parts) > 3 and parts[3].isdigit():
                                obj_type = "save"
                                obj_required = int(parts[3])
                                obj_target = parts[4] if len(parts) > 4 else ""
                            else:
                                obj_type = "save"
                                obj_target = description[len("save at least "):]
                                obj_required = 1
                        elif desc_lower.startswith("escort "):
                            obj_type = "escort"
                            obj_target = description[len("escort "):]
                            obj_required = 1
                        elif desc_lower.startswith("stabilize "):
                            obj_type = "stabilize"
                            obj_target = description[len("stabilize "):]
                            obj_required = 1
                        elif desc_lower.startswith("keep the signal alive "):
                            obj_type = "keep_alive"
                            obj_target = description[len("keep the signal alive "):]
                            obj_required = 1
                        elif desc_lower.startswith("activate "):
                            obj_type = "activate"
                            obj_target = description[len("activate "):]
                            obj_required = 1
                        elif desc_lower.startswith("face "):
                            obj_type = "face"
                            obj_target = description[len("face "):]
                            obj_required = 1
                        elif desc_lower.startswith("survive for "):
                            parts = description.split(" ", 3)
                            if len(parts) > 3 and parts[2].isdigit():
                                obj_type = "survive_time"
                                obj_required = int(parts[2])
                                obj_target = parts[3] if len(parts) > 3 else ""
                            else:
                                obj_type = "survive_time"
                                obj_target = description[len("survive for "):]
                                obj_required = 1
                        
                        parsed_objectives.append({
                            "type": obj_type,
                            "target": obj_target.strip(),
                            "count": obj_count,
                            "required": obj_required,
                            "description_original": description, # Keep original description for display if needed
                            "completed_original": obj_data.get('completed', False) # Keep original completed status
                        })
                    
                    quest = Quest(q_data['id'], q_data['name'], q_data['description'], parsed_objectives, q_data.get('tilemap_scene_name'))
                    quest.is_completed = q_data.get('is_completed', False)
                    quest.is_unlocked = q_data.get('is_unlocked', False) # Assuming quests can be locked/unlocked
                    self.all_quests.append(quest)
                    print(f"Loaded quest: '{quest.name}', is_completed: {quest.is_completed}, is_unlocked: {quest.is_unlocked}") # Debug print
            print(f"Finished loading {len(self.all_quests)} quests from {filepath}")
        except FileNotFoundError:
            print(f"Error: Quest file not found at {filepath}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {filepath}")
        except Exception as e:
            print(f"An unexpected error occurred while loading quests: {e}")

    def _set_initial_active_quest(self):
        print("Attempting to set initial active quest...") # Debug print
        for i, quest in enumerate(self.all_quests):
            print(f"Checking quest '{quest.name}': is_completed={quest.is_completed}, is_unlocked={quest.is_unlocked}") # Debug print
            if not quest.is_completed and quest.is_unlocked:
                self.current_active_quest_index = i
                self.active_quests = [quest]
                print(f"Initial active quest set to: '{quest.name}'")
                return
        print("No initial active quest found (all completed or locked).")

    def add_quest(self, quest):
        # This method might be less relevant if quests are loaded sequentially
        # but can be used for dynamic quest additions if needed.
        if quest not in self.active_quests and quest not in self.completed_quests:
            # For now, we'll only allow adding if it's the next in sequence or a special quest
            # This logic needs refinement based on how quests are truly added beyond initial load
            print(f"Quest '{quest.name}' added to tracker (consider if this is the intended flow).")
            # If we want to add it as the *new* active quest, we'd need to update index and active_quests
            # For now, we'll stick to the sequential advancement.

    def complete_quest(self, quest):
        if quest in self.active_quests:
            self.active_quests.remove(quest)
            self.quest_completed_display_active = True
            self.quest_completed_display_timer = pygame.time.get_ticks()
            self.completed_quests.append(quest)
            quest.is_completed = True # Ensure the quest object itself is marked completed
            print(f"Quest '{quest.name}' completed!")
            self._advance_active_quest()
        else:
            print(f"Quest '{quest.name}' not found in active quests.")

    def _advance_active_quest(self):
        self.active_quests = [] # Clear current active quest
        
        # First, try to unlock the next quest in the sequence
        next_potential_quest_index = self.current_active_quest_index + 1
        if next_potential_quest_index < len(self.all_quests):
            self.all_quests[next_potential_quest_index].is_unlocked = True
            print(f"Quest '{self.all_quests[next_potential_quest_index].name}' unlocked.")

        # Then, find the next active quest (which might be the one just unlocked)
        self.current_active_quest_index += 1
        while self.current_active_quest_index < len(self.all_quests):
            next_quest = self.all_quests[self.current_active_quest_index]
            if not next_quest.is_completed and next_quest.is_unlocked:
                self.active_quests = [next_quest]
                print(f"Active quest advanced to: '{next_quest.name}'")
                return
            self.current_active_quest_index += 1
        print("No more uncompleted and unlocked quests to activate.")

    def update_quest_progress(self, objective_type, target, amount=1):
        print(f"Attempting to update quest progress: type='{objective_type}', target='{target}', amount={amount}") # Debug print
        if self.active_quests:
            current_quest = self.active_quests[0]
            print(f"Current active quest: '{current_quest.name}'") # Debug print
            if current_quest.update_objective(objective_type, target, amount):
                if current_quest.is_completed:
                    self.complete_quest(current_quest)
        else:
            print("No active quest to update progress for.")

    def get_active_quests(self):
        # Now returns a list containing at most one active quest
        return self.active_quests

    def get_quest_status(self, quest_name):
        if self.active_quests and self.active_quests[0].name == quest_name:
            return f"Active: {self.active_quests[0].get_progress_status()}"
        for quest in self.completed_quests:
            if quest.name == quest_name:
                return "Completed"
        return "Quest not found."
    def is_quest_completed(self, quest_id):
        """Checks if a specific quest is completed."""
        for quest in self.all_quests:
            if quest.id == quest_id:
                return quest.is_completed
        return False # Return False if quest_id is not found

    def _parse_objective_data(self, obj_data):
        description = obj_data.get('description_original', obj_data.get('description', ''))
        
        obj_type = "unknown"
        obj_target = ""
        obj_required = 1
        obj_count = obj_data.get('count', 0) # Load count from save data
        
        desc_lower = description.lower()
        if desc_lower.startswith("talk to "):
            obj_type = "talk"
            obj_target = description[len("talk to "):].strip()
            obj_required = 1
        elif desc_lower.startswith("kill "):
            parts = description.split(" ", 2)
            if len(parts) > 2 and parts[1].isdigit():
                obj_type = "kill"
                obj_required = int(parts[1])
                obj_target = parts[2]
            else:
                obj_type = "kill"
                obj_target = description[len("kill "):]
                obj_required = 1
        elif desc_lower.startswith("save "):
            obj_type = "save"
            obj_target = description[len("save "):]
            obj_required = 1
        elif desc_lower.startswith("find "):
            obj_type = "find"
            obj_target = description[len("find "):]
            obj_required = 1
        elif desc_lower.startswith("disable "):
            obj_type = "disable"
            obj_target = description[len("disable "):]
            obj_required = 1
        elif desc_lower.startswith("extract "):
            obj_type = "extract"
            obj_target = description[len("extract "):]
            obj_required = 1
        elif desc_lower.startswith("ambush "):
            obj_type = "ambush"
            obj_target = description[len("ambush "):]
            obj_required = 1
        elif desc_lower.startswith("burn "):
            obj_type = "burn"
            obj_target = description[len("burn "):]
            obj_required = 1
        elif desc_lower.startswith("infiltrate "):
            obj_type = "infiltrate"
            obj_target = description[len("infiltrate "):]
            obj_required = 1
        elif desc_lower.startswith("bypass "):
            obj_type = "bypass"
            obj_target = description[len("bypass "):]
            obj_required = 1
        elif desc_lower.startswith("retrieve "):
            obj_type = "retrieve"
            obj_target = description[len("retrieve "):]
            obj_required = 1
        elif desc_lower.startswith("navigate "):
            obj_type = "navigate"
            obj_target = description[len("navigate "):]
            obj_required = 1
        elif desc_lower.startswith("defend "):
            obj_type = "defend"
            obj_target = description[len("defend "):]
            obj_required = 1
        elif desc_lower.startswith("escape "):
            obj_type = "escape"
            obj_target = description[len("escape "):]
            obj_required = 1
        elif desc_lower.startswith("disguise "):
            obj_type = "disguise"
            obj_target = description[len("disguise "):]
            obj_required = 1
        elif desc_lower.startswith("plant "):
            obj_type = "plant"
            obj_target = description[len("plant "):]
            obj_required = 1
        elif desc_lower.startswith("descend into "):
            obj_type = "descend"
            obj_target = description[len("descend into "):]
            obj_required = 1
        elif desc_lower.startswith("destroy "):
            parts = description.split(" ", 2)
            if len(parts) > 2 and parts[1].isdigit():
                obj_type = "destroy"
                obj_required = int(parts[1])
                obj_target = parts[2]
            else:
                obj_type = "destroy"
                obj_target = description[len("destroy "):]
                obj_required = 1
        elif desc_lower.startswith("locate "):
            obj_type = "locate"
            obj_target = description[len("locate "):]
            obj_required = 1
        elif desc_lower.startswith("override "):
            obj_type = "override"
            obj_target = description[len("override "):]
            obj_required = 1
        elif desc_lower.startswith("survive "):
            parts = description.split(" ", 2)
            if len(parts) > 2 and parts[1].isdigit():
                obj_type = "survive"
                obj_required = int(parts[1])
                obj_target = parts[2]
            else:
                obj_type = "survive"
                obj_target = description[len("survive "):]
                obj_required = 1
        elif desc_lower.startswith("free "):
            parts = description.split(" ", 2)
            if len(parts) > 2 and parts[1].isdigit():
                obj_type = "free"
                obj_required = int(parts[1])
                obj_target = parts[2]
            else:
                obj_type = "free"
                obj_target = description[len("free "):]
                obj_required = 1
        elif desc_lower.startswith("convince "):
            obj_type = "convince"
            obj_target = description[len("convince "):]
            obj_required = 1
        elif desc_lower.startswith("sabotage "):
            obj_type = "sabotage"
            obj_target = description[len("sabotage "):]
            obj_required = 1
        elif desc_lower.startswith("hold the line "):
            obj_type = "hold"
            obj_target = description[len("hold the line "):]
            obj_required = 1
        elif desc_lower.startswith("breach "):
            obj_type = "breach"
            obj_target = description[len("breach "):]
            obj_required = 1
        elif desc_lower.startswith("download "):
            obj_type = "download"
            obj_target = description[len("download "):]
            obj_required = 1
        elif desc_lower.startswith("ascend "):
            obj_type = "ascend"
            obj_target = description[len("ascend "):]
            obj_required = 1
        elif desc_lower.startswith("collapse "):
            obj_type = "collapse"
            obj_target = description[len("collapse "):]
            obj_required = 1
        elif desc_lower.startswith("protect "):
            obj_type = "protect"
            obj_target = description[len("protect "):]
            obj_required = 1
        elif desc_lower.startswith("retreat "):
            obj_type = "retreat"
            obj_target = description[len("retreat "):]
            obj_required = 1
        elif desc_lower.startswith("interrupt "):
            obj_type = "interrupt"
            obj_target = description[len("interrupt "):]
            obj_required = 1
        elif desc_lower.startswith("save at least "):
            parts = description.split(" ", 3)
            if len(parts) > 3 and parts[3].isdigit():
                obj_type = "save"
                obj_required = int(parts[3])
                obj_target = parts[4] if len(parts) > 4 else ""
            else:
                obj_type = "save"
                obj_target = description[len("save at least "):]
                obj_required = 1
        elif desc_lower.startswith("escort "):
            obj_type = "escort"
            obj_target = description[len("escort "):]
            obj_required = 1
        elif desc_lower.startswith("stabilize "):
            obj_type = "stabilize"
            obj_target = description[len("stabilize "):]
            obj_required = 1
        elif desc_lower.startswith("keep the signal alive "):
            obj_type = "keep_alive"
            obj_target = description[len("keep the signal alive "):]
            obj_required = 1
        elif desc_lower.startswith("activate "):
            obj_type = "activate"
            obj_target = description[len("activate "):]
            obj_required = 1
        elif desc_lower.startswith("face "):
            obj_type = "face"
            obj_target = description[len("face "):]
            obj_required = 1
        elif desc_lower.startswith("survive for "):
            parts = description.split(" ", 3)
            if len(parts) > 3 and parts[2].isdigit():
                obj_type = "survive_time"
                obj_required = int(parts[2])
                obj_target = parts[3] if len(parts) > 3 else ""
            else:
                obj_type = "survive_time"
                obj_target = description[len("survive for "):]
                obj_required = 1
        
        return {
            "type": obj_type,
            "target": obj_target.strip(),
            "count": obj_count,
            "required": obj_required,
            "description_original": description,
            "completed_original": obj_data.get('completed_original', False) # Use completed_original from save data
        }

    def get_quest_by_name(self, quest_name):
        for quest in self.all_quests:
            if quest.name == quest_name:
                return quest
        return None
class Quest:
    def __init__(self, id, name, description, objectives, tilemap_scene_name=None):
        self.id = id
        self.name = name
        self.description = description
        self.objectives = objectives  # A list of dictionaries, e.g., [{"type": "kill", "target": "Goblin", "count": 0, "required": 5}]
        self.tilemap_scene_name = tilemap_scene_name
        self.is_completed = False
        self.is_unlocked = False # New attribute for quest unlocking

    def _get_plural_form(self, word):
        """Attempts to convert a word to its plural form for common English singulars."""
        word_lower = word.lower()
        if word_lower.endswith("y") and len(word_lower) > 1 and word_lower[-2] not in 'aeiou': # e.g., "dummy" -> "dummies"
            return word[:-1] + "ies"
        elif word_lower.endswith("s") or word_lower.endswith("x") or \
             word_lower.endswith("z") or word_lower.endswith("ch") or \
             word_lower.endswith("sh"): # e.g., "box" -> "boxes", "church" -> "churches"
            return word + "es"
        else: # Most common case: just add 's'
            return word + "s"

    def update_objective(self, objective_type, target, amount=1):
        updated = False
        print(f"  Quest '{self.name}' - Checking objectives for type='{objective_type}', target='{target}'") # Debug print
        for obj in self.objectives:
            print(f"    Comparing with obj: type='{obj['type']}', target='{obj.get('target')}'") # Debug print
            obj_target_lower = obj.get("target", "").strip().lower()
            target_lower = target.strip().lower().replace('_', ' ') # Normalize incoming target by replacing underscores with spaces
            print(f"    obj_target_lower: '{obj_target_lower}', target_lower: '{target_lower}'")
            
            # Check for direct match, or if objective target is plural of incoming target
            if obj["type"].lower() == objective_type.lower() and \
               (obj_target_lower == target_lower or \
                obj_target_lower == self._get_plural_form(target_lower)):
                obj["count"] = min(obj["count"] + amount, obj["required"])
                print(f"Objective '{objective_type} {target}' progress: {obj['count']}/{obj['required']} for quest '{self.name}'.")
                updated = True
                break # Assuming one objective per type/target combination for simplicity
        if updated:
            self.check_completion()
        return updated

    def check_completion(self):
        all_objectives_met = all(obj["count"] >= obj["required"] for obj in self.objectives)
        if all_objectives_met and not self.is_completed:
            self.is_completed = True
            print(f"Quest '{self.name}' is now completed!")
            return True
        return False

    def get_progress_status(self):
        status = []
        for obj in self.objectives:
            # Use original description if available, otherwise construct from type/target
            if 'description_original' in obj and obj['description_original']:
                status.append(f"{obj['description_original']}: {obj['count']}/{obj['required']}")
            else:
                status.append(f"{obj['type'].capitalize()} {obj.get('target', '')}: {obj['count']}/{obj['required']}")
        return ", ".join(status)

    def is_objective_completed(self, objective_description):
        for obj in self.objectives:
            if obj['description_original'].lower() == objective_description.lower():
                return obj['count'] >= obj['required']
        return False

class QuestTrackerHUD:
    def __init__(self, quest_tracker):
        self.quest_tracker = quest_tracker

    def draw(self, screen):
        tracker_x = 10
        tracker_y = 10
        line_height = UI_FONT_SIZE_DEFAULT + 2

        draw_text(screen, "Active Quest:", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, tracker_x, tracker_y, align="topleft")
        current_y = tracker_y + line_height

        active_quests = self.quest_tracker.get_active_quests()
        if not active_quests:
            draw_text(screen, "No active quest.", UI_FONT_SIZE_DEFAULT - 4, UI_SECONDARY_COLOR, tracker_x, current_y, align="topleft")
            current_y += line_height
        else:
            quest = active_quests[0] # Display only the first (and only) active quest
            draw_text(screen, f"- {quest.name}", UI_FONT_SIZE_DEFAULT - 2, UI_PRIMARY_COLOR, tracker_x + 10, current_y, align="topleft")
            current_y += line_height
            for obj in quest.objectives:
                # Use original description if available, otherwise construct from type/target
                if 'description_original' in obj and obj['description_original']:
                    obj_text = f"  - {obj['description_original']}: {obj['count']}/{obj['required']}"
                else:
                    obj_text = f"  - {obj['type'].capitalize()} {obj.get('target', '')}: {obj['count']}/{obj['required']}"
                obj_color = GREEN if obj['count'] >= obj['required'] else UI_SECONDARY_COLOR
                draw_text(screen, obj_text, UI_FONT_SIZE_DEFAULT - 4, obj_color, tracker_x + 20, current_y, align="topleft")
                current_y += line_height
        
        # Handle "QUEST COMPLETED" display
        if self.quest_tracker.quest_completed_display_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.quest_tracker.quest_completed_display_timer < self.quest_tracker.QUEST_COMPLETED_DISPLAY_DURATION:
                # Calculate alpha for fade-out effect
                time_left = self.quest_tracker.QUEST_COMPLETED_DISPLAY_DURATION - (current_time - self.quest_tracker.quest_completed_display_timer)
                alpha = int(255 * (time_left / self.quest_tracker.QUEST_COMPLETED_DISPLAY_DURATION))
                alpha = max(0, min(255, alpha)) # Ensure alpha is within 0-255

                # "Hacker text" effect - animate characters
                display_text = "QUEST COMPLETED"
                animated_text = ""
                for i, char in enumerate(display_text):
                    if pygame.time.get_ticks() % 200 > 100: # Simple blink effect
                        animated_text += char
                    else:
                        animated_text += chr(random.randint(33, 126)) # Random ASCII char

                    font_size = UI_FONT_SIZE_DEFAULT * 3 # Very large text
                    center_x = screen.get_width() // 2
                    center_y = screen.get_height() // 2

                    # Stable red text
                    draw_text(screen, "QUEST COMPLETED", font_size, (255, 0, 0), center_x, center_y, alpha=int(alpha * 0.6))

                    # "Hacker text" effect - animate characters
                    display_text = "QUEST COMPLETED"
                    animated_text = ""
                    for i, char in enumerate(display_text):
                        if pygame.time.get_ticks() % 200 > 100: # Simple blink effect
                            animated_text += char
                        else:
                            animated_text += chr(random.randint(33, 126)) # Random ASCII char

                    # Animated green text
                    draw_text(screen, animated_text, font_size, (0, 255, 0), center_x, center_y, alpha=alpha)




            else:
                self.quest_tracker.quest_completed_display_active = False
