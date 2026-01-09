import pygame
import math
import random
from config.constants import TILE_SIZE
from utility.resource_path import resource_path

class CycloneSkill:
    def __init__(self, player):
        self.player = player
        self.game = player.game
        self.id = "cyclone"
        self.name = "Cyclone"
        self.description = "Spins rapidly, hitting all enemies in a circle repeatedly while draining mana."
        self.mana_cost = 10 + (player.level * 5)  # Initial cost + level scaling
        self.cooldown = 0 # From data/skills.json
        self.channel_cost_per_second = self.player.max_mana * (0.50 + (player.level / 1)) # Scales from 50% + level/10 of max mana per second
        self.hit_interval = 0.05 # From data/skills.json (seconds) - Decreased for faster hits
        self.last_hit_time = 0
        self.is_channeling = False
        self.radius = TILE_SIZE * 3.375 * self.player.cyclone_radius_multiplier # Area of effect for Cyclone, increased by 1.5x (2.25 * 1.5 = 3.375)

        self.bonus_damage_min = 0
        self.bonus_damage_max = 0
        # Visual effect attributes
        self.cyclone_effect_sprites = pygame.sprite.Group() # Use a sprite group for multiple sprites
        self.rotation_angle = 0
        self.num_orbiting_weapons = 3 # Number of weapons orbiting

        # Load default weapon graphic
        self.default_weapon_image = pygame.image.load(resource_path("graphics/UNUSED/weapons/ancient_sword.png")).convert_alpha()
        self.default_weapon_image = pygame.transform.scale(self.default_weapon_image, (TILE_SIZE, TILE_SIZE)) # Scale to tile size
        self.default_weapon_image.set_alpha(180) # Slightly transparent

        self._update_scaled_values() # Call this to set initial damage and speed based on player level

    def _get_scaled_value(self, level, points):
        # points is a list of tuples: [(level1, value1), (level2, value2), ...]
        # Assumes points are sorted by level
        if level <= points[0][0]:
            return points[0][1]
        if level >= points[-1][0]:
            return points[-1][1]

        for i in range(len(points) - 1):
            (l1, v1) = points[i]
            (l2, v2) = points[i+1]
            if l1 <= level <= l2:
                # Linear interpolation
                return v1 + (v2 - v1) * (level - l1) / (l2 - l1)
        return points[-1][1] # Should not be reached if logic is correct

    def _update_scaled_values(self):
        player_level = self.player.level

        # Damage scaling
        min_damage_points = [(1, 10), (50, 50), (100, 100), (200, 1000)]
        max_damage_points = [(1, 20), (50, 100), (100, 200), (200, 2000)]

        self.base_damage = {
            "min": int(self._get_scaled_value(player_level, min_damage_points)),
            "max": int(self._get_scaled_value(player_level, max_damage_points)),
            "type": "physical"
        }

        # Rotation speed scaling
        rotation_speed_points = [(1, 100), (50, 500), (100, 900), (200, 1800)]
        self.rotation_speed = int(self._get_scaled_value(player_level, rotation_speed_points))

    def can_cast(self):
        if self.player.current_mana < self.mana_cost:
            print("Not enough mana for Cyclone!")
            return False
        return True

    def activate(self):
        self._update_scaled_values() # Ensure values are updated based on current player level
        if not self.can_cast():
            return
        print(f"CycloneSkill.activate() called. is_channeling set to True.")
        self.is_channeling = True
        self.last_hit_time = pygame.time.get_ticks()
        print(f"Player activated Cyclone! Mana remaining: {self.player.current_mana}")

        # Create and add multiple continuous visual effect sprites
        if not self.cyclone_effect_sprites: # Only create if group is empty
            for i in range(self.num_orbiting_weapons):
                effect_sprite = pygame.sprite.Sprite()
                effect_sprite.image = self.default_weapon_image
                effect_sprite.rect = effect_sprite.image.get_rect(center=self.player.rect.center)
                effect_sprite.initial_angle_offset = (360 / self.num_orbiting_weapons) * i # Distribute evenly
                self.cyclone_effect_sprites.add(effect_sprite)
                self.game.current_scene.effects.add(effect_sprite)

    def deactivate(self):
        self.is_channeling = False
        print("Cyclone deactivated.")
        # Remove all continuous visual effect sprites
        for sprite in self.cyclone_effect_sprites:
            self.game.current_scene.effects.remove(sprite)
        self.cyclone_effect_sprites.empty() # Clear the group

    def update(self, dt):
        if not self.is_channeling:
            return

        current_time = pygame.time.get_ticks()

        # Drain mana over time
        mana_drain_amount = self.channel_cost_per_second * dt
        self.player.current_mana -= mana_drain_amount
        print(f"Cyclone update: Draining {mana_drain_amount:.2f} mana. Current mana: {self.player.current_mana:.2f}")

        if self.player.current_mana <= 0:
            self.player.current_mana = 0
            self.deactivate()
            print("Cyclone stopped: Out of mana.")
            return

        # Hit enemies at intervals
        if current_time - self.last_hit_time >= self.hit_interval * 1000:
            print(f"Cyclone update: Time for hit. Last hit: {self.last_hit_time}, Current time: {current_time}")
            self.last_hit_time = current_time
            self._perform_hit()

        # Update visual effect position and rotation for each sprite
        self.rotation_angle = (self.rotation_angle + self.rotation_speed * dt) % 360
        
        for sprite in self.cyclone_effect_sprites:
            # Calculate orbiting position with individual offset
            current_orbit_angle = self.rotation_angle + sprite.initial_angle_offset
            offset_x = self.radius * math.cos(math.radians(current_orbit_angle))
            offset_y = self.radius * math.sin(math.radians(current_orbit_angle))
            
            sprite.rect = sprite.image.get_rect(center=(self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y))


    def _perform_hit(self):
        print("Cyclone _perform_hit() called.")
        hit_enemies = set()
        player_center = self.player.rect.center
        print(f"Player center: {player_center}")

        # Projectile blocking logic
        for projectile in self.game.current_scene.projectiles:
            projectile_center = projectile.rect.center
            distance = math.hypot(player_center[0] - projectile_center[0], player_center[1] - projectile_center[1])
            if distance <= self.radius:
                print(f"Cyclone blocked projectile!")
                projectile.kill()  # Remove the projectile from all sprite groups
                continue # Skip enemy hits if a projectile was blocked

        for enemy in self.game.current_scene.enemies:
            enemy_center = enemy.rect.center
            distance = math.hypot(player_center[0] - enemy_center[0], player_center[1] - enemy_center[1])
            print(f"Checking enemy {enemy.name} at {enemy_center}. Distance: {distance:.2f}, Radius: {self.radius:.2f}")
            if distance <= self.radius:
                hit_enemies.add(enemy)
        
        if not hit_enemies:
            print("Cyclone _perform_hit(): No enemies in range.")

        for enemy in hit_enemies:
            damage_amount = random.randint(self.base_damage["min"] + self.bonus_damage_min, self.base_damage["max"] + self.bonus_damage_max)
            enemy.take_damage(damage_amount)
            print(f"Cyclone hit {enemy.name} for {damage_amount} {self.base_damage['type']} damage!")