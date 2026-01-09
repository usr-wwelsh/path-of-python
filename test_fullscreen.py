"""
Minimal test to verify fullscreen toggle works.
"""
import pygame
import sys

def test_fullscreen_toggle():
    pygame.init()
    pygame.display.set_caption("Fullscreen Test")

    # Create windowed mode first
    screen = pygame.display.set_mode((800, 600))
    print(f"[INIT] Created window: {screen.get_size()}")

    running = True
    fullscreen = False
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    print(f"[TOGGLE] F pressed, current fullscreen={fullscreen}")
                    fullscreen = not fullscreen

                    flags = pygame.FULLSCREEN if fullscreen else 0
                    print(f"[TOGGLE] Creating new display with flags={flags}")

                    screen = pygame.display.set_mode((800, 600), flags)
                    print(f"[TOGGLE] New screen size: {screen.get_size()}")

                    # Force a flip to update the display
                    screen.fill((50, 50, 100))
                    pygame.display.flip()
                    print(f"[TOGGLE] Flipped display")

                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Draw something
        screen.fill((50, 50, 100) if not fullscreen else (100, 50, 50))

        # Draw some text
        font = pygame.font.Font(None, 36)
        text = font.render(f"Fullscreen: {fullscreen} (Press F to toggle, ESC to quit)", True, (255, 255, 255))
        screen.blit(text, (100, 300))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("[EXIT] Test completed")

if __name__ == "__main__":
    test_fullscreen_toggle()
