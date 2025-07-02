import pygame
import os
import random

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, width, height, color, name="NPC", dialogue_id=None, sprite=None):
        super().__init__()
        self.game = game
        self.name = name
        self.dialogue_id = dialogue_id
        self.in_dialogue = False

        # Define sprite paths
        yaktaur_path_base = os.path.join(os.getcwd(), "graphics", "dc-mon")
        sprite_path = None
        
        if self.name == "Billy Bob" and sprite:
            sprite_path = os.path.join(os.getcwd(), sprite)
        elif self.name == "Bob the Bold":
            sprite_filename = "stone_giant.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        elif self.name == "Alice the Agile":
            sprite_filename = "deep_elf_mage.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        elif self.name == "Charlie the Calm":
            sprite_filename = "deformed_elf.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        elif self.name == "Charlie2":
            sprite_filename = "deformed_elf.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        elif self.name == "archivist":
            sprite_filename = "archivist.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        elif self.name == "Maze Wanderer":
            sprite_filename = "deep_elf_sorcerer.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        else:
            # Load random merfolk sprite for other NPCs
            merfolk_path_base = os.path.join(os.getcwd(), "graphics", "dc-mon", "cult")
            merfolk_sprites = [
                "1.png",
                "2.png",
                "3.png",
                "4.png",
            ]
            sprite_filename = random.choice(merfolk_sprites)
            sprite_path = os.path.join(merfolk_path_base, sprite_filename)

        if os.path.exists(sprite_path):
            self.image = pygame.image.load(sprite_path).convert_alpha()
            if self.name == "archivist":
                width *= 4
                height *= 4
            elif not (self.name == "Billy Bob" and sprite): # Check if it's NOT Billy Bob
                if "cult" in sprite_path: # Check if it's a merfolk sprite
                    width *= 2
                    height *= 2
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            # Fallback to colored rectangle if sprite not found
            self.image = pygame.Surface((width, height))
            self.image.fill(color)

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        # NPCs might have idle animations or simple movement patterns
        pass
    def draw(self, screen, camera_x, camera_y, zoom_level):
        # Adjust position based on camera and zoom
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
        scaled_rect = scaled_image.get_rect(topleft=(int((self.rect.x - camera_x) * zoom_level), int((self.rect.y - camera_y) * zoom_level)))
        screen.blit(scaled_image, scaled_rect)

    def interact(self, player):
        # Placeholder for interaction logic (e.g., open dialogue, quest, shop)
        if self.dialogue_id:
            self.in_dialogue = True
            self.game.dialogue_manager.start_dialogue(self.dialogue_id)
        # In a real game, this would trigger a dialogue UI