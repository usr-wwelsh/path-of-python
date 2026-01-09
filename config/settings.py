# Global Game Settings

# Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
RESOLUTIONS = [
  # Standard 4:3
    (800, 600),
    (1024, 768),
    (1152, 864),
    (1280, 960),
    (1400, 1050),
    (1600, 1200),
    
    # 5:4
    (1280, 1024),
    
    # 16:10
    (1280, 800),
    (1440, 900),
    (1680, 1050),
    (1920, 1200),
    (2560, 1600),
    
    # 16:9 (HD/FHD/QHD/UHD)
    (1280, 720),   # HD
    (1366, 768),
    (1600, 900),
    (1920, 1080),  # Full HD
    (2560, 1440),  # QHD/2K
    (3840, 2160),  # 4K UHD
    (7680, 4320),  # 8K UHD
    
    # 21:9 Ultrawide
    (2560, 1080),
    (3440, 1440),
    (3840, 1600),
    (5120, 2160),
    
    # Other common resolutions
    (320, 240),    # QVGA
    (640, 480),    # VGA
    (854, 480),    # FWVGA
    (960, 540),    # qHD
    (1280, 854),   # WXGA
    (1440, 960),
    (2048, 1152),
    (2560, 1080),
    (3200, 1800),  # QHD+
    (4096, 2160),  # 4K DCI
    (5120, 2880),  # 5K
    (6016, 3384),  # 6K
    (7680, 4320),  # 8K
    
    # Mobile/Tablet resolutions
    (720, 1280),
    (1080, 1920),
    (1440, 2560),
    (2160, 3840),
]
FPS = 60
CAPTION = "Path of Python"
FULLSCREEN = False
BORDERLESS = False
VSYNC = True

# Physics and Movement
PLAYER_SPEED = 200 # Pixels per second
TILE_SIZE = 32 # Size of each tile in pixels

# UI Appearance Settings
UI_FONT = "Arial"
UI_FONT_SIZE_DEFAULT = 24
UI_FONT_SIZE_SMALL = 18
UI_FONT_SIZE_LARGE = 32
UI_PRIMARY_COLOR = (200, 200, 200) # Light Gray
UI_SECONDARY_COLOR = (100, 100, 100) # Dark Gray
UI_ACCENT_COLOR = (255, 165, 0) # Orange
UI_BACKGROUND_COLOR = (30, 30, 30) # Dark Charcoal

# Debugging Settings
DEBUG_MODE = False
SHOW_FPS = True
SHOW_COLLISION_BOXES = False
SHOW_PATHFINDING = False
SHOW_PLAYER_COORDS = True # New debug flag
SHOW_SCENE_NAME = True # New debug flag
SHOW_DELTA_TIME = True # New debug flag
SHOW_PLAYER_TILE_COORDS = True # New debug flag

# Colors (RGB) - Common
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)