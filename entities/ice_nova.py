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
        self.max_damage = 5000
        self.damage_type = "cold"
        
        self.cooldown = 0.5 # Cooldown for click-based activation
        self.last_cast_time = 0 # Track last cast time for cooldown
        self.cast_time = 0.8 # This might be less relevant for continuous channeling
        self.max_radius = TILE_SIZE * 5
        
        # Freeze/chill effects
        self.freeze_duration = {"base": 1.5, "per_chill_stack": 0.2}
        self.chill_effect = {"slow_percentage": 30, "duration": 4.0}
        
        # Visual effects for initial nova
        self.particle_count = 120
        self.particle_speed = 200 # This might be less relevant for continuous pulsing

        # Attributes for single pulse nova
        self.pulsation_min_radius = TILE_SIZE * 0.5 # Minimum radius for pulsation
        base_pulsation_speed = self.max_radius / 0.3
        max_pulsation_speed_multiplier = 3.0
        level_factor = min(1.0, max(0.0, (self.player.level - 1) / (200 - 1)))
        self.pulsation_speed = base_pulsation_speed * (1 + level_factor * (max_pulsation_speed_multiplier - 1)) # Speed for both expansion and contraction (faster than old expansion_speed)
        self.pulsation_hit_interval = 0.1 # How often a hit occurs during pulsation (at max radius)
        
        # List to hold active nova instances (each click creates one)
        self.active_novas = []

        # New attributes for the dark blue barrier circle
        self.barrier_duration = 10.0 # Barrier lasts for 10 seconds (changed from 3.0)
        self.barrier_color = (0, 0, 139, 200) # Dark blue, slightly transparent
        self.barrier_radius = (TILE_SIZE ) # Radius for the barrier (half the size)
        self.active_barriers = [] # List to hold active barrier instances
        
        # Barrier DoT and Slow effects
        self.barrier_dot_interval = 0.1 # Damage and slow every 0.1 seconds
        self.barrier_slow_percentage = 70 # Super slow movement (70% slow)
        self.barrier_slow_duration = 5.0 # Slow effect lasts for 1 second (reapplied every interval)

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

        # Nova Overload passive ability
        self.effective_max_radius = self.max_radius
        self.effective_base_damage_min = self.base_damage_min
        self.effective_base_damage_max = self.base_damage_max

    def _calculate_damage(self):
        """Calculate damage based on player level using piecewise linear interpolation."""
        player_level = self.player.level
        
        # Find the two breakpoints that the current player level falls between
        levels = sorted(self.damage_breakpoints.keys())
        
        # Apply Nova Overload damage increase
        if "nova_overload" in self.player.active_passive_abilities:
            nova_overload_effect_data = self.player.active_passive_abilities["nova_overload"]
            damage_increase_percentage = nova_overload_effect_data.get("damage_increase_percentage", 0)
            
            # Temporarily adjust base damage for calculation
            original_base_damage_min = self.base_damage_min
            original_base_damage_max = self.base_damage_max
            self.base_damage_min *= (1 + damage_increase_percentage)
            self.base_damage_max *= (1 + damage_increase_percentage)

        # Handle levels below the first breakpoint
        if player_level <= levels[0]:
            calculated_damage = {"min": self.damage_breakpoints[levels[0]]["min"], 
                                 "max": self.damage_breakpoints[levels[0]]["max"], 
                                 "type": self.damage_type}
        
        # Handle levels above the last breakpoint
        elif player_level >= levels[-1]:
            calculated_damage = {"min": self.damage_breakpoints[levels[-1]]["min"], 
                                 "max": self.damage_breakpoints[levels[-1]]["max"], 
                                 "type": self.damage_type}

        # Perform linear interpolation between two breakpoints
        else:
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
                    
                    calculated_damage = {"min": interpolated_min_dmg, 
                                         "max": interpolated_max_dmg, 
                                         "type": self.damage_type}
                    break
            else: # Fallback (should not be reached if logic is correct)
                calculated_damage = {"min": self.base_damage_min, "max": self.base_damage_max, "type": self.damage_type}

        # Revert base damage to original values after calculation
        if "nova_overload" in self.player.active_passive_abilities:
            self.base_damage_min = original_base_damage_min
            self.base_damage_max = original_base_damage_max
            
            # Apply damage increase to the calculated damage
            calculated_damage["min"] *= (1 + damage_increase_percentage)
            calculated_damage["max"] *= (1 + damage_increase_percentage)
            print(f"Nova Overload: Damage increased by {damage_increase_percentage*100:.0f}% to min {calculated_damage['min']:.2f}, max {calculated_damage['max']:.2f}")

        return calculated_damage

    def can_cast(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_cast_time) / 1000.0 < self.cooldown:
            # print("Ice Nova is on cooldown!")
            return False
        if self.player.current_mana < self.mana_cost:
            print("Not enough mana for Ice Nova!")
            return False
        return True

    def activate(self, is_duplicate=False): # Added is_duplicate parameter
        if not is_duplicate: # Only apply cooldown and mana cost for original cast
            if not self.can_cast():
                return
            print(f"IceNovaSkill.activate() called. Casting single nova.")
            self.player.current_mana -= self.mana_cost # Deduct initial mana
            self.last_cast_time = pygame.time.get_ticks() # Set last cast time for cooldown
        
        # Apply Nova Overload radius increase
        self.effective_max_radius = self.max_radius
        if "nova_overload" in self.player.active_passive_abilities:
            nova_overload_effect_data = self.player.active_passive_abilities["nova_overload"]
            radius_increase_percentage = nova_overload_effect_data.get("radius_increase_percentage", 0)
            self.effective_max_radius = self.max_radius * (1 + radius_increase_percentage)
            print(f"Nova Overload: Max radius increased by {radius_increase_percentage*100:.0f}% to {self.effective_max_radius:.2f}")

        # Create a new nova instance for each click
        new_nova = _NovaInstance(self.player, self.game, self)
        self.active_novas.append(new_nova)
        
        # Create a new barrier instance at player's current position
        new_barrier = _IceNovaBarrier(
            self.game, 
            self.player.rect.center, 
            self.barrier_radius * self.player.double_size_barrier_state["barrier_size_multiplier"], 
            self.barrier_color, 
            self.barrier_duration,
            self # Pass skill_parent for damage/slow calculation
        )
        self.active_barriers.append(new_barrier)

        print(f"Player cast Ice Nova! Mana remaining: {self.player.current_mana}")
        
    def _create_particle_image(self):
        """Create a frost particle image for the main pulsating nova"""
        size = random.randint(5, 15)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for _ in range(3):
            alpha = random.randint(50, 150)
            color = (200, 230, 255, alpha)
            pygame.draw.circle(surf, color, (size//2, size//2), size//2 - _*2)
        return surf

    def update(self, dt):
        # Update and remove completed nova instances
        novas_to_remove = []
        for nova in self.active_novas:
            nova.update(dt)
            if nova.is_complete:
                novas_to_remove.append(nova)
        
        for nova in novas_to_remove:
            self.active_novas.remove(nova)
            # The _NovaInstance itself will handle particle removal when it sets is_complete

        # Update and remove completed barrier instances
        barriers_to_remove = []
        for barrier in self.active_barriers:
            barrier.update(dt)
            if barrier.is_complete:
                barriers_to_remove.append(barrier)
        
        for barrier in barriers_to_remove:
            self.active_barriers.remove(barrier)
            # The _IceNovaBarrier itself will handle its removal from effects

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

        self.max_radius = skill_parent.effective_max_radius # Use effective_max_radius
        self.min_radius = skill_parent.pulsation_min_radius # Minimum radius for pulsation
        self.pulsation_speed = skill_parent.pulsation_speed # Speed for both expansion and contraction
        self.pulsation_hit_interval = skill_parent.pulsation_hit_interval # How often a hit occurs

        self.current_radius = self.min_radius # Start from min radius for pulsation
        self.is_expanding = True # Controls if it's expanding or shrinking
        
        self.is_complete = False # Flag to indicate when this nova instance is done
        self.last_hit_time = pygame.time.get_ticks() # Track last hit time for interval

        self.nova_sprites = pygame.sprite.Group()
        
        # Create initial visual effect particles for the main pulsating nova
        for i in range(self.skill_parent.particle_count): 
            particle = pygame.sprite.Sprite()
            particle.image = self.skill_parent._create_particle_image()
            particle.rect = particle.image.get_rect(center=self.player.rect.center)
            particle.angle = (360 / self.skill_parent.particle_count) * i
            particle.distance = self.current_radius # Start at min_radius
            self.nova_sprites.add(particle)
            self.game.current_scene.effects.add(particle)

    def update(self, dt):
        if self.is_complete:
            return

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
            
            # After one full expansion and contraction, this nova instance is complete
            self.is_complete = True
            self.skill_parent.remove_particles(self.nova_sprites) # Remove main nova particles when complete

    def _perform_hit(self):
        damage = self.skill_parent._calculate_damage() # Use skill_parent's damage calculation
        hit_enemies = []
        player_center = self.player.rect.center
        
        # Projectile blocking logic removed from here, now handled by _IceNovaBarrier
        
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


class _IceNovaBarrier(pygame.sprite.Sprite):
    def __init__(self, game, position, radius, color, duration, skill_parent, barrier_size_multiplier=1.0):
        super().__init__()
        self.game = game
        self.position = position
        self.radius = radius * barrier_size_multiplier
        self.base_color = color # Base dark blue
        self.duration = duration
        self.skill_parent = skill_parent # Reference to IceNovaSkill for damage/slow
        self.creation_time = pygame.time.get_ticks()
        self.is_complete = False

        self.glow_color = (0, 255, 255) # Neon Cyan for hacker look
        self.glow_thickness = 2
        self.grid_density = 15 # Spacing for grid lines
        self.flicker_timer = 0
        self.flicker_interval = 100 # ms between flickers

        self.last_damage_time = pygame.time.get_ticks() # For DoT and slow application

        self._draw_barrier_image() # Initial drawing

        # Add to effects group
        self.game.current_scene.effects.add(self)

    def _draw_barrier_image(self, flicker_offset=0):
        size = int(self.radius * 2)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)

        # Base dark blue filled circle
        pygame.draw.circle(self.image, self.base_color, center, int(self.radius))

        # Glowing outer ring (pulsating effect handled in update by alpha)
        # Draw with full alpha here, update will modify it
        pygame.draw.circle(self.image, self.glow_color, center, int(self.radius), self.glow_thickness)

        # Grid pattern
        for i in range(0, size, self.grid_density):
            pygame.draw.line(self.image, self.glow_color + (50,), (i, 0), (i, size), 1) # Vertical lines
            pygame.draw.line(self.image, self.glow_color + (50,), (0, i), (size, i), 1) # Horizontal lines

        # Apply flicker offset
        if flicker_offset != 0:
            temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            temp_surf.blit(self.image, (flicker_offset, flicker_offset))
            self.image = temp_surf

        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        if self.is_complete:
            return

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.creation_time) / 1000.0

        if elapsed_time >= self.duration:
            self.is_complete = True
            self.game.current_scene.effects.remove(self)
            return

        # Pulsating glow effect
        # Use sine wave for smooth pulsation, varying alpha
        pulse_factor = (math.sin(elapsed_time * 1.25) + 1) / 2 # Varies from 0 to 1
        alpha = int(100 + pulse_factor * 155) # Alpha from 100 to 255
        
        # Flicker effect
        self.flicker_timer += dt * 1000 # Convert dt to milliseconds
        if self.flicker_timer >= self.flicker_interval:
            flicker_offset = random.choice([-1, 0, 1]) if random.random() < 0.3 else 0 # 30% chance to flicker
            # Re-evaluate radius based on current player state before redrawing
            self.radius = self.skill_parent.barrier_radius * self.skill_parent.player.double_size_barrier_state["barrier_size_multiplier"]
            self._draw_barrier_image(flicker_offset)
            self.flicker_timer = 0
        
        # Apply pulsating alpha to the entire image
        self.image.set_alpha(alpha)

        # Damage over time and super slow application
        if (current_time - self.last_damage_time) / 1000.0 >= self.skill_parent.barrier_dot_interval:
            self.last_damage_time = current_time
            damage = self.skill_parent._calculate_damage()
            
            for enemy in self.game.current_scene.enemies:
                enemy_center = enemy.rect.center
                distance = math.hypot(self.position[0] - enemy_center[0], self.position[1] - enemy_center[1])
                
                if distance <= self.radius:
                    # Apply outer ring damage multiplier
                    final_damage = {
                        "min": damage["min"] * self.skill_parent.outer_ring_multiplier,
                        "max": damage["max"] * self.skill_parent.outer_ring_multiplier,
                        "type": damage["type"]
                    }
                    damage_amount = random.randint(int(final_damage["min"]), int(final_damage["max"]))
                    enemy.take_damage(damage_amount)
                    # print(f"Ice Nova barrier dealt {damage_amount} {final_damage['type']} damage to {enemy.name}!")

                    # Apply super slow movement
                    enemy.apply_slow(
                        self.skill_parent.barrier_slow_percentage / 100,
                        self.skill_parent.barrier_slow_duration
                    )
                    # print(f"Ice Nova barrier applied super slow to {enemy.name}!")

        # Projectile blocking logic
        projectiles_to_remove = []
        for projectile in self.game.current_scene.projectiles:
            projectile_center = projectile.rect.center
            distance = math.hypot(self.position[0] - projectile_center[0], self.position[1] - projectile_center[1])
            if distance <= self.radius * 2:
                # Exclude ArcSkill projectiles from being blocked
                if isinstance(projectile, ArcProjectile):
                    continue # Do not block ArcProjectile
                print(f"Ice Nova barrier blocked projectile!")
                projectiles_to_remove.append(projectile)
        
        for projectile in projectiles_to_remove:
            projectile.kill() # Remove the projectile from all sprite groups