# AGENTS.md - Path of Python Development Guidelines

This document provides guidelines for AI agents working on the Path of Python codebase.

## Build & Run Commands

```bash
# Install dependencies
pip install pygame noise

# Run the game (development mode with loading screen)
python main.py

# Run without loading screen (faster startup)
python main.py -dev

# Profile the game (generates profile_output.prof)
python -m cProfile -o profile_output.prof main.py
python read_profile.py  # Read the profiling results

# Mouse control test
python mouse_test.py

# Skill test
python skill_test.py

# Check image paths
python check_image_paths.py
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_loot_gen.py -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing
```

## Code Style Guidelines

### Import Organization
- Standard library imports first
- Third-party imports (pygame, noise) second
- Local application imports third
- Use absolute imports from project root
- Example:
```python
import sys
import os
import pygame
import noise
from config.constants import TILE_SIZE
from core.game_engine import GameEngine
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `GameEngine`, `Player`, `Inventory`)
- **Functions/Variables**: snake_case (e.g., `calculate_distance`, `current_life`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `TILE_SIZE`, `PLAYER_SPEED`)
- **Private Methods/Attributes**: Leading underscore (e.g., `_execute_skill`, `_internal_state`)
- **Module-level constants**: UPPER_SNAKE_CASE in all caps

### Type Annotations
- Use type hints for function parameters and return values where beneficial
- Use `Optional[Type]` instead of `Union[Type, None]`
- Use `List[Type]`, `Dict[KeyType, ValueType]` from typing module
- Example:
```python
from typing import Optional, List, Dict

def get_item_quantity(self, item_id: str) -> int:
    ...
```

### Error Handling
- Use try/except for file I/O and external resource loading
- Provide meaningful error messages with print() for user-facing errors
- Use logging module for game engine errors (logging.getLogger)
- Return None or False with print message for recoverable errors
- Raise NotImplementedError for abstract methods
- Example:
```python
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
except FileNotFoundError:
    print(f"Error: File not found at {filepath}")
    return None
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {filepath}")
    return None
```

### Documentation
- Use docstrings for all public classes and functions
- Follow Google-style docstrings:
```python
def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculates the distance between two points.

    Args:
        point1: First point as (x, y) tuple
        point2: Second point as (x, y) tuple

    Returns:
        Euclidean distance between the two points
    """
```
- Use inline comments for complex logic only

### Code Structure
- Keep functions focused (single responsibility)
- Maximum ~100 lines per function preferred
- Use private methods for internal logic (leading underscore)
- Initialize instance attributes in __init__
- Use pygame.math.Vector2 for vector math operations
- Use pygame.sprite.Sprite for game entities

### UI/Game Development
- Constants for all magic numbers (colors, sizes, speeds)
- Use config/constants.py and config/settings.py for global constants
- Use utility/font_cache.py and utility/image_cache.py for resource caching
- Store game data in JSON files in data/ directory
- Store graphics in graphics/ directory organized by type

### File Organization
- **core/**: Core game engine, scenes, and systems
- **ui/**: User interface components (menus, screens, HUD)
- **combat/**: Combat mechanics, skills, status effects
- **items/**: Item system, inventory, loot generation
- **world/**: Map generation, zones, environment
- **entities/**: Game entities (player, enemies, projectiles)
- **progression/**: Quests, skill trees, paste tree
- **config/**: Settings and constants
- **utility/**: Helper utilities (fonts, images, licenses)
- **graphics/**: Sprites and visual assets
- **data/**: JSON data files (quests, scenes, zones)

### Pygame Patterns
- Initialize pygame at application start: `pygame.init()`
- Use pygame.time.Clock for frame rate control
- Hide system cursor: `pygame.mouse.set_visible(False)`
- Use sprite groups for entity management
- Load images with convert_alpha() for performance
- Use SRCALPHA for surfaces needing transparency

### Common Patterns
- GameEngine singleton pattern for global access
- SceneManager for scene transitions
- InputHandler for input processing
- Resource caching (FontCache, ImageCache)
- JSON-based data loading for quests, scenes, zones
