import json
import os
import pygame
import random
from config.constants import TILE_SIZE

class PasteTreeManager:
    _instance = None

    def __new__(cls, game=None):
        if cls._instance is None:
            cls._instance = super(PasteTreeManager, cls).__new__(cls)
            cls._instance.game = game
            cls._instance.paste_tree_data = {}
            if game: # Only load data if game is provided (i.e., not during initial singleton creation without game context)
                cls._instance._load_paste_tree_data()
        return cls._instance

    def _load_paste_tree_data(self):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, '..', 'data', 'paste_trees.json')
        try:
            with open(file_path, 'r') as f:
                self.paste_tree_data = json.load(f)
            print(f"Loaded paste tree data from {file_path}")
        except FileNotFoundError:
            print(f"Error: paste_trees.json not found at {file_path}")
            self.paste_tree_data = {}
        except json.JSONDecodeError:
            print(f"Error decoding paste_trees.json at {file_path}")
            self.paste_tree_data = {}

    def load_player_paste_tree_data(self, player, save_data):
        if "paste_tree" in save_data:
            paste_tree_data = save_data["paste_tree"]
            if "acquired_paste_nodes" in paste_tree_data:
                for node_id in paste_tree_data["acquired_paste_nodes"]:
                    if node_id not in player.acquired_paste_nodes:
                        player.acquired_paste_nodes.append(node_id)
                        node_data = self.get_node_data(node_id)
                        if node_data:
                            self._apply_node_effect(player, node_data)
            if "paste" in paste_tree_data:
                player.paste = paste_tree_data["paste"]
            print(f"Loaded player paste tree data: {paste_tree_data}")

    def get_node_data(self, node_id):
        for tree_name in self.paste_tree_data:
            for node in self.paste_tree_data[tree_name]["nodes"]:
                if node["id"] == node_id:
                    return node
        return None

    def acquire_node(self, player, node_id):
        node_data = self.get_node_data(node_id)
        if node_data and node_id not in player.acquired_paste_nodes:
            player.acquired_paste_nodes.append(node_id)
            print(f"Player acquired node: {node_id}")
            self._apply_node_effect(player, node_data)
            return True
        return False

    def _apply_node_effect(self, player, node_data):
        effect_type = node_data.get("effect_type")
        effect_data = node_data.get("effect_data", {})

        if effect_type == "STAT_MODIFIER":
            self._apply_stat_modifier(player, effect_data)
        elif effect_type == "PASSIVE_ABILITY":
            self._apply_passive_ability(player, effect_data)
        elif effect_type == "SKILL_GRANT":
            self._grant_skill(player, effect_data)
        else:
            print(f"Unknown effect type: {effect_type} for node {node_data.get('id')}")

    def _apply_stat_modifier(self, player, effect_data):
        stat = effect_data.get("stat")
        value = effect_data.get("value")
        operation = effect_data.get("operation")

        if not all([stat, value, operation]):
            print(f"Invalid STAT_MODIFIER data: {effect_data}")
            return

        # Store modifiers temporarily for now, actual application will happen in Player.apply_stats
        if not hasattr(player, '_temp_paste_tree_modifiers'):
            player._temp_paste_tree_modifiers = {}

        if stat not in player._temp_paste_tree_modifiers:
            player._temp_paste_tree_modifiers[stat] = []

        player._temp_paste_tree_modifiers[stat].append({"value": value, "operation": operation})
        print(f"Applied stat modifier: {stat} {operation} {value}")

        # Trigger player stat recalculation
        player.apply_stats()

    def _apply_passive_ability(self, player, effect_data):
        ability_id = effect_data.get("ability_id")
        if not ability_id:
            print(f"Passive ability missing ID: {effect_data}")
            return

        print(f"Applying passive ability: {ability_id} with data {effect_data}")
        # This is where the logic for passive abilities will be integrated.
        # For now, we'll just store them or trigger a flag.
        # More complex passive abilities might require direct modification of player/skill behavior
        # or a dedicated system to manage active passive effects.
        if not hasattr(player, 'active_passive_abilities'):
            player.active_passive_abilities = {}
        player.active_passive_abilities[ability_id] = effect_data
        # Initialize passive ability states if not already present
        # Ensure the state exists, then update its values
        player.void_embrace_state = {
            "active": False,
            "cooldown_start_time": 0,
            "last_regen_tick": 0,
            "cooldown_duration": effect_data.get("cooldown", 0) * 1000, # Convert to ms
            "duration": effect_data.get("duration", 0) * 1000, # Convert to ms
            "regen_percentage": effect_data.get("regen_percentage", 0),
            "hp_threshold": effect_data.get("hp_threshold", 0)
        }
        if ability_id == "entropic_decay":
            player.entropic_decay_state = {
                "active": False, # This passive is always "active" once acquired, but this flag might be useful for other abilities
                "damage_percentage": effect_data.get("damage_percentage", 0),
                "duration": effect_data.get("duration", 0) * 1000, # Convert to ms
                "max_stacks": effect_data.get("max_stacks", 0),
                "tick_interval": effect_data.get("tick_interval", 1000),
                "enemies_debuffed": {} # Stores {enemy_id: {"stacks": X, "last_tick_time": Y, "applied_time": Z}}
            }
        if ability_id == "paradox_armor":
            player.paradox_armor_state = {
                "active": False,
                "cooldown_start_time": 0,
                "cooldown_duration": effect_data.get("cooldown", 0) * 1000, # Convert to ms
                "damage_delay_percentage": effect_data.get("damage_delay_percentage", 0),
                "damage_delay_duration": effect_data.get("damage_delay_duration", 0) * 1000, # Convert to ms
                "time_revert_duration": effect_data.get("time_revert_duration", 0) * 1000, # Convert to ms
                "delayed_damage": [], # Stores {"amount": X, "apply_time": Y}
                "last_life_snapshot": {"time": 0, "life": 0} # For time revert
            }
        if ability_id == "arc_singularity":
            player.arc_singularity_state = {
                "active": False,
                "cooldown_start_time": 0,
                "cooldown_duration": effect_data.get("cooldown", 0) * 1000,
                "damage_increase_percentage": effect_data.get("damage_increase_percentage", 0),
                "radius": effect_data.get("radius", 0),
                "duration": 0, # Duration is not used for this passive
                "last_activation_time": 0
            }
        if ability_id == "nova_overload":
            player.nova_overload_state = {
                "active": True, # This passive is always active once acquired
                "radius_increase_percentage": effect_data.get("radius_increase_percentage", 0),
                "damage_increase_percentage": effect_data.get("damage_increase_percentage", 0)
            }
        if ability_id == "quantum_entanglement":
            player.quantum_entanglement_state = {
                "active": True,  # Assuming it's always active once acquired
                "chance_to_duplicate": effect_data.get("chance_to_duplicate", 0),
                "duplicate_damage_multiplier": effect_data.get("duplicate_damage_multiplier", 0),
                "duplicate_next_spell": False # New flag
            }
        if ability_id == "ghost_arc":
            player.ghost_arc_state["active"] = True
            player.ghost_arc_state["ignore_walls"] = effect_data.get("ignore_walls", False)
        if ability_id == "double_size_barrier":
            player.double_size_barrier_state["active"] = True
            player.double_size_barrier_state["barrier_size_multiplier"] = effect_data.get("barrier_size_multiplier", 1.0)
        if ability_id == "webweavers_wrath":
            player.webweavers_wrath_state["active"] = True
            player.webweavers_wrath_state["slow_amount"] = effect_data.get("slow_amount", 0)
            player.webweavers_wrath_state["entangle_duration"] = effect_data.get("entangle_duration", 0)
        # Add more passive ability state initializations here
        player.active_passive_abilities[ability_id] = effect_data

    def update_passive_abilities(self, player, dt):
        current_time = pygame.time.get_ticks()
        for ability_id, effect_data in list(player.active_passive_abilities.items()):
            if ability_id == "cleave_reality":
                # cleave_reality is handled directly in CleaveSkill, no continuous update needed here
                pass
            elif ability_id == "void_embrace":
                self._handle_void_embrace(player, effect_data, dt, current_time)
            elif ability_id == "entropic_decay":
                self._handle_entropic_decay(player, effect_data, dt, current_time)
            elif ability_id == "paradox_armor":
                self._handle_paradox_armor(player, effect_data, dt, current_time)
            elif ability_id == "arc_singularity":
                self._handle_arc_singularity(player, effect_data, dt, current_time)
            elif ability_id == "nova_overload":
                self._handle_nova_overload(player, effect_data, dt, current_time)
            elif ability_id == "quantum_entanglement":
                self._handle_quantum_entanglement(player, effect_data, dt, current_time)
            elif ability_id == "webweavers_wrath":
                self._handle_webweavers_wrath(player, effect_data, dt, current_time)
            elif ability_id == "ghost_arc":
                self._handle_ghost_arc(player, effect_data, dt, current_time)
            # Add more passive ability handlers here as they are implemented
            elif ability_id == "arachnophobia":
                self._handle_arachnophobia(player, effect_data, dt, current_time)
            elif ability_id == "necrotic_plague":
                self._handle_necrotic_plague(player, effect_data, dt, current_time)
            elif ability_id == "singularity_core":
                self._handle_singularity_core(player, effect_data, dt, current_time)

    def _handle_void_embrace(self, player, effect_data, dt, current_time):
        state = player.void_embrace_state

        # Check if player HP is below threshold and not on cooldown
        if not state["active"] and player.current_life / player.max_life <= state["hp_threshold"] and \
           (current_time - state["cooldown_start_time"] > state["cooldown_duration"]):

            state["active"] = True
            player.is_intangible = True # Make player intangible
            state["last_regen_tick"] = current_time
            state["activation_time"] = current_time
            print(f"Void Embrace activated! Player is intangible and regenerating.")

        if state["active"]:
            # Apply regeneration
            if current_time - state["last_regen_tick"] > 1000: # Regenerate every second
                regen_amount = player.max_life * state["regen_percentage"]
                player.current_life = min(player.max_life, player.current_life + regen_amount)
                state["last_regen_tick"] = current_time
                print(f"Void Embrace regenerating {regen_amount:.2f} HP. Current HP: {player.current_life:.2f}")

            # Check if duration has expired
            if current_time - state["activation_time"] > state["duration"]:
                state["active"] = False
                player.is_intangible = False # End intangibility
                state["cooldown_start_time"] = current_time # Start cooldown
                print("Void Embrace duration ended. Cooldown started.")

    def _handle_entropic_decay(self, player, effect_data, dt, current_time):
        # Entropic Decay is applied on hit, so its handling here will primarily involve
        # ensuring the player's attacks can trigger the debuff on enemies.
        # This method itself doesn't need to do much in terms of continuous updates,
        # as the debuff logic is handled in entities/enemy.py.
        # However, we might use this to modify player attack properties or
        # register a listener for player hits if needed in the future.
        pass

    def _handle_paradox_armor(self, player, effect_data, dt, current_time):
        state = player.paradox_armor_state

        # Ensure last_life_snapshot is initialized
        if "last_life_snapshot" not in state:
            state["last_life_snapshot"] = {"time": 0, "life": 0}

        # Ensure delayed_damage is initialized
        if "delayed_damage" not in state:
            state["delayed_damage"] = []

        # Update last life snapshot
        state["last_life_snapshot"]["time"] = current_time
        state["last_life_snapshot"]["life"] = player.current_life

        # Apply delayed damage
        new_delayed_damage = []
        for delayed_dmg in state["delayed_damage"]:
            if current_time >= delayed_dmg["apply_time"]:
                player.take_damage(delayed_dmg["amount"])
                print(f"Paradox Armor: Applied {delayed_dmg['amount']:.2f} delayed damage.")
            else:
                new_delayed_damage.append(delayed_dmg)
        state["delayed_damage"] = new_delayed_damage

        # Check for cooldown
        if state["active"] and (current_time - state["cooldown_start_time"] > state["cooldown_duration"]):
            state["active"] = False
            print("Paradox Armor cooldown ended.")

    def _handle_arc_singularity(self, player, effect_data, dt, current_time):
        state = player.arc_singularity_state

        # Arc Singularity activates when ArcSkill is cast.
        # This handler will primarily manage its duration and cooldown.
        if state["active"]:
            if current_time - state["last_activation_time"] > state["duration"]:
                state["active"] = False
                # Revert any temporary stat changes if applied directly here
                print("Arc Singularity duration ended.")
                # Start cooldown
                state["cooldown_start_time"] = current_time
        elif current_time - state["cooldown_start_time"] > state["cooldown_duration"]:
            # Cooldown ended, ready to activate again
            pass

    def _handle_quantum_entanglement(self, player, effect_data, dt, current_time):
        state = player.quantum_entanglement_state
        if state["active"]:
            # This passive doesn't have continuous effects in PasteTreeManager.
            # Its effect (chance to duplicate spell) is checked in Player.activate_skill.
            pass

    def _handle_nova_overload(self, player, effect_data, dt, current_time):
        # Nova Overload is a passive that modifies Ice Nova's properties.
        # It doesn't have continuous effects that need updating here.
        # Its effects are applied directly when Ice Nova is cast or its properties are accessed.
        pass

    def _handle_webweavers_wrath(self, player, effect_data, dt, current_time):
        # Webweaver's Wrath is handled by modifying the spider's attack behavior
        # to create lingering webs. No continuous update needed here.
        pass
    def _handle_arachnophobia(self, player, effect_data, dt, current_time):
        # Arachnophobia: Spiders now explode on death, dealing 300% of their base hp as damage in a 4-tile radius and spawning 3 smaller spiders.
        pass

        player.necrotic_plague_state = {
            "active": True,
            "chance_to_inflict": effect_data.get("chance_to_inflict", 0.20),
            "damage_percentage_per_second": effect_data.get("damage_percentage_per_second", 0.10)
        }
    def _handle_necrotic_plague(self, player, effect_data, dt, current_time):
        # Necrotic Plague: Minion attacks have a 20% chance to inflict a stacking plague that deals 10% max HP per second and spreads to nearby enemies on death.
        pass

    def _handle_singularity_core(self, player, effect_data, dt, current_time):
        # Singularity Core: All damage has a 5% chance to collapse enemies into a micro-singularity, pulling in nearby foes and dealing 1000% damage after 2 seconds.
        pass
    def _handle_ghost_arc(self, player, effect_data, dt, current_time):
        # Ghost Arc is a passive that modifies ArcSkill's projectile behavior.
        # It doesn't have continuous effects that need updating here.
        # Its effects are applied directly when ArcSkill projectiles are created.
        pass

    def _grant_skill(self, player, effect_data):
        skill_id = effect_data.get("skill_id")
        if not skill_id:
            print(f"Skill grant missing ID: {effect_data}")
            return

        player.grant_skill(skill_id)
        print(f"Granted skill: {skill_id}")
