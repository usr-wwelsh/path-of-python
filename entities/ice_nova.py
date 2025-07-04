import pygame
import math
import random
from config.constants import TILE_SIZE
from entities.arc_skill import ArcProjectile

class IceNovaSkill:
    def __init__(self, player):
        self.player = player
        self.game = player.game
        self.id = "ice_nova"
        self.name = "Ice Nova"
        self.description = "Unleashes a devastating ring of frost that expands outward, freezing enemies at the epicenter and chilling those further away."
        self.mana_cost = 15 + (player.level * 3) # Initial mana cost for activation
        
        # Damage scales from 36 to 51 at level 1 to 500 at level 150
        self.base_damage_min = 36
        self.base_damage_max = 51
        self.max_damage = 500
        self.damage_type = "cold"
        
        self.cooldown = 0.5
        self.cast_time = 0.8 # This might be less relevant for continuous channeling
        self.max_radius = TILE_SIZE * 5
        
        # Freeze/chill effects
        self.freeze_duration = {"base": 1.5, "per_chill_stack": 0.2}
        self.chill_effect = {"slow_percentage": 30, "duration": 4.0}
        
        # Visual effects for initial nova
        self.particle_count = 120
        self.particle_speed = 200 # This might be less relevant for continuous pulsing

        # New attributes for continuous pulsing
        self.is_channeling = False
        self.channel_start_time = 0
        self.mana_per_second_channeled = 10 # Mana cost per second while channeling
        self.last_mana_deduction_time = 0
        self.current_nova_instance = None # To hold the single active pulsing nova
        self.pulsation_min_radius = TILE_SIZE * 0.5 # Minimum radius for pulsation
        base_pulsation_speed = self.max_radius / 0.3
        max_pulsation_speed_multiplier = 3.0
        level_factor = min(1.0, max(0.0, (self.player.level - 1) / (200 - 1)))
        self.pulsation_speed = base_pulsation_speed * (1 + level_factor * (max_pulsation_speed_multiplier - 1)) # Speed for both expansion and contraction (faster than old expansion_speed)
        self.pulsation_hit_interval = 0.5 # How often a hit occurs during pulsation (at max radius)

        # Attributes for the persistent inner ring visual effect
        self.inner_ring_particle_count = 50 # Fewer particles for a less dense inner ring
        self.inner_ring_radius = TILE_SIZE * 1.5 # Fixed radius for the inner ring
        self.inner_ring_color = (100, 150, 200, 255) # Darker blue, fully opaque
        
        # List to hold active nova instances (will primarily hold current_nova_instance)
        self.active_novas = []
        
        # Damage scaling by distance
        self.inner_ring_multiplier = 1.5
        self.outer_ring_multiplier = 0.7

        # New damage scaling breakpoints
        self.damage_breakpoints = {
            1: {"min": 39, "max": 53},
            50: {"min": 300, "max": 500},
            100: {"min": 800, "max": 1000},
            150: {"min": 1300, "max": 1500},
            200: {"min": 4000, "max": 5000}
        }

    def _calculate_damage(self):
        """Calculate damage based on player level using piecewise linear interpolation."""
        player_level = self.player.level
        
        # Find the two breakpoints that the current player level falls between
        levels = sorted(self.damage_breakpoints.keys())
        
        # Handle levels below the first breakpoint
        if player_level <= levels[0]:
            return {"min": self.damage_breakpoints[levels[0]]["min"], 
                    "max": self.damage_breakpoints[levels[0]]["max"], 
                    "type": self.damage_type}
        
        # Handle levels above the last breakpoint
        if player_level >= levels[-1]:
            return {"min": self.damage_breakpoints[levels[-1]]["min"], 
                    "max": self.damage_breakpoints[levels[-1]]["max"], 
                    "type": self.damage_type}

        # Perform linear interpolation between two breakpoints
        for i in range(len(levels) - 1):
            level1 = levels[i]
            level2 = levels[i+1]
            
            if level1 <= player_level <= level2:
                # Calculate interpolation factor
                factor = (player_level - level1) / (level2 - level1)
                
                min_dmg1 = self.damage_breakpoints[level1]["min"]
                max_dmg1 = self.damage_breakpoints[level1]["max"]
                min_dmg2 = self.damage_breakpoints[level2]["min"]
                max_dmg2 = self.damage_breakpoints[level2]["max"]
                
                interpolated_min_dmg = min_dmg1 + (min_dmg2 - min_dmg1) * factor
                interpolated_max_dmg = max_dmg1 + (max_dmg2 - max_dmg1) * factor
                
                return {"min": interpolated_min_dmg, 
                        "max": interpolated_max_dmg, 
                        "type": self.damage_type}
        
        # Fallback (should not be reached if logic is correct)
        return {"min": self.base_damage_min, "max": self.base_damage_max, "type": self.damage_type}

    def can_cast(self):
        if self.is_channeling: # If already channeling, assume it's valid to continue (mana checked in update)
            return True
        if self.player.current_mana < self.mana_cost:
            print("Not enough mana for Ice Nova!")
            return False
        return True

    def activate(self):
        if not self.is_channeling: # Only start channeling if not already
            if not self.can_cast(): # Check initial mana cost
                return
            print(f"IceNovaSkill.activate() called. Starting channeling.")
            self.player.current_mana -= self.mana_cost # Deduct initial mana
            self.is_channeling = True
            self.channel_start_time = pygame.time.get_ticks()
            self.last_mana_deduction_time = self.channel_start_time

            # Create a single nova instance for continuous pulsing
            if self.current_nova_instance:
                # If for some reason an old instance is still active, mark it for removal
                self.current_nova_instance.is_complete = True 
                self.remove_particles(self.current_nova_instance.nova_sprites)
                self.remove_particles(self.current_nova_instance.inner_ring_sprites) # Also remove inner ring particles
            
            self.current_nova_instance = _NovaInstance(self.player, self.game, self)
            self.active_novas.append(self.current_nova_instance) # Add to active_novas for update loop
            print(f"Player activated Ice Nova! Mana remaining: {self.player.current_mana}")
        else:
            print("Ice Nova is already channeling.")

    def stop_channeling(self):
        print("IceNovaSkill.stop_channeling() called.")
        self.is_channeling = False
        if self.current_nova_instance:
            # Allow the current pulse to finish or fade out
            self.current_nova_instance.is_fading_out = True 
            self.current_nova_instance.is_expanding = False # Start shrinking to fade out
            self.current_nova_instance = None # Clear reference, _NovaInstance will handle its own completion
        
    def _create_particle_image(self):
        """Create a frost particle image for the main pulsating nova"""
        size = random.randint(5, 15)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for _ in range(3):
            alpha = random.randint(50, 150)
            color = (200, 230, 255, alpha)
            pygame.draw.circle(surf, color, (size//2, size//2), size//2 - _*2)
        return surf

    def _create_inner_ring_particle_image(self):
        """Create a darker frost particle image for the persistent inner ring"""
        size = random.randint(5, 12) # Smaller particles for inner ring
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = self.inner_ring_color
        pygame.draw.circle(surf, color, (size//2, size//2), size//2)
        return surf

    def update(self, dt):
        # Handle mana deduction for channeling
        if self.is_channeling:
            current_time = pygame.time.get_ticks()
            time_since_last_deduction = (current_time - self.last_mana_deduction_time) / 1000.0 # in seconds
            mana_to_deduct = self.mana_per_second_channeled * time_since_last_deduction

            if mana_to_deduct >= 1: # Deduct mana in whole units or at a reasonable interval
                if self.player.current_mana >= mana_to_deduct:
                    self.player.current_mana -= mana_to_deduct
                    self.last_mana_deduction_time = current_time
                    # print(f"Ice Nova channeling mana deduction. Mana remaining: {self.player.current_mana}")
                else:
                    print("Not enough mana to continue channeling Ice Nova. Stopping.")
                    self.stop_channeling() # Automatically stop if mana runs out

        novas_to_remove = []
        for nova in self.active_novas:
            nova.update(dt)
            if nova.is_complete:
                novas_to_remove.append(nova)
        
        for nova in novas_to_remove:
            self.active_novas.remove(nova)
            # The _NovaInstance itself will handle particle removal when it sets is_complete

    def remove_particles(self, sprite_group):
        """Remove particles from a specific sprite group from the scene"""
        for particle in sprite_group:
            self.game.current_scene.effects.remove(particle)
        sprite_group.empty()


class _NovaInstance(pygame.sprite.Sprite): # Inherit from Sprite to use .image and .rect
    def __init__(self, player, game, skill_parent):
        super().__init__() # Initialize the base Sprite class
        self.player = player
        self.game = game
        self.skill_parent = skill_parent # Reference to IceNovaSkill for shared properties/methods

        self.max_radius = skill_parent.max_radius
        self.min_radius = skill_parent.pulsation_min_radius # Minimum radius for pulsation
        self.pulsation_speed = skill_parent.pulsation_speed # Speed for both expansion and contraction
        self.pulsation_hit_interval = skill_parent.pulsation_hit_interval # How often a hit occurs

        self.current_radius = self.min_radius # Start from min radius for pulsation
        self.is_expanding = True # Controls if it's expanding or shrinking
        self.is_fading_out = False # Flag set when channeling stops, to complete current pulse and remove

        self.is_complete = False # Flag to indicate when this nova instance is done
        self.last_hit_time = pygame.time.get_ticks() # Track last hit time for interval

        self.nova_sprites = pygame.sprite.Group()
        self.inner_ring_sprites = pygame.sprite.Group() # New group for the inner ring
        
        self.current_rotation = 0 # For inner ring rotation

        # Create initial visual effect particles for the main pulsating nova
        for i in range(self.skill_parent.particle_count): 
            particle = pygame.sprite.Sprite()
            particle.image = self.skill_parent._create_particle_image()
            particle.rect = particle.image.get_rect(center=self.player.rect.center)
            particle.angle = (360 / self.skill_parent.particle_count) * i
            particle.distance = self.current_radius # Start at min_radius
            self.nova_sprites.add(particle)
            self.game.current_scene.effects.add(particle)

        # Create particles for the persistent inner ring
        for i in range(self.skill_parent.inner_ring_particle_count):
            particle = pygame.sprite.Sprite()
            particle.original_image = self.skill_parent._create_inner_ring_particle_image() # Store original image
            particle.image = particle.original_image # Current image for display
            particle.rect = particle.image.get_rect(center=self.player.rect.center)
            particle.original_angle = (360 / self.skill_parent.inner_ring_particle_count) * i # Store original angle
            particle.distance = self.skill_parent.inner_ring_radius # Fixed radius for inner ring
            self.inner_ring_sprites.add(particle)
            self.game.current_scene.effects.add(particle)

    def update(self, dt):
        if self.is_complete:
            return

        # Calculate angular speed for inner ring rotation
        if self.pulsation_speed > 0:
            angular_speed = (180 * self.pulsation_speed) / self.max_radius
        else:
            angular_speed = 0 # No rotation if pulsation speed is zero

        self.current_rotation = (self.current_rotation + angular_speed * dt) % 360

        # Update inner ring particle positions and rotation
        for particle in self.inner_ring_sprites:
            # Calculate the new angle for the particle based on the overall ring rotation
            new_particle_angle = (particle.original_angle + self.current_rotation) % 360
            rad_angle = math.radians(new_particle_angle)
            
            # No need to rotate individual particle images, just update their positions
            offset_x = particle.distance * math.cos(rad_angle)
            offset_y = particle.distance * math.sin(rad_angle)
            particle.rect.center = (
                self.player.rect.centerx + offset_x,
                self.player.rect.centery + offset_y
            )

        # Determine target radius and speed based on expansion/contraction for main nova
        if self.is_expanding:
            target_radius = self.max_radius
            speed = self.pulsation_speed
        else:
            target_radius = self.min_radius
            speed = self.pulsation_speed

        # Update current radius for main nova
        if self.is_expanding:
            self.current_radius = min(target_radius, self.current_radius + speed * dt)
        else:
            self.current_radius = max(target_radius, self.current_radius - speed * dt)

        # Update main nova particle positions
        for particle in self.nova_sprites:
            particle.distance = self.current_radius
            rad_angle = math.radians(particle.angle)
            offset_x = particle.distance * math.cos(rad_angle)
            offset_y = particle.distance * math.sin(rad_angle)
            particle.rect.center = (
                self.player.rect.centerx + offset_x,
                self.player.rect.centery + offset_y
            )

        # Check for state transitions for main nova
        if self.is_expanding and self.current_radius >= self.max_radius:
            self.current_radius = self.max_radius # Ensure it's exactly max_radius
            
            # Perform hit only if enough time has passed since last hit
            current_time = pygame.time.get_ticks()
            if (current_time - self.last_hit_time) / 1000.0 >= self.pulsation_hit_interval:
                self.last_hit_time = current_time
                self._perform_hit()
            
            self.is_expanding = False # Start shrinking

        elif not self.is_expanding and self.current_radius <= self.min_radius:
            self.current_radius = self.min_radius # Ensure it's exactly min_radius
            
            if self.skill_parent.is_channeling and not self.is_fading_out:
                self.is_expanding = True # Start expanding again for next pulse
            else:
                # Channeling has stopped, and we've shrunk to min_radius, so complete
                self.is_complete = True
                self.skill_parent.remove_particles(self.nova_sprites) # Remove main nova particles when complete
                self.skill_parent.remove_particles(self.inner_ring_sprites) # Remove inner ring particles too

    def _perform_hit(self):
        damage = self.skill_parent._calculate_damage() # Use skill_parent's damage calculation
        hit_enemies = []
        player_center = self.player.rect.center
        
        # Projectile blocking logic
        for projectile in self.game.current_scene.projectiles:
            projectile_center = projectile.rect.center
            distance = math.hypot(player_center[0] - projectile_center[0], player_center[1] - projectile_center[1])
            if distance <= self.max_radius:
                # Exclude ArcSkill projectiles from being blocked
                if isinstance(projectile, ArcProjectile):
                    # print(f"Ice Nova did NOT block ArcProjectile!") # Commented out for less console spam
                    continue # Do not block ArcProjectile
                print(f"Ice Nova blocked projectile!")
                projectile.kill()  # Remove the projectile from all sprite groups
        
        for enemy in self.game.current_scene.enemies:
            enemy_center = enemy.rect.center
            distance = math.hypot(
                player_center[0] - enemy_center[0],
                player_center[1] - enemy_center[1]
            )
            
            if distance <= self.max_radius:
                # Calculate damage multiplier based on distance
                distance_ratio = distance / self.max_radius
                if distance_ratio < 0.33:  # Inner ring
                    damage_multiplier = self.skill_parent.inner_ring_multiplier
                    # Apply freeze to enemies in inner ring
                    enemy.apply_slow(1.0, self.skill_parent.freeze_duration["base"] + self.skill_parent.freeze_duration["per_chill_stack"] * getattr(enemy, 'chill_stacks', 0))
                else:  # Outer ring
                    damage_multiplier = self.skill_parent.outer_ring_multiplier
                    # Apply chill to enemies in outer ring
                    enemy.apply_slow(
                        self.skill_parent.chill_effect["slow_percentage"] / 100,
                        self.skill_parent.chill_effect["duration"]
                    )
                
                # Calculate final damage
                final_damage = {
                    "min": damage["min"] * damage_multiplier,
                    "max": damage["max"] * damage_multiplier,
                    "type": damage["type"]
                }
                hit_enemies.append((enemy, final_damage))
        
        for enemy, dmg in hit_enemies:
            damage_amount = random.randint(int(dmg["min"]), int(dmg["max"]))
            enemy.take_damage(damage_amount)
            print(f"Ice Nova hit {enemy.name} for {damage_amount} {dmg['type']} damage!")