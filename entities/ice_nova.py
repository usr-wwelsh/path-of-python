import pygame
import math
import random
from config.constants import TILE_SIZE

class IceNovaSkill:
    def __init__(self, player):
        self.player = player
        self.game = player.game
        self.id = "ice_nova"
        self.name = "Ice Nova"
        self.description = "Unleashes a devastating ring of frost that expands outward, freezing enemies at the epicenter and chilling those further away."
        self.mana_cost = 15 + (player.level * 3)
        
        # Damage scales from 15-30 at level 1 to 3000 at level 100
        self.base_damage_min = 15
        self.base_damage_max = 30
        self.max_damage = 3000
        self.damage_type = "cold"
        
        self.cooldown = 0.5
        self.cast_time = 0.8
        self.max_radius = TILE_SIZE * 5
        self.expansion_speed = self.max_radius / 0.5
        
        # Freeze/chill effects
        self.freeze_duration = {"base": 1.5, "per_chill_stack": 0.2}
        self.chill_effect = {"slow_percentage": 30, "duration": 4.0}
        
        # Visual effects for initial nova
        self.particle_count = 120
        self.particle_speed = 200
        
        # Visual effects for additional blast
        self.second_blast_particle_count = 150  # More particles for a denser blast
        self.second_blast_expansion_speed = self.max_radius / 0.1  # Much faster
        self.second_blast_color = (100, 150, 200, 255)  # Darker blue, fully opaque
        
        # List to hold active nova instances
        self.active_novas = []
        
        # Damage scaling by distance
        self.inner_ring_multiplier = 1.5
        self.outer_ring_multiplier = 0.7

    def _calculate_damage(self):
        """Calculate damage based on player level, scaling linearly to max damage at level 100"""
        level_scale = min(1.0, self.player.level / 100.0)
        min_dmg = self.base_damage_min + (self.max_damage - self.base_damage_min) * level_scale
        max_dmg = self.base_damage_max + (self.max_damage - self.base_damage_max) * level_scale
        return {"min": min_dmg, "max": max_dmg, "type": self.damage_type}

    def can_cast(self):
        if self.player.current_mana < self.mana_cost:
            print("Not enough mana for Ice Nova!")
            return False
        return True

    def activate(self):
        if not self.can_cast():
            return
        print(f"IceNovaSkill.activate() called.")
        self.player.current_mana -= self.mana_cost # Deduct mana here
        new_nova = _NovaInstance(self.player, self.game, self) # Pass self (IceNovaSkill) for access to particle creation methods
        self.active_novas.append(new_nova)
        print(f"Player activated Ice Nova! Mana remaining: {self.player.current_mana}")

    def _create_particle_image(self):
        """Create a frost particle image"""
        size = random.randint(5, 15)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Make the initial nova more interesting:
        # Use a gradient or multiple circles for a more complex look
        # For simplicity, let's add a slight glow effect by drawing multiple circles
        for _ in range(3):
            alpha = random.randint(50, 150)
            color = (200, 230, 255, alpha)
            pygame.draw.circle(surf, color, (size//2, size//2), size//2 - _*2)
        return surf

    def _create_second_blast_particle_image(self):
        """Create a darker frost particle image for the second blast"""
        size = random.randint(7, 20)  # Slightly larger particles
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = self.second_blast_color
        pygame.draw.circle(surf, color, (size//2, size//2), size//2)
        return surf

    def update(self, dt):
        novas_to_remove = []
        for nova in self.active_novas:
            nova.update(dt)
            if nova.is_complete: # _NovaInstance will set this when its animation is done
                novas_to_remove.append(nova)
        
        for nova in novas_to_remove:
            self.active_novas.remove(nova)

    def remove_particles(self, sprite_group):
        """Remove particles from a specific sprite group from the scene"""
        for particle in sprite_group:
            self.game.current_scene.effects.remove(particle)
        sprite_group.empty()


class _NovaInstance:
    def __init__(self, player, game, skill_parent):
        self.player = player
        self.game = game
        self.skill_parent = skill_parent # Reference to IceNovaSkill for shared properties/methods

        self.max_radius = skill_parent.max_radius
        self.expansion_speed = skill_parent.expansion_speed
        self.particle_count = skill_parent.particle_count
        self.second_blast_particle_count = skill_parent.second_blast_particle_count
        self.second_blast_expansion_speed = skill_parent.second_blast_expansion_speed

        self.current_radius = 0
        self.is_casting = True # Initial nova is casting
        self.cast_start_time = pygame.time.get_ticks()
        self.nova_sprites = pygame.sprite.Group()
        
        self.is_second_blast_active = False
        self.second_blast_current_radius = 0
        self.second_blast_start_time = 0
        self.second_blast_sprites = pygame.sprite.Group()

        self.is_complete = False # Flag to indicate when this nova instance is done

        # Create initial visual effect particles
        for i in range(self.particle_count):
            particle = pygame.sprite.Sprite()
            particle.image = self.skill_parent._create_particle_image()
            particle.rect = particle.image.get_rect(center=self.player.rect.center)
            particle.angle = (360 / self.particle_count) * i
            particle.distance = 0
            self.nova_sprites.add(particle)
            self.game.current_scene.effects.add(particle)

    def _activate_second_blast(self):
        print("Activating second blast for this nova instance!")
        self.is_second_blast_active = True
        self.second_blast_start_time = pygame.time.get_ticks()
        self.second_blast_current_radius = 0
        self.skill_parent.remove_particles(self.nova_sprites) # Remove initial nova particles for THIS instance

        for i in range(self.second_blast_particle_count):
            particle = pygame.sprite.Sprite()
            particle.image = self.skill_parent._create_second_blast_particle_image()
            particle.rect = particle.image.get_rect(center=self.player.rect.center)
            particle.angle = (360 / self.second_blast_particle_count) * i
            particle.distance = 0
            self.second_blast_sprites.add(particle)
            self.game.current_scene.effects.add(particle)

    def _update_second_blast(self, dt):
        if not self.is_second_blast_active:
            return

        self.second_blast_current_radius = min(self.max_radius, self.second_blast_current_radius + self.second_blast_expansion_speed * dt)

        for particle in self.second_blast_sprites:
            particle.distance = self.second_blast_current_radius
            rad_angle = math.radians(particle.angle)
            offset_x = particle.distance * math.cos(rad_angle)
            offset_y = particle.distance * math.sin(rad_angle)
            particle.rect.center = (
                self.player.rect.centerx + offset_x,
                self.player.rect.centery + offset_y
            )
        
        if self.second_blast_current_radius >= self.max_radius:
            self.is_second_blast_active = False
            self.is_complete = True # Mark this nova instance as complete
            self.skill_parent.remove_particles(self.second_blast_sprites) # Remove second blast particles immediately

    def update(self, dt):
        if self.is_casting:
            current_time = pygame.time.get_ticks()
            
            # Expand nova radius
            self.current_radius = min(self.max_radius, self.current_radius + self.expansion_speed * dt)
            
            # Update particle positions
            for particle in self.nova_sprites:
                particle.distance = self.current_radius
                rad_angle = math.radians(particle.angle)
                offset_x = particle.distance * math.cos(rad_angle)
                offset_y = particle.distance * math.sin(rad_angle)
                particle.rect.center = (
                    self.player.rect.centerx + offset_x,
                    self.player.rect.centery + offset_y
                )
            
            # Check for hit at max radius
            if self.current_radius >= self.max_radius:
                self._perform_hit()
                self.is_casting = False
                self._activate_second_blast() # Activate the second blast here
        
        self._update_second_blast(dt) # Update the second blast regardless of initial casting state

    def _perform_hit(self):
        damage = self.skill_parent._calculate_damage() # Use skill_parent's damage calculation
        hit_enemies = []
        player_center = self.player.rect.center
        
        # Projectile blocking logic
        for projectile in self.game.current_scene.projectiles:
            projectile_center = projectile.rect.center
            distance = math.hypot(player_center[0] - projectile_center[0], player_center[1] - projectile_center[1])
            if distance <= self.max_radius:
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