import pygame

_image_cache = {}

def load_image(path):
    if path not in _image_cache:
        try:
            image = pygame.image.load(path).convert_alpha()
            _image_cache[path] = image
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
            return None # Or a placeholder image
    return _image_cache[path]
