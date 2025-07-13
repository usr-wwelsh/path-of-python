from core.base_gameplay_scene import BaseGameplayScene
import pygame as pg

import json
import os
import random
import math

import core

class SpriteWithFilename(pg.Surface):
    def __init__(self, size, filename=""):
        super().__init__(size)
        self.filename = filename

class FleshAlgorithmTerminal(BaseGameplayScene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.name = "flesh_algorithm_terminal"
        self.skills = self.load_skills()
        if self.skills:
            self.selected_skill = self.skills[0]
        else:
            self.selected_skill = None
        self.cost = 250000
        self.hud = None
        self.player = None
        self.frame_count = 0
        self.tile_map = None
        self.decorations = []

        self.sprite_parts = ["head", "body", "hand1", "hand2", "gloves", "legs", "base"]
        self.sprite_filenames = {part: [] for part in self.sprite_parts}
        self.selected_sprites = {part: None for part in self.sprite_parts}
        self.sprites = self.load_sprites()
        for part in self.sprite_parts:
            if self.sprite_filenames[part]:
                self.selected_sprites[part] = self.sprite_filenames[part][0]
        self.current_sprite_part_index = 0 # Initialize selected part for keyboard control

        # Lore-friendly terminal theme colors
        self.primary_color = (180, 50, 50)  # Muted, unsettling red/flesh tone
        self.secondary_color = (100, 30, 30) # Darker, deeper red
        self.tertiary_color = (50, 150, 50) # A sickly green for accents
        self.glitch_color_options = [(255, 0, 0), (0, 255, 255), (255, 255, 0), (100, 200, 100), (200, 100, 200)] # More varied and unsettling glitch colors
        self.title_color = self.primary_color
        self.text_color = (200, 200, 200) # Off-white for general text
        self.border_color = (70, 20, 20) # Dark red for borders

        self.glitch_timer = 0
        self.glitch_offset = 0
        self.glitch_amplitude = 3 # Increased amplitude for more noticeable glitches
        self.screen_shake_intensity = 2 # New: for screen shake effect

        # Fonts - using a more generic font for a "terminal" feel
        self.font_large = pg.font.Font(None, 52) # Slightly larger title
        self.font_medium = pg.font.Font(None, 38) # Slightly larger main text
        self.font_small = pg.font.Font(None, 26) # Slightly larger smaller details
        self.font_mono = pg.font.Font(None, 28) # New: for monospace-like text

        self.arrow_size = (20, 20)
        self.arrow_color = self.primary_color
        self.arrow_left = pg.Surface(self.arrow_size, pg.SRCALPHA)
        self.arrow_left.fill((0,0,0,0)) # Transparent background
        pg.draw.polygon(self.arrow_left, self.arrow_color, [(self.arrow_size[0], 0), (0, self.arrow_size[1] / 2), (self.arrow_size[0], self.arrow_size[1])])
        self.arrow_right = pg.transform.flip(self.arrow_left, True, False)
        self.arrow_rects = {part: {"left": None, "right": None} for part in self.sprite_parts}

        # Button properties
        self.button_width = 200
        self.button_height = 50
        self.button_margin = 20
        self.cancel_button_rect = None
        self.confirm_button_rect = None
        self.apply_button_rect = None
        self.button_color = self.secondary_color # Use secondary color for buttons
        self.button_hover_color = self.primary_color # Use primary color for hover
        self.button_text_color = (255, 255, 255)

    def load_skills(self):
        with open("data/skills.json", "r") as f:
            skills_data = json.load(f)
        return [skill["name"] for skill in skills_data["active_skills"]]

    def load_sprites(self):
        sprites = {}
        for part in self.sprite_parts:
            sprite_dir = os.path.join("graphics", "player", part)
            loaded_sprites = []
            filenames = []
            print(f"Loading sprites from: {sprite_dir}")  # Log the directory
            try:
                for f in os.listdir(sprite_dir):
                    if f.endswith(".png"):
                        print(f"Attempting to load: {f}")  # Log the filename
                        try:
                            sprite = pg.image.load(os.path.join(sprite_dir, f)).convert_alpha()
                            custom_sprite = SpriteWithFilename(sprite.get_size())
                            custom_sprite.blit(sprite, (0, 0))
                            custom_sprite.filename = f  # Set the filename attribute
                            loaded_sprites.append(custom_sprite)
                            filenames.append(f)
                            print(f"Loaded sprite: {f}")  # Log that the sprite was loaded
                        except pg.error as e:
                            print(f"Error loading sprite: {f} - {e}")
                    else:
                        print(f"Skipping non-PNG file: {f}")  # Log skipped files
            except FileNotFoundError:
                print(f"Directory not found: {sprite_dir}")
            sprites[part] = loaded_sprites
            self.sprite_filenames[part] = filenames
            print(f"Filenames for {part}: {filenames}")  # Log the filenames list
        return sprites

    def handle_event(self, event):
        if not self.skills:
            return False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                # Cycle through sprite parts for selection
                self.current_sprite_part_index = (self.current_sprite_part_index + 1) % len(self.sprite_parts)
                self.game.redraw = True
            elif event.key == pg.K_UP:
                # Cycle through sprite parts for selection
                self.current_sprite_part_index = (self.current_sprite_part_index - 1) % len(self.sprite_parts)
                self.game.redraw = True
            elif event.key == pg.K_LEFT:
                # Cycle sprites for the currently selected part (left)
                part = self.sprite_parts[self.current_sprite_part_index]
                if self.sprite_filenames[part]:
                    current_index = next((i for i, filename in enumerate(self.sprite_filenames[part]) if filename == self.selected_sprites[part]), -1)
                    if current_index != -1:
                        next_index = (current_index - 1) % len(self.sprite_filenames[part])
                        self.selected_sprites[part] = self.sprite_filenames[part][next_index]
                        self.game.redraw = True
                        self.update_player_sprite()
            elif event.key == pg.K_RIGHT:
                # Cycle sprites for the currently selected part (right)
                part = self.sprite_parts[self.current_sprite_part_index]
                if self.sprite_filenames[part]:
                    current_index = next((i for i, filename in enumerate(self.sprite_filenames[part]) if filename == self.selected_sprites[part]), -1)
                    if current_index != -1:
                        next_index = (current_index + 1) % len(self.sprite_filenames[part])
                        self.selected_sprites[part] = self.sprite_filenames[part][next_index]
                        self.game.redraw = True
                        self.update_player_sprite()
            return True
        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = pg.mouse.get_pos()
            screen_width = self.game.screen.get_width()
            center_x = screen_width // 2
            initial_y_offset = 500 # This should match the initial y_offset in draw
            arrow_spacing = 30

            # Check if cancel or apply button was clicked
            if self.cancel_button_rect and self.cancel_button_rect.collidepoint(mouse_pos):
                self.game.scene_manager.set_scene(self.game.scene_manager.previous_scene_name)
                return True
            elif self.confirm_button_rect and self.confirm_button_rect.collidepoint(mouse_pos):
                self.confirm_changes()
                self.game.scene_manager.set_scene(self.game.scene_manager.previous_scene_name)
                return True
            elif self.apply_button_rect and self.apply_button_rect.collidepoint(mouse_pos):
                self.randomize_sprites()
    

            for i, part in enumerate(self.sprite_parts):
                current_y_offset = initial_y_offset + i * 75 # Calculate y_offset based on part index
                arrow_left_x = center_x - arrow_spacing - self.arrow_size[0]
                arrow_right_x = center_x + arrow_spacing

                # Adjust arrow_y to be vertically centered with the sprite, similar to draw method
                # Assuming sprite height is roughly 4x arrow height for centering
                sprite_display_height_offset = 30 # This is the offset used in draw for sprite y position
                arrow_y = current_y_offset + sprite_display_height_offset - (self.arrow_size[1] / 2)

                arrow_left_rect = pg.Rect(arrow_left_x, arrow_y, self.arrow_size[0], self.arrow_size[1])
                arrow_right_rect = pg.Rect(arrow_right_x, arrow_y, self.arrow_size[0], self.arrow_size[1])

                if arrow_left_rect.collidepoint(mouse_pos):
                    if self.sprite_filenames[part]:
                        current_index = next((idx for idx, filename in enumerate(self.sprite_filenames[part]) if filename == self.selected_sprites[part]), -1)
                        if current_index != -1:
                            next_index = (current_index - 1) % len(self.sprite_filenames[part])
                            self.selected_sprites[part] = self.sprite_filenames[part][next_index]
                            self.game.redraw = True
                            self.update_player_sprite()
                        else: # If selected_sprites[part] is None or not found, default to the last sprite
                            self.selected_sprites[part] = self.sprite_filenames[part][-1]
                    return True
                elif arrow_right_rect.collidepoint(mouse_pos):
                    if self.sprite_filenames[part]:
                        current_index = next((idx for idx, filename in enumerate(self.sprite_filenames[part]) if filename == self.selected_sprites[part]), -1)
                        if current_index != -1:
                            next_index = (current_index + 1) % len(self.sprite_filenames[part])
                            self.selected_sprites[part] = self.sprite_filenames[part][next_index]
                            self.game.redraw = True
                            self.update_player_sprite()
                        else: # If selected_sprites[part] is None or not found, default to the first sprite
                            self.selected_sprites[part] = self.sprite_filenames[part][0]
                    return True
        return False

    def update(self, dt):
        super().update(dt)
        self.glitch_timer += dt
        if self.glitch_timer > 0.06: # More frequent glitches
            self.glitch_timer = 0
            if random.random() < 0.5: # Higher chance of color glitch
                self.title_color = random.choice(self.glitch_color_options)
            else:
                self.title_color = self.primary_color

            # Introduce positional glitch
            self.glitch_offset = random.randint(-self.glitch_amplitude, self.glitch_amplitude)
            self.glitch_amplitude = random.randint(2, 4) # Vary amplitude more

            # Screen shake
            self.screen_offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity) if random.random() < 0.2 else 0
            self.screen_offset_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity) if random.random() < 0.2 else 0
        else:
            self.screen_offset_x = 0
            self.screen_offset_y = 0


    def open(self):
        self.game.scene_manager.set_scene(self.name)

    def draw(self, screen):
        super().draw(screen)
        # Get screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        center_x = screen_width // 2

        # Apply a subtle screen shake/offset for the whole terminal feel
        # These are now updated in the update method for consistent glitching
        screen_offset_x = self.screen_offset_x
        screen_offset_y = self.screen_offset_y

        # Draw a background rectangle for the terminal screen
        terminal_rect = pg.Rect(50, 50, screen_width - 100, screen_height - 100)
        pg.draw.rect(screen, (10, 10, 10), terminal_rect) # Dark background
        pg.draw.rect(screen, self.border_color, terminal_rect, 3) # Border

        # Title
        title_text = "PROFIT ENGINE // FLESH ALGORITHM v.7.3.4"
        text_surface = self.font_large.render(title_text, True, self.title_color)

        # Apply glitch offset to title
        title_x = 100 + self.glitch_offset + screen_offset_x
        title_y = 100 + self.glitch_offset + screen_offset_y
        screen.blit(text_surface, (title_x, title_y))

        # Subtitle/Status
        status_text = "[STATUS: MEATWARE_INTERFACE_ACTIVE // BIO-SIGNATURE_CONFIRMED]"
        status_surface = self.font_medium.render(status_text, True, self.tertiary_color) # Use sickly green
        screen.blit(status_surface, (100 + screen_offset_x, 150 + screen_offset_y))

        # Skill Selection
        skill_label = self.font_medium.render("[MODULE: NEURAL_ADAPTATION_PROTOCOL]", True, self.primary_color)
        screen.blit(skill_label, (100 + screen_offset_x, 200 + screen_offset_y))

        skill_value = self.font_mono.render(f"> {self.selected_skill or 'NO_MODULE_SELECTED'}", True, self.text_color)
        screen.blit(skill_value, (120 + screen_offset_x, 230 + screen_offset_y))

        # Cost Display
        cost_label = self.font_medium.render("[RESOURCE: PROFIT_PASTE_UNITS_REQUIRED]", True, self.primary_color)
        screen.blit(cost_label, (100 + screen_offset_x, 300 + screen_offset_y))

        cost_value = self.font_mono.render(f"> 5 UNITS (ESTIMATED_CONSUMPTION)", True, self.text_color)
        screen.blit(cost_value, (120 + screen_offset_x, 330 + screen_offset_y))

        # Draw buttons in the top right corner
        button_x = screen_width - self.button_width - self.button_margin - 50 # Adjust for terminal border
        button_y = self.button_margin + 50 # Adjust for terminal border

        # Cancel button
        cancel_button_text = self.font_small.render("TERMINATE_SESSION", True, self.button_text_color)
        cancel_button_rect = pg.Rect(button_x, button_y, self.button_width, self.button_height)
        self.cancel_button_rect = cancel_button_rect

        # Check if mouse is hovering over the cancel button
        mouse_pos = pg.mouse.get_pos()
        if cancel_button_rect.collidepoint(mouse_pos):
            pg.draw.rect(screen, self.button_hover_color, cancel_button_rect)
        else:
            pg.draw.rect(screen, self.button_color, cancel_button_rect)

        # Draw button text centered
        cancel_text_rect = cancel_button_text.get_rect(center=cancel_button_rect.center)
        screen.blit(cancel_button_text, cancel_text_rect)

        # Confirm button
        button_y += self.button_height + self.button_margin
        confirm_button_text = self.font_small.render("INITIATE_REPROGRAM", True, self.button_text_color)
        confirm_button_rect = pg.Rect(button_x, button_y, self.button_width, self.button_height)
        self.confirm_button_rect = confirm_button_rect

        # Check if mouse is hovering over the confirm button
        if confirm_button_rect.collidepoint(mouse_pos):
            pg.draw.rect(screen, self.button_hover_color, confirm_button_rect)
        else:
            pg.draw.rect(screen, self.button_color, confirm_button_rect)

        # Draw button text centered
        confirm_text_rect = confirm_button_text.get_rect(center=confirm_button_rect.center)
        screen.blit(confirm_button_text, confirm_text_rect)

        # Apply button
        button_y += self.button_height + self.button_margin
        apply_button_text = self.font_small.render("RANDOMIZE_FLESH", True, self.button_text_color)
        apply_button_rect = pg.Rect(button_x, button_y, self.button_width, self.button_height)
        self.apply_button_rect = apply_button_rect

        # Check if mouse is hovering over the apply button
        if apply_button_rect.collidepoint(mouse_pos):
            pg.draw.rect(screen, self.button_hover_color, apply_button_rect)
        else:
            pg.draw.rect(screen, self.button_color, apply_button_rect)

        # Draw button text centered
        apply_text_rect = apply_button_text.get_rect(center=apply_button_rect.center)
        screen.blit(apply_button_text, apply_text_rect)

        # Sprite Selection
        y_offset = 400
        for i, part in enumerate(self.sprite_parts): # Use enumerate to get index
            # Sprite Label
            label_color = self.primary_color
            if i == self.current_sprite_part_index: # Highlight selected part
                label_color = (255, 255, 0) # Yellow for selected part
            part_label = self.font_medium.render(f"[FLESH_COMPONENT: {part.upper()}]", True, label_color)
            screen.blit(part_label, (100 + screen_offset_x, y_offset + screen_offset_y))

            # Draw the sprite
            if self.selected_sprites[part]:
                print(f"Drawing part: {part}, Selected sprite filename: {self.selected_sprites[part]}")
                sprite = next((s for s in self.sprites[part] if s.filename == self.selected_sprites[part]), None)
                if sprite:
                    print(f"Found sprite for {part}: {sprite.filename}")
                    # Scale the sprite to 4x its original size
                    scaled_sprite = pg.transform.scale(sprite, (int(sprite.get_width() * 2), int(sprite.get_height() * 2)))
                    sprite_rect = scaled_sprite.get_rect(center=(center_x + screen_offset_x, y_offset + 30 + screen_offset_y))
                    screen.blit(scaled_sprite, sprite_rect)

                    # Draw arrows next to the scaled sprite (removed random glitch for arrows)
                    arrow_padding = 10 # Padding between sprite and arrow
                    arrow_y = sprite_rect.centery - (self.arrow_size[1] / 2) # Vertically center with sprite

                    arrow_left_x = sprite_rect.left - self.arrow_size[0] - arrow_padding
                    arrow_right_x = sprite_rect.right + arrow_padding

                    screen.blit(self.arrow_left, (arrow_left_x, arrow_y))
                    screen.blit(self.arrow_right, (arrow_right_x, arrow_y))
                    self.arrow_rects[part]["left"] = pg.Rect(arrow_left_x, arrow_y, self.arrow_size[0], self.arrow_size[1])
                    self.arrow_rects[part]["right"] = pg.Rect(arrow_right_x, arrow_y, self.arrow_size[0], self.arrow_size[1])
                else:
                    print(f"Sprite not found for {part} with filename {self.selected_sprites[part]}")
            y_offset += 75 # Decreased vertical spacing

        # Add some decorative lines/elements
        pg.draw.line(screen, self.tertiary_color, (100 + screen_offset_x, 280 + screen_offset_y), (screen_width - 300 + screen_offset_x, 280 + screen_offset_y), 2)
        pg.draw.line(screen, self.tertiary_color, (100 + screen_offset_x, 380 + screen_offset_y), (screen_width - 300 + screen_offset_x, 380 + screen_offset_y), 2)
        pg.draw.line(screen, self.tertiary_color, (100 + screen_offset_x, screen_height - 150 + screen_offset_y), (screen_width - 100 + screen_offset_x, screen_height - 150 + screen_offset_y), 2)

        # Add a blinking cursor effect
        if int(pg.time.get_ticks() / 500) % 2 == 0:
            cursor_text = self.font_mono.render("_", True, self.text_color)
            screen.blit(cursor_text, (120 + screen_offset_x + skill_value.get_width() + 5, 230 + screen_offset_y))


    def update_sprite_part(self, part, sprite_index):
        """
        Updates the selected sprite for a given part based on the sprite index.
        """
        if part in self.sprite_parts and self.sprite_filenames[part]:
            if 0 <= sprite_index < len(self.sprite_filenames[part]):
                self.selected_sprites[part] = self.sprite_filenames[part][sprite_index]
                self.update_player_sprite()
            else:
                print(f"Invalid sprite index: {sprite_index} for part: {part}")
        else:
            print(f"Invalid part: {part} or no sprites loaded for this part.")

    def update_player_sprite(self):
    #"Updates the player's sprite based on currently selected parts."""
        if not hasattr(self.game, 'player'):
            return

        for part in self.sprite_parts:
            if self.selected_sprites[part]:
                sprite_path = os.path.join("graphics", "player", part, self.selected_sprites[part])
            try:
                sprite = pg.image.load(sprite_path).convert_alpha()
                # Double the sprite size
                sprite = pg.transform.scale(sprite, (sprite.get_width() * 2, sprite.get_height() * 2))
                setattr(self.game.player, f"{part}_sprite", sprite)
                print(f"Updated player {part} sprite to: {sprite_path}")
            except pg.error as e:
                print(f"Error updating player {part} sprite: {e}")

    def randomize_sprites(self):
        """
        Randomly selects a sprite for each part and updates the player's sprite.
        """
        for part in self.sprite_parts:
            if self.sprite_filenames[part]:
                random_filename = random.choice(self.sprite_filenames[part])
                self.selected_sprites[part] = random_filename
        self.update_player_sprite()
        self.game.redraw = True
    def confirm_changes(self):
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'paste') and self.game.player.paste >= self.cost:
            self.game.player.paste -= self.cost
            
            if hasattr(self.game.player, 'rebuild_sprite'):
                self.game.player.rebuild_sprite()
        else:
            print("Insufficient profit paste to confirm changes")
