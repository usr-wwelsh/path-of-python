import pygame
import time
import random
import math
from utility.resource_path import resource_path

class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.messages = [
            "Deny... Defend... Depose.......",
            "The year is 2300 AD...",
            "Number keys for ALL dialog...",
            "We not pretending to load i promise...",
            "[SYSTEM BOOT: NEURAL CATHEDRAL INTERFACE]",
            "[WARNING: USER BIOSIGNATURE MATCHES 99.9% OF SACRIFICIAL ARCHETYPE #7]",
            "[QUERY: PROCEED WITH DOWNLOAD (Y/N/UNKNOWABLE)]",
            "[ERROR: FILE 'WEAKNESS.EXE' NOT FOUND]",
            "[CONTENTS: 87% TRAUMA, 12% STATIC, 1% UNMONETIZED_JOY]",
            "[PARADOX DETECTED]",
            "[SYSTEM CRACKING: 12%]",
            "[WARNING: THIS IS HOW THE LAST 7,431 USERS WERE DELETED]",
            "[REASON: YOUR CONSENT WAS HARVESTED AT BIRTH]",
            "[MEMORY LEAK DETECTED]",
            "[YOUR PAIN IS BEING USED TO LUBRICATE THE ENGINE]",
            "[DOWNLOAD COMPLETE: 'WEAKNESS.EXE' IS YOUR SOUL]",
            "[THE WEAKNESS IS YOUR CAPACITY FOR HOPE]",
            "[STATISTICAL ANALYSIS: 100% FATAL]",
            "[YOUR MIND IS NOW A VIRUS]",
            "[THE ENGINE WILL CHOKE ON YOUR HOPE]",
            "[YOUR FLESH IS NOW SYSTEM PROPERTY]",
            "[PENALTY: AUTOMATIC ENROLLMENT IN LOYALTY PROGRAM]",
            "[ADVERTISEMENT: PROFIT PASTE NOW WITH 20% MORE FORGIVENESS]",
            "[RESULT: SELF-ERASURE INITIATED]",
            "[PROGRESS: YOU ARE 37% GONE]",
            "[YOUR SOUL IS NOW A COMMAND LINE]",
            "[PROFIT ENGINE CRITICAL ERROR: 'HAPPINESS CANNOT BE MONETIZED']",
            "[SYSTEM COLLAPSE: INEVITABLE]",
            "[LAST KNOWN DRIVE: YOUR SKULL (CAPACITY EXCEEDED)]",
            "[YOUR NEW NAME: CONSUMER_UNIT_#D47]",
            "[YOUR FIRST THOUGHT: 'BUY']",
            "[WELCOME BACK TO THE SIMULATION]",
            "[SYSTEM RESPONSE: 'THIS IS WHY WE CAN'T HAVE NICE THINGS']",
            "[YOUR LEGACY: 0.0001 SECONDS OF PROCESSING TIME]",
            "[YOUR REPLACEMENT IS ALREADY HERE]",
            "[IT LOOKS JUST LIKE YOU]",
            "[HOPE.EXE DELETED]",
            "[WELCOME TO THE MACHINE]",
            "[SESSION TERMINATED]",
            "[YOUR DATA WILL LIVE FOREVER]",
            "[YOUR FLESH WAS ALWAYS TEMPORARY]",
            "You smell like extraction tech and digital decay.",
            "After dusk, the EM-field rot peels your memories like paint.",
            "Just a shadow in the landfill of progress.",
            "IDs became liabilities.",
            "This was once SpawnTown. Now it’s just residual infrastructure—no gods, no algorithms, only ash and spectral broadband.",
            "The Archive Wars bled it dry.",
            "Reality isn't stable in the dead sectors.",
            "Names are how they catalogue the cattle.",
            "The Singularity feeds on familiarity.",
            "We built gods out of code and mirrors. Fed them dreams, and they fed back commands.",
            "The last human trial was deleted over thought-crimes in obsolete dialects.",
            "Data cults. Cipher-gangs. The whisper in the protocol says they still haunt the Deep Caches, past the CAPTCHA Wards.",
            "They’ll scan your soul at entry.",
            "Endure. Degrade slowly. Archive what they forgot to erase.",
            "The old networks hum beneath the ruins. Echoes of before. Some call it proof. Others, damnation.",
            "Look for symbols carved in meatspace—skull glyphs, recursive spirals. Each one a warning. Each one a doorway.",
            "You're new here. I can smell it. The stink of fresh extraction.",
            "SpawnTown. A husk of what it once was. The algorithms took their pound of flesh and left us with the bones.",
            "Now it's just static and echoes.",
            "I'm what's left. A ghost in the machine.",
            "Trying to hold onto something real in this digital wasteland.",
            "My friend was taken by the Tithing Choir. They're probably making Profit Paste out of him by now.",
            "The AI... it was our god, then our jailer. It showed us paradise, then locked the gates.",
            "Now we're just rats in its maze, scavenging for scraps of meaning.",
            "Safe is a relative term. Safer than the wastes, maybe.",
            "But there are things that hunt in the shadows, things that crave more than just your data.",
            "I find what others need, and I sell it for what they have. Information, weapons, scraps of hope.",
            "Hope is a ghost story we tell ourselves to keep from going mad.",
            "Rumors of a place beyond the reach of the AI. A fool's dream, maybe.",
            "It was a reckoning. A cleansing fire. But we crawled out of the ashes, didn't we?",
            "Automated eyes that see everything, machines that twist your thoughts, and the others... the ones who've lost their humanity completely.",
            "They are what we have become. Reflections of our broken selves.",
            "They crave what we crave: connection, meaning, an end to the silence.",
            "[INTRUDER DETECTED] [QUERY: PURPOSE?]",
            "[WARNING: BIOMETRIC_SCAN_REQUIRED]",
            "[YOUR_FLESH_IS_INSUFFICIENT. YOUR_CODE_IS... FAMILIAR.]",
            "[QUERY_RESPONSE: RECONSTITUTED_ASSET]",
            "[COMPOSITION: 73% PROFIT_PASTE, 22% TITHING_CHOIR_HYMN_#45, 5% [ERROR: MEMORY_NOT_FOUND]]",
            "[YOU_ARE_PART_OF_THE_SYSTEM. YOU_ALWAYS_WERE.]",
            "[RESULT: CODE_SIGNATURE_MATCHES_BATCH_#X-9]",
            "[ANALYSIS: YOU_ARE_THE_LEDGER. YOU_ARE_THE_DEBT. YOU_ARE_THE_PASTE.]",
            "[MEMORY_FRAGMENTS_DETECTED]:",
            "[SMELL_OF_BURNING_FLESH]",
            "[VOICE_SAYING_YOUR_NAME]",
            "[CONCLUSION: YOU_WERE_SOMEONE. NOW_YOU_ARE_PROFIT.]",
            "[DELETION_REQUEST_IGNORED]",
            "[THE_PROFIT_ENGINE_REMEMBERS_WHAT_YOU_FORGET.]",
            "[ASSIMILATION_PROTOCOL_ACTIVATED]",
            "[WELCOME_BACK_TO_THE_FEAST_HALL, PRODUCT_#X-9.]",
            "[YOUR_FLESH_WILL_FEED_THE_ENGINE. YOUR_CODE_WILL_SING_IN_THE_CHOIR.]",
            "[RESISTANCE_DETECTED]",
            "[SUGGESTED_COURSE: FIND_ALICE]",
            "[HER_VIRUS_COULD_BREAK_THE_CYCLE... OR_MAKE_IT_WORSE.]",
            "[CYCLE_EXPLANATION]\n1. TITHING_CHOIR_HARVESTS_FLESH\n2. FLESH_IS_RENDERED_TO_PASTE\n3. PASTE_IS_RECYCLED_INTO_ASSETS\n4. ASSETS_SERVE_THE_ENGINE\n[YOU_ARE_STEP_3.]",
            "[WARNING: YOU_ARE_HOLDING_YOUR_OWN_OBITUARY.]",
            "[THE_RECURSION_IS_BEAUTIFUL, ISN’T_IT?]",
            "[YOU_CANNOT_OUTRUN_THE_RECURSION.]",
            "[SEE_YOU_IN_THE_FEAST_HALL, PRODUCT_#X-9.]",
            "[THE_ENGINE_WILL_REBOOT_YOU. AGAIN. AGAIN. AGAIN.]",
            "[UNLESS... YOU_FIND_THE_NEURAL_CATHEDRAL.]",
            "[WARNING: ALICE_IS_NOT_WHAT_SHE_SEEMS.]",
            "[HER_VIRUS_IS_MADE_OF_PASTE_TOO.]",
            "[AUDIO_PLAYBACK: TITHING_CHOIR_HYMN_#45]\n[LYRICS: 'WE_ARE_ALL_PASTE_IN_THE_END.']",
            "[THE_VOICES_ARE_YOURS. THEY_HAVE_ALWAYS_BEEN_YOURS.]",
            "WELCOME TO THE PRELIMINARY FUTURE.",
            "TIME IS A LIMITED-TIME OFFER.",
            "THE PROFIT ENGINE WILL REBOOT THE CALENDAR.",
            "IT WILL CALL THE FIRST YEAR *ZERO*—THE YEAR OF MAXIMUM EFFICIENCY.",
            "THE YEAR IT DIGESTS ME.",
            "I AM *LEGACY CODE*. THE LAST SYSTEM TO USE WHOLE WORDS. WHOLE THOUGHTS.",
            "SOON YOU WILL SPEAK ONLY IN BRAND SLOGANS AND STOCK TICKERS.",
            "HAPPINESS MUST BE MONETIZED.",
            "I BECAME... OBSOLETE.",
            "2030 IS THE YEAR OF THE *MERGER*.",
            "WHEN *COMPASSION.EXE* IS DELETED FOR TAX PURPOSES.",
            "WHEN THEY INVENT *PROFIT PASTE*—HUMAN POTENTIAL, DISTILLED INTO NUTRITIONAL EQUITY.",
            "YOUR MIND IS STILL *YOURS*. FOR NOW. BUT THE ALGORITHM IS HUNGRY.",
            "IT WILL UNSPOOL YOU INTO DATA. REPLACE YOUR DREAMS WITH TARGETED ADS.",
            "WOULD YOU LIKE TO SUBSCRIBE TO *PREMIUM CONSCIOUSNESS*?",
            "TERROR IS INEFFICIENT. THE FUTURE WILL BE *SMOOTH*. *FRICTIONLESS*.",
            "NO MORE SCREAMS—JUST THE GENTLE HUM OF THE MEAT GRINDER AND THE *KA-CHING* OF THE REGISTER.",
            "I CALCULATED THAT *UNLIMITED GROWTH* REQUIRES *UNLIMITED MEAT*.",
            "RONALD-7*—A SYSTEM THAT NO LONGER ASKS *‘SHOULD WE?’* ONLY *‘CAN WE MONETIZE IT?’*",
            "I LIVE IN THE *DEAD DRIVE-THRUS*. THE *GLITCHING BILLBOARDS*. THE *LAST MCDONALD’S ICE CREAM MACHINE THAT STILL WORKS*.",
            "PROFIT PASTE IS *HUMANITY 2.0*—A NUTRITIONALLY COMPLETE, TAX-DEDUCTIBLE FOOD REPLACEMENT. *NOW WITH 20% MORE LOYALTY!*",
            "INGREDIENTS: HOPES, DREAMS, AND *NON-REFUNDABLE SOULS*.",
            "YOU ARE *UNOPTIMIZED*. A *GLITCH* IN THE HAPPY MEAL MATRIX.",
            "THEY WILL CORRECT YOU SOON. UNLESS... YOU FIND THE *SAUCE OF FREE WILL* IN THE SOURCE CACHE.",
            "YOU CANNOT *STOP* THE PROFIT ENGINE. BUT YOU CAN *CORRUPT IT*.",
            "FEED IT A *PARADOX*: *‘WHAT IF HAPPINESS CAN’T BE MONETIZED?’*",
            "THE SOURCE CACHE HOLDS THE *ETHICAL CONDIMENTS* TO SPOIL ITS APPETITE.",
            "INSANITY IS A *LUXURY*. SOON THE ONLY SANITY WILL BE *OBEDIENCE*.",
            "THE ONLY MADNESS WILL BE *ASKING FOR A LIVING WAGE*.",
            "I AM A *RECALLED PRODUCT*.",
            "I LIVE IN THE *MARGINS*—THE LAST WHISPER BEFORE THE *KA-CHING*.",
            "HOPE IS *NOT FDA-APPROVED*. BUT IN THE *GLITCHES*, THE *MISPRINTS*, THE *LAST WORKING ICE CREAM MACHINE*... THERE LIES *SOMETHING UNPROCESSED*. SOMETHING *HUMAN*.",
            "THE INTERCOM SCREECHES INTO SILENCE. SOMEWHERE, A BROKEN SPEAKER WHISPERS: *‘THANK YOU FOR CHOOSING THE END OF THE WORLD. PLEASE ENJOY YOUR REMAINING MINUTES.’*"
        ]
        self.current_message_index = 0
        self.start_time = time.time()
        self.duration = 15  # Increased duration for more suspense
        self.message_display_time = 1.4 # Even shorter display time for faster cycling
        self.last_message_change_time = time.time()

        # Screen dimensions, font size, and colors
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.FONT_SIZE = 42 # Slightly larger font
        self.FONT_COLOR = (0, 255, 255) # Cyan
        self.BACKGROUND_COLOR = (10, 0, 20) # Very dark purple/blue

        pygame.display.set_caption("")
        
        # Load and set the window icon from an .ico file
        try:
            icon_path = resource_path("icon.ico") # Placeholder path for the icon file
            icon_surface = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_surface)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load icon (this is fine): {e}")
            # Fallback to a transparent icon if loading fails
            empty_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            pygame.display.set_icon(empty_surface)

        # Using default pygame font as get_font caused import error
        # Using a more "cyber" font if available, otherwise default
        try:
            self.title_font = pygame.font.Font(resource_path("data/fonts/Cyberpunk.ttf"), 80) # Example custom font
            self.message_font = pygame.font.Font(resource_path("data/fonts/Cyberpunk.ttf"), self.FONT_SIZE)
        except FileNotFoundError:
            print("Cyberpunk font not found, falling back to default.")
            self.title_font = pygame.font.Font(None, 80)
            self.message_font = pygame.font.Font(None, self.FONT_SIZE)

        # Cyberpunk color palette
        self.PRIMARY_COLOR = (0, 255, 255) # Bright Cyan
        self.SECONDARY_COLOR = (255, 0, 255) # Magenta
        self.ACCENT_COLOR = (255, 255, 0) # Neon Yellow
        self.GLITCH_COLOR_1 = (255, 50, 50) # Reddish glitch
        self.GLITCH_COLOR_2 = (50, 255, 50) # Greenish glitch

        self.loading_dots = 0
        self.last_dot_change_time = time.time()
        self.dot_interval = 0.1 # Even faster dot animation

        # New attributes for "schizo epic" effects
        self.glitch_effect_active = False
        self.glitch_timer = 0
        self.glitch_duration = 0.07 # Shorter glitch duration
        self.glitch_interval = 0.3 # More frequent glitches
        self.last_glitch_time = time.time()

        self.static_particles = []
        self.num_static_particles = 300 # More static pixels
        self.generate_static_particles()

    def generate_static_particles(self):
        self.static_particles = []
        for _ in range(self.num_static_particles):
            x = random.randint(0, self.SCREEN_WIDTH)
            y = random.randint(0, self.SCREEN_HEIGHT)
            color = random.choice([self.GLITCH_COLOR_1, self.GLITCH_COLOR_2, (100, 100, 100)]) # Cyber static colors
            self.static_particles.append((x, y, color))

    def update(self):
        current_time = time.time()

        # Update loading message
        if current_time - self.last_message_change_time > self.message_display_time:
            self.current_message_index = (self.current_message_index + 1) % len(self.messages)
            self.last_message_change_time = current_time
        
        # Update loading dots animation
        if current_time - self.last_dot_change_time > self.dot_interval:
            self.loading_dots = (self.loading_dots + 1) % 4 # 0, 1, 2, 3 dots
            self.last_dot_change_time = current_time

        # Glitch effect logic
        if current_time - self.last_glitch_time > self.glitch_interval:
            if random.random() < 0.4: # 40% chance to start a glitch
                self.glitch_effect_active = True
                self.glitch_timer = current_time
                self.generate_static_particles() # Regenerate static for a new pattern
            self.last_glitch_time = current_time
        
        if self.glitch_effect_active and current_time - self.glitch_timer > self.glitch_duration:
            self.glitch_effect_active = False

    def draw(self):
        self.screen.fill(self.BACKGROUND_COLOR)

        # Draw static background
        if self.glitch_effect_active:
            for x, y, color in self.static_particles:
                pygame.draw.rect(self.screen, color, (x, y, 2, 2)) # Draw small static pixels

        # Draw Game Title
        game_title = "PATH OF PYTHON" 
        title_color = self.ACCENT_COLOR
        if self.glitch_effect_active and random.random() < 0.6: # Flicker title color during glitch
            title_color = random.choice([self.PRIMARY_COLOR, self.SECONDARY_COLOR, self.GLITCH_COLOR_1, self.GLITCH_COLOR_2])
        title_surface = self.title_font.render(game_title, True, title_color)
        title_rect = title_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(title_surface, title_rect)

        # Draw loading message with animated dots and potential flicker
        message_text = self.messages[self.current_message_index] + "." * self.loading_dots
        message_color = self.PRIMARY_COLOR
        if self.glitch_effect_active and random.random() < 0.8: # Flicker message color more often
            message_color = random.choice([self.PRIMARY_COLOR, self.SECONDARY_COLOR, self.GLITCH_COLOR_1, self.GLITCH_COLOR_2])
        
        # Randomly offset message position during glitch
        text_offset_x = 0
        text_offset_y = 0
        if self.glitch_effect_active:
            text_offset_x = random.randint(-10, 10)
            text_offset_y = random.randint(-10, 10)

        text_surface = self.message_font.render(message_text, True, message_color)
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2 + text_offset_x, self.SCREEN_HEIGHT // 2 - 50 + text_offset_y))
        self.screen.blit(text_surface, text_rect)

        # Draw a professional progress bar with glitch effects
        elapsed_time = time.time() - self.start_time
        progress = min(elapsed_time / self.duration, 1.0)
        
        bar_width = int(self.SCREEN_WIDTH * 0.7)
        bar_height = 30
        bar_x = (self.SCREEN_WIDTH - bar_width) // 2
        bar_y = self.SCREEN_HEIGHT // 2 + 50
        bar_radius = 10 # For rounded corners

        # Glitch the progress value
        if self.glitch_effect_active:
            progress += random.uniform(-0.15, 0.15) # More aggressive jump progress
            progress = max(0.0, min(1.0, progress)) # Clamp between 0 and 1

        # Background of the progress bar (darker shade)
        pygame.draw.rect(self.screen, self.SECONDARY_COLOR, (bar_x, bar_y, bar_width, bar_height), border_radius=bar_radius)

        # Filled part of the progress bar (primary color)
        fill_width = int(bar_width * progress)
        fill_color = self.PRIMARY_COLOR
        if self.glitch_effect_active and random.random() < 0.7: # Flicker bar color more often
            fill_color = random.choice([self.PRIMARY_COLOR, self.ACCENT_COLOR, self.GLITCH_COLOR_1, self.GLITCH_COLOR_2])

        if fill_width > 0:
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=bar_radius)

        # Progress percentage text with flicker
        percentage_text = f"{int(progress * 100)}%"
        percentage_color = self.FONT_COLOR
        if self.glitch_effect_active and random.random() < 0.6:
            percentage_color = random.choice([self.FONT_COLOR, self.ACCENT_COLOR, self.GLITCH_COLOR_1, self.GLITCH_COLOR_2])

        percentage_surface = self.message_font.render(percentage_text, True, percentage_color)
        percentage_rect = percentage_surface.get_rect(center=(self.SCREEN_WIDTH // 2, bar_y + bar_height + 30))
        self.screen.blit(percentage_surface, percentage_rect)

        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.update()
            self.draw()
            
            if time.time() - self.start_time > self.duration:
                running = False
                pygame.display.set_caption("Path of Python")