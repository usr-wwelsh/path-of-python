import sys
sys.setrecursionlimit(5000)
import pygame
import json
import os
from entities.enemy import Enemy

class EnemyFactory:
    def __init__(self, game):
        self.game = game
        self.enemy_configs = self._load_enemy_configs()

    def _load_enemy_configs(self):
        enemy_config_path = os.path.join(os.getcwd(), "data", "enemy_data.json")
        try:
            with open(enemy_config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading enemy configuration from {enemy_config_path}: {e}")
            return {}

    def create_enemy(self, enemy_type, x, y):
        config = self.enemy_configs.get(enemy_type)

        if not config:
            print(f"Warning: No config found for enemy type: {enemy_type}")
            return None

        health = config.get('health', 10)
        damage = config.get('damage', 1)
        speed = config.get('speed', 50)
        sprite_path = config.get('sprite_path', 'graphics/dc-mon/misc/demon_small.png')
        attack_range = config.get('attack_range', 0)
        attack_cooldown = config.get('attack_cooldown', 0)
        projectile_sprite_path = config.get('projectile_sprite_path')
        ranged_attack_pattern = config.get('ranged_attack_pattern', 'single')
        xp_value = config.get('xp_value', 0)
        scale_factor = config.get('scale_factor', 1.0)
        
        # New spawning attributes
        spawn_on_cooldown = config.get('spawn_on_cooldown', False)
        spawn_cooldown = config.get('spawn_cooldown', 0)
        enemies_to_spawn = config.get('enemies_to_spawn', [])
        max_spawned_enemies = config.get('max_spawned_enemies', 0)

        enemy = Enemy(
            self.game,
            x,
            y,
            enemy_type,
            health,
            damage,
            speed,
            sprite_path,
            attack_range,
            attack_cooldown,
            projectile_sprite_path,
            ranged_attack_pattern,
            xp_value=xp_value,
            scale_factor=scale_factor
        )
        
        # Assign spawning attributes if applicable
        enemy.spawn_on_cooldown = spawn_on_cooldown
        enemy.spawn_cooldown = spawn_cooldown
        enemy.enemies_to_spawn = enemies_to_spawn
        enemy.max_spawned_enemies = max_spawned_enemies
        enemy.last_spawn_time = pygame.time.get_ticks()

        return enemy