import pygame
import os

class AnimatedCursor:
    def __init__(self, ani_file_path):
        self.ani_file = ani_file_path
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 0
        self.max_frame_delay = 5  # Adjust this to control animation speed
        self.load_animation()

    def load_animation(self):
        # This is a simplified approach since we can't directly load .ani files with pygame
        # We'll simulate animation by loading multiple frames from a sprite sheet
        # In a real implementation, you might need a proper .ani file parser
        try:
            # Try to load the first frame as a fallback
            base_path = os.path.splitext(self.ani_file)[0]
            frame_path = f"{base_path}_frame0.png"

            # Load the first frame
            frame = pygame.image.load(frame_path).convert_alpha()
            self.frames.append(frame)

            # Try to load additional frames (simulating animation)
            for i in range(1, 10):  # Try to load up to 10 frames
                frame_path = f"{base_path}_frame{i}.png"
                if os.path.exists(frame_path):
                    frame = pygame.image.load(frame_path).convert_alpha()
                    self.frames.append(frame)
                else:
                    break

            if not self.frames:
                # If no frames found, load the original .ani file as a static image
                self.frames.append(pygame.image.load(self.ani_file).convert_alpha())

        except pygame.error:
            # If all else fails, create a simple default cursor
            self.frames.append(pygame.Surface((32, 32), pygame.SRCALPHA))
            pygame.draw.circle(self.frames[0], (255, 255, 255, 255), (16, 16), 16)

    def update(self):
        # Update the animation frame
        self.frame_delay += 1
        if self.frame_delay >= self.max_frame_delay:
            self.frame_delay = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def set_position(self, pos):
        self.position = pos