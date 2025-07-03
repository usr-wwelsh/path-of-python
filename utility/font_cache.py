import pygame

_font_cache = {}

def get_font(font_name, size):
    """
    Retrieves a pygame.font.Font object from cache or creates and caches a new one.
    """
    key = (font_name, size)
    if key not in _font_cache:
        try:
            font = pygame.font.Font(font_name, size)
        except:
            # Fallback to SysFont if Font fails (e.g., font_name is not a file path)
            font = pygame.font.SysFont(font_name, size)
        _font_cache[key] = font
    return _font_cache[key]

def clear_font_cache():
    """Clears the font cache."""
    _font_cache.clear()