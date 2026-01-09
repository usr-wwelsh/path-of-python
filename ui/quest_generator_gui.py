import sys
import os
import json
import pygame
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
from tkinter import font as tkFont

from core.new_dungeon_generator import translate_tile_type, load_enemy_data
from ui.dungeon_gui_scene_generator import generate_scene_file, add_scene_to_game_engine
from ui.dungeon_display import display_dungeon
from utility.resource_path import resource_path

class QuestGeneratorGUI:
    def __init__(self, game):
        self.game = game
        self.game.logger.info("QuestGeneratorGUI initialized.")
        self.root = tk.Tk()
        self.root.after(100, self.update_tkinter)
        self.root.title("Quest Generator")
        
        # Apply modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        
        # Configure styles for frames and labels
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabelFrame', background='#f0f0f0', foreground='#333333', font=('Arial', 10, 'bold'))
        self.style.configure('TLabel', background='#f0f0f0', foreground='#333333')
        self.style.configure('TButton', font=('Arial', 9, 'bold'), background='#e0e0e0', foreground='#333333')
        self.style.map('TButton', background=[('active', '#c0c0c0')])
        self.style.configure('TEntry', fieldbackground='#ffffff', foreground='#333333')
        self.style.configure('TCombobox', fieldbackground='#ffffff', foreground='#333333')
        self.style.configure('TCheckbutton', background='#f0f0f0', foreground='#333333')
        
        # Configure text widget for better appearance
        self.root.option_add('*Text.Background', 'white')
        self.root.option_add('*Text.Foreground', 'black')
        self.root.option_add('*Text.Borderwidth', 1)
        self.root.option_add('*Text.Relief', 'solid')
        
        # Define a font for text wrapping
        self.wrapped_font = tkFont.Font(family="Arial", size=9)
        
        # Configure main window layout
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Main container with paned windows
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for tools
        self.left_tools_frame = ttk.Frame(self.main_paned, width=300)
        self.main_paned.add(self.left_tools_frame)

        # Middle panel for map
        self.map_frame = ttk.Frame(self.main_paned, width=600)
        self.main_paned.add(self.map_frame)

        # Right panel for tools
        self.right_tools_frame = ttk.Frame(self.main_paned, width=300)
        self.main_paned.add(self.right_tools_frame)
        
        # Initialize components
        self.create_quest_controls()
        self.create_tile_tools() 
        self.create_npc_controls()
        self.create_enemy_controls()
        self.create_objectives_editor()
        self.create_toolbar()
        
        # Canvas for displaying the quest map
        self.canvas = tk.Canvas(self.map_frame, width=600, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Quest data structure
        self.quest_data = {
            'width': 20,
            'height': 20,
            'tile_map': [[0 for _ in range(20)] for _ in range(20)],
            'npcs': [],
            'enemies': [],
            'objectives': [],
            'rewards': {},
            'name': 'New Quest',
            'description': '',
            'tileset': 'default',
            'is_completed': False,
            'is_unlocked': True,
            'tilemap_scene_name': ''
        }
        
        # Editor state
        self.zoom_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.current_tool = None
        self.selected_tile = 0
        self.selected_npc = None
        self.selected_enemy = None

    def create_quest_controls(self):
        # Quest metadata frame
        meta_frame = ttk.LabelFrame(self.left_tools_frame, text="Quest Metadata")
        meta_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Name
        ttk.Label(meta_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        self.quest_name_entry = ttk.Entry(meta_frame)
        self.quest_name_entry.insert(0, "New Quest")
        self.quest_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Description
        ttk.Label(meta_frame, text="Description:").grid(row=1, column=0, sticky=tk.NW)
        self.desc_text = tk.Text(meta_frame, height=4, width=30)
        self.desc_text.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Scene name
        ttk.Label(meta_frame, text="Scene Name:").grid(row=2, column=0, sticky=tk.W)
        self.scene_name_entry = ttk.Entry(meta_frame)
        self.scene_name_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Map dimensions
        dim_frame = ttk.Frame(meta_frame)
        dim_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
        
        ttk.Label(dim_frame, text="Width:").pack(side=tk.LEFT)
        self.width_entry = ttk.Entry(dim_frame, width=5)
        self.width_entry.insert(0, "20")
        self.width_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dim_frame, text="Height:").pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(dim_frame, width=5)
        self.height_entry.insert(0, "20")
        self.height_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(dim_frame, text="Resize", command=self.resize_map).pack(side=tk.RIGHT)
        
        # Tileset selection
        ttk.Label(meta_frame, text="Tileset:").grid(row=4, column=0, sticky=tk.W)
        with open(resource_path('data/tileset_mappings.json'), 'r') as f:
            tileset_data = json.load(f)
        self.tileset_options = list(tileset_data.keys())
        self.tileset_combo = ttk.Combobox(meta_frame, values=self.tileset_options)
        self.tileset_combo.set("default")
        self.tileset_combo.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Status
        status_frame = ttk.Frame(meta_frame)
        status_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW)
        
        self.unlocked_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(status_frame, text="Unlocked", variable=self.unlocked_var).pack(side=tk.LEFT)
        
        self.completed_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(status_frame, text="Completed", variable=self.completed_var).pack(side=tk.LEFT)

    def create_tile_tools(self):
        tile_frame = ttk.LabelFrame(self.left_tools_frame, text="Tile Tools")
        tile_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tile_types = {
            0: "Empty",
            1: "Floor", 
            2: "Wall",
            3: "Water",
            4: "Door",
            5: "Player Spawn"
        }
        
        for i, (tile_id, tile_name) in enumerate(self.tile_types.items()):
            btn = ttk.Radiobutton(
                tile_frame, 
                text=tile_name, 
                value=tile_id,
                variable=tk.IntVar(value=0),
                command=lambda t=tile_id: self.select_tile(t)
            )
            btn.grid(row=i//3, column=i%3, sticky=tk.W, padx=2, pady=2)
        
        # Draw Radius
        ttk.Label(tile_frame, text="Draw Radius:").grid(row=len(self.tile_types)//3 + 1, column=0, sticky=tk.W)
        self.draw_radius_var = tk.IntVar(value=0) # Default to 0 for single tile
        self.draw_radius_spinbox = ttk.Spinbox(tile_frame, from_=0, to=5, textvariable=self.draw_radius_var, width=5)
        self.draw_radius_spinbox.grid(row=len(self.tile_types)//3 + 1, column=1, sticky=tk.W, padx=2, pady=2)

    def create_npc_controls(self):
        npc_frame = ttk.LabelFrame(self.right_tools_frame, text="NPC Management")
        npc_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # NPC list with scrollbar
        npc_list_frame = ttk.Frame(npc_frame)
        npc_list_frame.pack(fill=tk.X)
        
        self.npc_listbox = tk.Listbox(npc_list_frame, height=5)
        self.npc_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.npc_listbox.bind('<<ListboxSelect>>', self.select_npc)
        
        scrollbar = ttk.Scrollbar(npc_list_frame, orient=tk.VERTICAL, command=self.npc_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.npc_listbox.config(yscrollcommand=scrollbar.set)
        
        # NPC controls
        btn_frame = ttk.Frame(npc_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Add NPC", command=self.add_npc).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Remove NPC", command=self.remove_npc).pack(side=tk.LEFT)
        
        # NPC properties
        props_frame = ttk.Frame(npc_frame)
        props_frame.pack(fill=tk.X)
        
        ttk.Label(props_frame, text="Dialog:").pack(anchor=tk.W)
        self.dialog_text = tk.Text(props_frame, height=5, width=30)
        self.dialog_text.pack(fill=tk.X, padx=5, pady=2)
        
        sprite_frame = ttk.Frame(npc_frame)
        sprite_frame.pack(fill=tk.X)
        
        ttk.Label(sprite_frame, text="Sprite:").pack(side=tk.LEFT)
        self.sprite_button = ttk.Button(sprite_frame, text="Select Sprite", command=self.select_sprite)
        self.sprite_button.pack(side=tk.LEFT, padx=5)
        self.sprite_preview = ttk.Label(sprite_frame)
        self.sprite_preview.pack(side=tk.LEFT)

    def create_enemy_controls(self):
        enemy_frame = ttk.LabelFrame(self.right_tools_frame, text="Enemy Placement")
        enemy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Enemy type selection
        type_frame = ttk.Frame(enemy_frame)
        type_frame.pack(fill=tk.X)
        
        ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT)
        enemy_data = load_enemy_data('data/enemy_data.json')
        self.enemy_types = list(enemy_data.keys())
        self.enemy_combo = ttk.Combobox(type_frame, values=self.enemy_types)
        self.enemy_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Enemy stats
        stats_frame = ttk.Frame(enemy_frame)
        stats_frame.pack(fill=tk.X)
        
        ttk.Label(stats_frame, text="Health:").pack(side=tk.LEFT)
        self.health_entry = ttk.Entry(stats_frame, width=5)
        self.health_entry.insert(0, "50")
        self.health_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(stats_frame, text="Damage:").pack(side=tk.LEFT)
        self.damage_entry = ttk.Entry(stats_frame, width=5)
        self.damage_entry.insert(0, "10")
        self.damage_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(stats_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_entry = ttk.Entry(stats_frame, width=5)
        self.speed_entry.insert(0, "40")
        self.speed_entry.pack(side=tk.LEFT, padx=2)
        
        # Enemy list
        enemy_list_frame = ttk.Frame(enemy_frame)
        enemy_list_frame.pack(fill=tk.X)
        
        self.enemy_listbox = tk.Listbox(enemy_list_frame, height=5)
        self.enemy_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.enemy_listbox.bind('<<ListboxSelect>>', self.select_enemy)
        
        scrollbar = ttk.Scrollbar(enemy_list_frame, orient=tk.VERTICAL, command=self.enemy_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.enemy_listbox.config(yscrollcommand=scrollbar.set)
        
        # Enemy controls
        btn_frame = ttk.Frame(enemy_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Place Enemy", command=self.place_enemy).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Remove Enemy", command=self.remove_enemy).pack(side=tk.LEFT)

    def create_objectives_editor(self):
        obj_frame = ttk.LabelFrame(self.right_tools_frame, text="Objectives")
        obj_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Objectives list
        obj_list_frame = ttk.Frame(obj_frame)
        obj_list_frame.pack(fill=tk.X)
        
        self.objectives_listbox = tk.Listbox(obj_list_frame, height=5)
        self.objectives_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.objectives_listbox.bind('<<ListboxSelect>>', self.select_objective)
        
        scrollbar = ttk.Scrollbar(obj_list_frame, orient=tk.VERTICAL, command=self.objectives_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.objectives_listbox.config(yscrollcommand=scrollbar.set)
        
        # Objective controls
        btn_frame = ttk.Frame(obj_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Add Objective", command=self.add_objective).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Remove Objective", command=self.remove_objective).pack(side=tk.LEFT)
        
        # Objective text
        ttk.Label(obj_frame, text="Description:").pack(anchor=tk.W)
        self.objective_text = tk.Text(obj_frame, height=3, width=30)
        self.objective_text.pack(fill=tk.X, padx=5, pady=2)

    def create_toolbar(self):
        toolbar = ttk.Frame(self.map_frame)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(toolbar, text="Select", command=lambda: self.set_tool('select')).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Paint", command=lambda: self.set_tool('paint')).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Erase", command=lambda: self.set_tool('erase')).pack(side=tk.LEFT)
        
        ttk.Button(toolbar, text="Save", command=self.save_quest).pack(side=tk.RIGHT)
        ttk.Button(toolbar, text="Load", command=self.load_quest).pack(side=tk.RIGHT)
        ttk.Button(toolbar, text="Test", command=self.test_quest).pack(side=tk.RIGHT)

    def set_tool(self, tool):
        self.current_tool = tool
        if tool == 'select':
            self.canvas.config(cursor="arrow")
        else:
            self.canvas.config(cursor="cross")

    def select_tile(self, tile_id):
        self.selected_tile = tile_id

    def select_npc(self, event):
        selection = self.npc_listbox.curselection()
        if selection:
            self.selected_npc = selection[0]
            npc = self.quest_data['npcs'][self.selected_npc]
            self.dialog_text.delete(1.0, tk.END)
            self.dialog_text.insert(1.0, npc.get('dialog', ''))
            
            # Load sprite preview if exists
            if 'sprite' in npc and npc['sprite']:
                try:
                    img = Image.open(npc['sprite'])
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.sprite_preview.config(image=photo)
                    self.sprite_preview.image = photo
                except Exception as e:
                    print(f"Error loading sprite: {e}")

    def select_enemy(self, event):
        selection = self.enemy_listbox.curselection()
        if selection:
            self.selected_enemy = selection[0]
            enemy = self.quest_data['enemies'][self.selected_enemy]
            self.enemy_combo.set(enemy['type'])
            self.health_entry.delete(0, tk.END)
            self.health_entry.insert(0, str(enemy.get('health', 50)))
            self.damage_entry.delete(0, tk.END)
            self.damage_entry.insert(0, str(enemy.get('damage', 10)))
            self.speed_entry.delete(0, tk.END)
            self.speed_entry.insert(0, str(enemy.get('speed', 40)))

    def select_objective(self, event):
        selection = self.objectives_listbox.curselection()
        if selection:
            obj_index = selection[0]
            objective = self.quest_data['objectives'][obj_index]
            self.objective_text.delete(1.0, tk.END)
            self.objective_text.insert(1.0, objective.get('description', ''))

    def add_npc(self):
        npc = {
            'x': 0,
            'y': 0,
            'sprite': '',
            'dialog': 'Hello traveler!'
        }
        self.quest_data['npcs'].append(npc)
        self.npc_listbox.insert(tk.END, f"NPC {len(self.quest_data['npcs'])}")
        self.selected_npc = len(self.quest_data['npcs']) - 1
        self.npc_listbox.selection_set(self.selected_npc)

    def remove_npc(self):
        if self.selected_npc is not None:
            self.quest_data['npcs'].pop(self.selected_npc)
            self.npc_listbox.delete(self.selected_npc)
            self.selected_npc = None
            self.dialog_text.delete(1.0, tk.END)
            self.sprite_preview.config(image='')
            self.sprite_preview.image = None

    def add_objective(self):
        objective = {
            'description': 'New objective',
            'completed': False
        }
        self.quest_data['objectives'].append(objective)
        self.objectives_listbox.insert(tk.END, objective['description'])
        self.objectives_listbox.selection_clear(0, tk.END)
        self.objectives_listbox.selection_set(tk.END)

    def remove_objective(self):
        selection = self.objectives_listbox.curselection()
        if selection:
            obj_index = selection[0]
            self.quest_data['objectives'].pop(obj_index)
            self.objectives_listbox.delete(obj_index)
            self.objective_text.delete(1.0, tk.END)

    def select_sprite(self):
        if self.selected_npc is None:
            return
            
        filename = filedialog.askopenfilename(
            initialdir="graphics/dc-mon",
            title="Select NPC Sprite",
            filetypes=(("PNG files", "*.png"), ("all files", "*.*"))
        )
        
        if filename:
            self.quest_data['npcs'][self.selected_npc]['sprite'] = filename
            try:
                img = Image.open(filename)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.sprite_preview.config(image=photo)
                self.sprite_preview.image = photo
            except Exception as e:
                messagebox.showerror("Error", f"Could not load sprite: {e}")

    def place_enemy(self):
        enemy_type = self.enemy_combo.get()
        if not enemy_type:
            return
            
        try:
            health = int(self.health_entry.get())
            damage = int(self.damage_entry.get())
            speed = int(self.speed_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Health, damage and speed must be numbers")
            return
            
        self.current_tool = 'place_enemy'
        self.canvas.config(cursor="cross")
        self.pending_enemy = {
            'type': enemy_type,
            'health': health,
            'damage': damage,
            'speed': speed
        }

    def remove_enemy(self):
        if self.selected_enemy is not None:
            self.quest_data['enemies'].pop(self.selected_enemy)
            self.enemy_listbox.delete(self.selected_enemy)
            self.selected_enemy = None
            self.redraw_map()

    def resize_map(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            
            if width < 5 or height < 5:
                raise ValueError("Minimum size is 5x5")
                
            # Create new empty map
            new_map = [[0 for _ in range(width)] for _ in range(height)]
            
            # Copy existing tiles that fit in new dimensions
            for y in range(min(height, len(self.quest_data['tile_map']))):
                for x in range(min(width, len(self.quest_data['tile_map'][0]))):
                    new_map[y][x] = self.quest_data['tile_map'][y][x]
            
            self.quest_data['tile_map'] = new_map
            self.quest_data['width'] = width
            self.quest_data['height'] = height
            
            self.redraw_map()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def on_canvas_click(self, event):
        x = int((event.x - self.offset_x) / (32 * self.zoom_scale))
        y = int((event.y - self.offset_y) / (32 * self.zoom_scale))
        
        if 0 <= x < self.quest_data['width'] and 0 <= y < self.quest_data['height']:
            if self.current_tool == 'paint':
                self.apply_tile_change(x, y, self.selected_tile)
            elif self.current_tool == 'erase':
                self.apply_tile_change(x, y, 0)
            elif self.current_tool == 'place_enemy' and hasattr(self, 'pending_enemy'):
                enemy = self.pending_enemy.copy()
                enemy['x'] = x
                enemy['y'] = y
                self.quest_data['enemies'].append(enemy)
                self.enemy_listbox.insert(tk.END, f"{enemy['type']} at ({x},{y})")
                self.current_tool = None
                self.canvas.config(cursor="")
            elif self.selected_npc is not None:
                self.quest_data['npcs'][self.selected_npc]['x'] = x
                self.quest_data['npcs'][self.selected_npc]['y'] = y
                self.npc_listbox.delete(self.selected_npc)
                self.npc_listbox.insert(self.selected_npc, f"NPC at ({x},{y})")
                self.npc_listbox.selection_set(self.selected_npc)
            
            self.redraw_map()

    def on_canvas_drag(self, event):
        if self.current_tool in ['paint', 'erase']:
            self.on_canvas_click(event)
    def apply_tile_change(self, center_x, center_y, tile_value):
        radius = self.draw_radius_var.get()
        for y_offset in range(-radius, radius + 1):
            for x_offset in range(-radius, radius + 1):
                x, y = center_x + x_offset, center_y + y_offset
                if 0 <= x < self.quest_data['width'] and 0 <= y < self.quest_data['height']:
                    self.quest_data['tile_map'][y][x] = tile_value

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_scale *= 1.1
        else:
            self.zoom_scale /= 1.1
        self.redraw_map()

    def redraw_map(self):
        self.canvas.delete("all")
        
        # Draw tiles
        for y in range(self.quest_data['height']):
            for x in range(self.quest_data['width']):
                tile_type = self.quest_data['tile_map'][y][x]
                color = self.get_tile_color(tile_type)
                self.canvas.create_rectangle(
                    x * 32 * self.zoom_scale + self.offset_x,
                    y * 32 * self.zoom_scale + self.offset_y,
                    (x + 1) * 32 * self.zoom_scale + self.offset_x,
                    (y + 1) * 32 * self.zoom_scale + self.offset_y,
                    fill=color,
                    outline='black'
                )
        
        # Draw NPCs
        for i, npc in enumerate(self.quest_data['npcs']):
            x, y = npc.get('x', 0), npc.get('y', 0)
            color = 'blue' if i == self.selected_npc else 'darkblue'
            self.canvas.create_oval(
                x * 32 * self.zoom_scale + self.offset_x,
                y * 32 * self.zoom_scale + self.offset_y,
                (x + 1) * 32 * self.zoom_scale + self.offset_x,
                (y + 1) * 32 * self.zoom_scale + self.offset_y,
                fill=color
            )
        
        # Draw enemies
        for i, enemy in enumerate(self.quest_data['enemies']):
            x, y = enemy.get('x', 0), enemy.get('y', 0)
            color = 'red' if i == self.selected_enemy else 'darkred'
            self.canvas.create_rectangle(
                x * 32 * self.zoom_scale + self.offset_x,
                y * 32 * self.zoom_scale + self.offset_y,
                (x + 1) * 32 * self.zoom_scale + self.offset_x,
                (y + 1) * 32 * self.zoom_scale + self.offset_y,
                fill=color
            )

    def get_tile_color(self, tile_type):
        colors = {
            0: 'black',    # Empty
            1: 'gray',     # Floor
            2: 'brown',    # Wall
            3: 'blue',     # Water
            4: 'yellow',   # Door
            5: 'green'     # Player Spawn
        }
        return colors.get(tile_type, 'white')

    def save_quest(self):
        # Update quest data from UI
        self.quest_data['name'] = self.quest_name_entry.get()
        self.quest_data['description'] = self.desc_text.get(1.0, tk.END).strip()
        self.quest_data['tileset'] = self.tileset_combo.get()
        self.quest_data['is_unlocked'] = self.unlocked_var.get()
        self.quest_data['is_completed'] = self.completed_var.get()
        
        # Set scene name if empty
        scene_name = self.scene_name_entry.get().strip()
        if not scene_name:
            scene_name = f"quest_{self.quest_data['name'].lower().replace(' ', '_')}"
            self.scene_name_entry.delete(0, tk.END)
            self.scene_name_entry.insert(0, scene_name)
        self.quest_data['tilemap_scene_name'] = scene_name
        
        # Save NPC dialog
        if self.selected_npc is not None:
            self.quest_data['npcs'][self.selected_npc]['dialog'] = self.dialog_text.get(1.0, tk.END).strip()
        
        # Save objectives
        for i, obj in enumerate(self.quest_data['objectives']):
            if i < self.objectives_listbox.size():
                obj['description'] = self.objectives_listbox.get(i)
        
        filename = simpledialog.askstring("Save Quest", "Enter filename:")
        if filename:
            # Save to file
            quest_dir = "data/quests"
            if not os.path.exists(quest_dir):
                os.makedirs(quest_dir)
            filepath = os.path.join(quest_dir, f'{filename}.json')
            
            with open(filepath, 'w') as f:
                json.dump(self.quest_data, f, indent=4)
            
            # Generate scene file
            generate_scene_file(filename, self.quest_data)
            add_scene_to_game_engine(filename)
            self.game.scene_manager.load_scenes()
            
            messagebox.showinfo("Success", f"Quest saved to {filepath}")

    def load_quest(self):
        filename = filedialog.askopenfilename(
            initialdir="data/quests",
            title="Select Quest File",
            filetypes=(("JSON files", "*.json"), ("all files", "*.*"))
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.quest_data = json.load(f)
                
                # Update UI
                self.quest_name_entry.delete(0, tk.END)
                self.quest_name_entry.insert(0, self.quest_data.get('name', 'New Quest'))
                
                self.desc_text.delete(1.0, tk.END)
                self.desc_text.insert(1.0, self.quest_data.get('description', ''))
                
                self.scene_name_entry.delete(0, tk.END)
                self.scene_name_entry.insert(0, self.quest_data.get('tilemap_scene_name', ''))
                
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(self.quest_data.get('width', 20)))
                
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(self.quest_data.get('height', 20)))
                
                self.tileset_combo.set(self.quest_data.get('tileset', 'default'))
                self.unlocked_var.set(self.quest_data.get('is_unlocked', False))
                self.completed_var.set(self.quest_data.get('is_completed', False))
                
                # Load NPCs
                self.npc_listbox.delete(0, tk.END)
                for npc in self.quest_data.get('npcs', []):
                    self.npc_listbox.insert(tk.END, f"NPC at ({npc.get('x', 0)},{npc.get('y', 0)})")
                
                # Load enemies
                self.enemy_listbox.delete(0, tk.END)
                for enemy in self.quest_data.get('enemies', []):
                    self.enemy_listbox.insert(tk.END, 
                        f"{enemy.get('type', 'unknown')} at ({enemy.get('x', 0)},{enemy.get('y', 0)})")
                
                # Load objectives
                self.objectives_listbox.delete(0, tk.END)
                for obj in self.quest_data.get('objectives', []):
                    self.objectives_listbox.insert(tk.END, obj.get('description', ''))
                
                self.redraw_map()
                messagebox.showinfo("Success", "Quest loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not load quest: {e}")

    def test_quest(self):
        messagebox.showinfo("Info", "Test functionality would launch the quest in a test environment")

    def update_tkinter(self):
        self.root.update_idletasks()
        self.root.update()
        self.root.after(100, self.update_tkinter)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    class DummyGame:
        def __init__(self):
            self.settings = type('Settings', (object,), {'FULLSCREEN': False})()
            self.logger = type('Logger', (object,), {'info': print, 'error': print})()
            self.scene_manager = type('SceneManager', (object,), {'set_scene': print})()
        def apply_display_settings(self):
            pass

    gui = QuestGeneratorGUI(DummyGame())
    gui.run()