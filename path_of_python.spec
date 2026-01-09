# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Path of Python game.

This spec file bundles the game into a single executable with all resources.
Run with: pyinstaller path_of_python.spec
"""

block_cipher = None

# Collect all data files that need to be bundled
data_files = [
    ('data', 'data'),           # JSON files, audio, etc.
    ('graphics', 'graphics'),   # All graphics assets
    ('config', 'config'),       # Configuration files
    ('icon.ico', '.'),          # Window icon file
]

# Explicitly list all modules that are dynamically imported
# This ensures PyInstaller includes them even though they're loaded via strings
hiddenimports = [
    # Core modules
    'core.game_engine',
    'core.scene_manager',
    'core.music_manager',
    'core.utils',
    'core.input_handler',
    'core.spawn_town',
    'core.CharacterSelectionScene',
    'core.base_gameplay_scene',
    'core.IntroScene',
    'core.swamp_cave_dungeon',
    'core.quest_001_scene',
    'core.pathfinding',
    'core.animated_cursor',
    'core.boss_system_manager',
    'core.new_dungeon_generator',

    # Dungeon scenes (dynamically loaded from scenes.json)
    'core.dungeons.tower1',
    'core.dungeons.tower2',
    'core.dungeons.tower3',
    'core.dungeons.tower4',
    'core.dungeons.final_sanctum',
    'core.dungeons.grass',
    'core.dungeons.arena',
    'core.dungeons.arena2',
    'core.dungeons.arena3',
    'core.dungeons.noobzone',
    'core.dungeons.funz',
    'core.dungeons.UltraDungeon',
    'core.dungeons.hallway',
    'core.dungeons.maze',
    'core.dungeons.third',
    'core.dungeons.bot',
    'core.dungeons.flesh_lab',
    'core.dungeons.neural_cathedral',
    'core.dungeons.vault',
    'core.dungeons.firewall',
    'core.dungeons.feast_hall',
    'core.dungeons.feast_hall2',
    'core.dungeons.feast_hall3',
    'core.dungeons.feast_hall4',
    'core.dungeons.data_maw',
    'core.dungeons.broadcast_tower',
    'core.quest_001_scene',
    'core.boss_scenes.boss_room_scene',
    'world.zone',

    # UI modules
    'ui.title_screen',
    'ui.settings_menu',
    'ui.button',
    'ui.dropdown',
    'ui.hud',
    'ui.inventory_screen',
    'ui.paste_tree_screen',
    'ui.dialogue_manager',
    'ui.developer_inventory_screen',
    'ui.loading_screen',
    'ui.loading_overlay',
    'ui.menus',
    'ui.flesh_algorithm_terminal',
    'ui.teleporter_menu',
    'ui.level_up_screen',
    'ui.save_menu',
    'ui.skill_tree_ui',
    'ui.shop_window',
    'ui.dungeon_display',
    'ui.dungeon_renderer',

    # Entities
    'entities.player',
    'entities.npc',
    'entities.enemy',
    'entities.paste',
    'entities.projectile',
    'entities.boss_portal',
    'entities.effects',
    'entities.player_sprites',
    'entities.arc_skill',
    'entities.cleave_skill',
    'entities.cyclone_skill',
    'entities.fireball_skill',
    'entities.ice_nova',
    'entities.necrotic_plague',
    'entities.singularity_core',
    'entities.summon_skeletons',
    'entities.summon_spiders',
    'entities.web_effect',

    # Combat
    'combat.enemy_factory',
    'combat.skills',
    'combat.skill_gems',
    'combat.damage_calc',
    'combat.status_effects',

    # Progression
    'progression.quests',
    'progression.quest_tracker',

    # Items
    'items.item_factory',
    'items.item',
    'items.weapon',
    'items.armor',
    'items.potion',
    'items.gem',
    'items.inventory',
    'items.loot_generator',

    # World
    'world.zone',
    'world.environment',
    'world.map_generator',
    'world.world_state',

    # Utility
    'utility.font_cache',
    'utility.resource_path',
    'utility.image_cache',

    # Config
    'config.settings',
    'config.constants',

    # Pygame and dependencies
    'pygame',
    'pygame.mixer',
    'pygame.font',
    'pygame.image',
    'pygame.display',
    'pygame.event',
    'pygame.time',
    'pygame.draw',
    'pygame.transform',
    'pygame.rect',
    'pygame.sprite',
    'pygame.surface',
    'pygame.locals',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test modules and unnecessary packages to reduce size
        'tests',
        'pytest',
        'unittest',
        'tkinter',
        '_tkinter',
        'matplotlib',
        'numpy.random._examples',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PathOfPython',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX to reduce size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True for debugging, False for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Game icon for the executable
)
