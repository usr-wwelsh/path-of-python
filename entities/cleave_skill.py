import pygame
import math
import random
from config.constants import TILE_SIZE
from entities.enemy import Enemy # Import Enemy for type hinting and potential future use

class CleaveSkill:
    def __init__(self, player):
        self.player = player
        self.game = player.game
        self.id = "cleave"
        self.name = "Cleave"
        self.description = "A wide, sweeping attack that damages enemies in an arc."
        self.mana_cost = 7 # From data/skills.json
        self.base_damage = {"min": 50, "max": 200, "type": "physical"} # From data/skills.json
        self.cooldown = 0 # From data/skills.json
        self.attack_speed_multiplier = 1.0 # From data/skills.json
        self.last_cast_time = 0
        self.cooldown_duration = 0 # Cleave has 0 cooldown in skills.json, but adding for consistency

        # Cleave specific attributes
        self.arc_angle = math.radians(90) # 90-degree arc
        self.drawing_range = TILE_SIZE * 4 # Visual drawing range
        self.attack_range = TILE_SIZE * 6 # Attack range, 50% more than drawing range

        self.active_effects = pygame.sprite.Group() # To manage temporary visual effects

        # Cleave Reality passive ability attributes
        self.reality_hits_required = 5
        self.reality_damage_multiplier = 3.0
        self.reality_cone_radius = TILE_SIZE * 10 # Larger radius for reality effect
        self.reality_slow_percentage = 0.70
        self.reality_slow_duration = 3000 # milliseconds
        self.current_hits = 0 # Counter for hits to trigger reality effect

    def can_cast(self):
        current_time = pygame.time.get_ticks()
        if self.player.current_mana < self.mana_cost:
            print("Not enough mana for Cleave!")
            return False
        if current_time - self.last_cast_time < self.cooldown_duration * 1000:
            print("Cleave is on cooldown!")
            return False
        return True

    def activate(self):
        if not self.can_cast():
            return

        self.player.current_mana -= self.mana_cost
        self.last_cast_time = pygame.time.get_ticks()
        print(f"Player activated Cleave! Mana remaining: {self.player.current_mana}")

        # Calculate the direction the player is facing (assuming mouse position determines direction)
        mouse_x, mouse_y = self.game.input_handler.get_mouse_pos()
        player_screen_x = self.player.rect.centerx - self.game.current_scene.camera_x
        player_screen_y = self.player.rect.centery - self.game.current_scene.camera_y

        # Invert the y-component for angle calculation to account for Pygame's inverted y-axis
        direction_vector = pygame.math.Vector2(mouse_x - player_screen_x, -(mouse_y - player_screen_y))
        if direction_vector.length_squared() == 0: # Use length_squared for efficiency
            direction_vector = pygame.math.Vector2(1, 0) # Default to right if no mouse movement
        direction_vector = direction_vector.normalize()

        # Calculate the center angle of the cleave arc
        center_angle = math.atan2(direction_vector.y, direction_vector.x) # Angle of mouse cursor

        # Calculate the start and end angles of the arc for hit detection and drawing
        start_angle = center_angle - (self.arc_angle / 2)
        end_angle = center_angle + (self.arc_angle / 2)

        print(f"--- Cleave Activation Debug ---")
        print(f"Mouse (screen): ({mouse_x}, {mouse_y})")
        print(f"Player (screen): ({player_screen_x}, {player_screen_y})")
        print(f"Direction Vector: {direction_vector}")
        print(f"Center Angle (degrees): {math.degrees(center_angle):.2f}")
        print(f"Start Angle (degrees): {math.degrees(start_angle):.2f}")
        print(f"End Angle (degrees): {math.degrees(end_angle):.2f}")
        print(f"Cleave Drawing Range: {self.drawing_range}")
        print(f"Cleave Attack Range: {self.attack_range}")
        print(f"Arc Angle (degrees): {math.degrees(self.arc_angle):.2f}")
        print(f"--- Enemy Hit Detection ---")
        
        # Detect enemies within the cleave arc
        hit_enemies = set()
        player_center_world = self.player.rect.center # Player's world coordinates
        
        for enemy in self.game.current_scene.enemies:
            enemy_vector = pygame.math.Vector2(enemy.rect.centerx - player_center_world[0],
                                                -(enemy.rect.centery - player_center_world[1])) # Invert y-component
            
            if enemy_vector.length() <= self.attack_range:
                # Check if enemy is within the angular arc
                angle_to_enemy = math.atan2(enemy_vector.y, enemy_vector.x)
                
                # Calculate the angular difference and normalize it to (-pi, pi]
                angle_diff = angle_to_enemy - center_angle
                angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi # Normalize to (-pi, pi]

                print(f"  Enemy: {enemy.name} at ({enemy.rect.centerx}, {enemy.rect.centery})")
                print(f"    Enemy Vector: {enemy_vector}")
                print(f"    Distance to Enemy: {enemy_vector.length():.2f}")
                print(f"    Angle to Enemy (degrees): {math.degrees(angle_to_enemy):.2f}")
                print(f"    Angle Diff (degrees): {math.degrees(angle_diff):.2f}")
                print(f"    Within Arc: {abs(angle_diff) <= (self.arc_angle / 2)}")

                if abs(angle_diff) <= (self.arc_angle / 2):
                    hit_enemies.add(enemy)

        for enemy in hit_enemies:
            damage_amount = random.randint(self.base_damage["min"], self.base_damage["max"])
            # Apply cleave_damage_multiplier from player stats
            damage_amount *= self.player.cleave_damage_multiplier
            enemy.take_damage(damage_amount)
            print(f"Cleave hit {enemy.name} for {damage_amount} {self.base_damage['type']} damage!")
            self.current_hits += 1 # Increment hit counter for Cleave Reality

        # Check for Cleave Reality activation
        if "cleave_reality" in self.player.active_passive_abilities and self.current_hits >= self.reality_hits_required:
            print(f"Cleave Reality activated after {self.current_hits} hits!")
            self._apply_reality_effect(center_angle)
            self.current_hits = 0 # Reset hit counter

        # --- Visual effect for Cleave ---
        effect_size = int(self.drawing_range * 2.5) # Slightly larger surface to prevent clipping
        cleave_effect_surface = pygame.Surface((effect_size, effect_size), pygame.SRCALPHA)
        
        # Center for drawing on the effect surface
        surface_center = (effect_size // 2, effect_size // 2)

        # Define colors for the gradient/layers
        color_outer_most = (255, 50, 0, 60) # Very transparent, deep orange
        color_outer = (255, 100, 0, 100) # Fiery orange, more transparent
        color_middle = (255, 165, 0, 150) # Orange, semi-transparent
        color_inner = (255, 223, 0, 200) # Gold/Yellow, less transparent
        color_core = (255, 255, 150, 220) # Bright yellow, almost opaque
        color_flash = (255, 255, 255, 255) # White flash

        # Draw multiple arcs for a layered, "whoosh" effect
        # Outermost arc (thinnest, most transparent)
        pygame.draw.arc(cleave_effect_surface, color_outer_most,
                        (surface_center[0] - self.drawing_range * 1.3, surface_center[1] - self.drawing_range * 1.3,
                         self.drawing_range * 2.6, self.drawing_range * 2.6),
                        start_angle, end_angle, int(TILE_SIZE * 0.1))

        # Outer arc (thinner, more transparent)
        pygame.draw.arc(cleave_effect_surface, color_outer,
                        (surface_center[0] - self.drawing_range * 1.2, surface_center[1] - self.drawing_range * 1.2,
                         self.drawing_range * 2.4, self.drawing_range * 2.4),
                        start_angle, end_angle, int(TILE_SIZE * 0.2))

        # Middle arc (medium thickness, medium transparency)
        pygame.draw.arc(cleave_effect_surface, color_middle,
                        (surface_center[0] - self.drawing_range, surface_center[1] - self.drawing_range,
                         self.drawing_range * 2, self.drawing_range * 2),
                        start_angle, end_angle, int(TILE_SIZE * 0.4))

        # Inner arc (thickest, less transparent)
        pygame.draw.arc(cleave_effect_surface, color_inner,
                        (surface_center[0] - self.drawing_range * 0.8, surface_center[1] - self.drawing_range * 0.8,
                         self.drawing_range * 1.6, self.drawing_range * 1.6),
                        start_angle, end_angle, int(TILE_SIZE * 0.6))
        
        # Core arc (very thick, almost opaque)
        pygame.draw.arc(cleave_effect_surface, color_core,
                        (surface_center[0] - self.drawing_range * 0.6, surface_center[1] - self.drawing_range * 0.6,
                         self.drawing_range * 1.2, self.drawing_range * 1.2),
                        start_angle, end_angle, int(TILE_SIZE * 0.8))

        # Add a "flash" at the player's center for impact
        pygame.draw.circle(cleave_effect_surface, color_flash, surface_center, int(TILE_SIZE * 0.4), 0)
        
        effect_sprite = pygame.sprite.Sprite()
        effect_sprite.image = cleave_effect_surface
        effect_sprite.rect = effect_sprite.image.get_rect(center=self.player.rect.center)
        effect_sprite.creation_time = pygame.time.get_ticks()
        effect_sprite.duration = 250 # milliseconds for the effect to last and fade
        self.active_effects.add(effect_sprite) # Add to skill's own group
        self.game.current_scene.effects.add(effect_sprite) # Add to scene's effects group

    def _apply_reality_effect(self, center_angle):
        """Applies the special 'Cleave Reality' effect."""
        reality_start_angle = center_angle - (self.arc_angle / 2)
        reality_end_angle = center_angle + (self.arc_angle / 2)

        player_center_world = self.player.rect.center
        
        # Detect enemies within the larger reality cone
        reality_hit_enemies = set()
        for enemy in self.game.current_scene.enemies:
            enemy_vector = pygame.math.Vector2(enemy.rect.centerx - player_center_world[0],
                                                -(enemy.rect.centery - player_center_world[1]))
            
            if enemy_vector.length() <= self.reality_cone_radius:
                angle_to_enemy = math.atan2(enemy_vector.y, enemy_vector.x)
                angle_diff = (angle_to_enemy - center_angle + math.pi) % (2 * math.pi) - math.pi

                if abs(angle_diff) <= (self.arc_angle / 2): # Use the original arc angle for the reality cone's angular spread
                    reality_hit_enemies.add(enemy)

        for enemy in reality_hit_enemies:
            # Apply increased damage
            reality_damage = random.randint(self.base_damage["min"], self.base_damage["max"]) * self.reality_damage_multiplier
            # Apply cleave_damage_multiplier from player stats
            reality_damage *= self.player.cleave_damage_multiplier
            enemy.take_damage(reality_damage)
            print(f"Cleave Reality hit {enemy.name} for {reality_damage} {self.base_damage['type']} damage (Reality Effect)!")

            # Apply slow effect
            enemy.apply_slow(self.reality_slow_percentage, self.reality_slow_duration)
            print(f"Applied {self.reality_slow_percentage*100}% slow to {enemy.name} for {self.reality_slow_duration/1000} seconds.")

        # Visual effect for Cleave Reality (larger, distinct color)
        effect_size = int(self.reality_cone_radius * 2.5)
        reality_effect_surface = pygame.Surface((effect_size, effect_size), pygame.SRCALPHA)
        surface_center = (effect_size // 2, effect_size // 2)

        # Reality effect colors (e.g., blue/purple for a "reality shift" feel)
        color_reality_outer = (0, 100, 255, 80) # Light blue, transparent
        color_reality_inner = (50, 0, 150, 180) # Purple, less transparent
        color_reality_core = (100, 0, 200, 220) # Deeper purple, almost opaque

        pygame.draw.arc(reality_effect_surface, color_reality_outer,
                        (surface_center[0] - self.reality_cone_radius * 1.3, surface_center[1] - self.reality_cone_radius * 1.3,
                         self.reality_cone_radius * 2.6, self.reality_cone_radius * 2.6),
                        reality_start_angle, reality_end_angle, int(TILE_SIZE * 0.2))
        pygame.draw.arc(reality_effect_surface, color_reality_inner,
                        (surface_center[0] - self.reality_cone_radius, surface_center[1] - self.reality_cone_radius,
                         self.reality_cone_radius * 2, self.reality_cone_radius * 2),
                        reality_start_angle, reality_end_angle, int(TILE_SIZE * 0.6))
        pygame.draw.arc(reality_effect_surface, color_reality_core,
                        (surface_center[0] - self.reality_cone_radius * 0.6, surface_center[1] - self.reality_cone_radius * 0.6,
                         self.reality_cone_radius * 1.2, self.reality_cone_radius * 1.2),
                        reality_start_angle, reality_end_angle, int(TILE_SIZE * 1.0))

        reality_effect_sprite = pygame.sprite.Sprite()
        reality_effect_sprite.image = reality_effect_surface
        reality_effect_sprite.rect = reality_effect_sprite.image.get_rect(center=self.player.rect.center)
        reality_effect_sprite.creation_time = pygame.time.get_ticks()
        reality_effect_sprite.duration = 500 # Longer duration for reality effect
        self.active_effects.add(reality_effect_sprite)
        self.game.current_scene.effects.add(reality_effect_sprite)

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        for effect in list(self.active_effects): # Iterate over a copy to allow removal
            elapsed_time = current_time - effect.creation_time
            if elapsed_time >= effect.duration:
                self.game.current_scene.effects.remove(effect)
                self.active_effects.remove(effect)
            else:
                # Calculate alpha based on elapsed time for fading effect
                initial_alpha = 255 # Max alpha for the effect surface
                fade_progress = elapsed_time / effect.duration
                current_alpha = max(0, initial_alpha - int(initial_alpha * fade_progress))
                
                # Apply the fading alpha to the effect image
                effect.image.set_alpha(current_alpha)