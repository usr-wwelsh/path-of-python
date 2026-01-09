import pygame
import json
from core.new_dungeon_generator import translate_tile_type
from utility.resource_path import resource_path

# Cache for missing texture placeholder
_missing_texture_cache = None

def get_missing_texture(tile_size=32):
    """Create a placeholder texture for missing assets."""
    global _missing_texture_cache
    if _missing_texture_cache is None:
        # Create a magenta/black checkerboard pattern (classic missing texture)
        surface = pygame.Surface((tile_size, tile_size))
        half = tile_size // 2
        # Top-left and bottom-right: magenta
        pygame.draw.rect(surface, (255, 0, 255), (0, 0, half, half))
        pygame.draw.rect(surface, (255, 0, 255), (half, half, half, half))
        # Top-right and bottom-left: black
        pygame.draw.rect(surface, (0, 0, 0), (half, 0, half, half))
        pygame.draw.rect(surface, (0, 0, 0), (0, half, half, half))
        _missing_texture_cache = surface
    return _missing_texture_cache

def render_dungeon_pygame(dungeon_data, zoom_scale):
    width = dungeon_data['width']
    height = dungeon_data['height']
    tile_map = dungeon_data['tile_map']
    tileset_name = dungeon_data['tileset']

    # Load tileset
    tileset_path = resource_path(f'data/tilesets/{tileset_name}_tileset.json')
    with open(resource_path('data/tileset_mappings.json'), 'r') as f:
        tileset_mappings = json.load(f)
    tileset_mapping = tileset_mappings.get(tileset_name, tileset_mappings['default'])
    tileset = {}
    with open(tileset_path, 'r') as f:
        tileset_data = json.load(f)

    for tile_name, tile_path in tileset_data.items():
        try:
            tile_image = pygame.image.load(resource_path(tile_path)).convert_alpha()
            tileset[tile_name] = tile_image
        except FileNotFoundError:
            print(f"Warning: Missing texture '{tile_path}', using placeholder")
            tileset[tile_name] = get_missing_texture()

    # Create a Pygame surface
    tile_size = 32  # Assuming each tile is 32x32 pixels
    surface_width = width * tile_size
    surface_height = height * tile_size
    dungeon_surface = pygame.Surface((surface_width, surface_height))

    # Draw the tile map on the surface
    for y in range(height):
        for x in range(width):
            tile_type = tile_map[y][x]
            tile_name = translate_tile_type(tile_type, tileset_mapping)
            tile = tileset.get(tile_name)
            if tile:
                dungeon_surface.blit(tile, (x * tile_size, y * tile_size))
            else:
                print(f"Tile not found: {tile_name}")

    # Scale the surface
    scaled_width = int(surface_width * zoom_scale)
    scaled_height = int(surface_height * zoom_scale)
    scaled_surface = pygame.transform.scale(dungeon_surface, (scaled_width, scaled_height))
    
    return scaled_surface