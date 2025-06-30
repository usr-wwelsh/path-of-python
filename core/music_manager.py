import pygame
import os
import random

class MusicManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MusicManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            pygame.mixer.init()
            self.music_directory = "data/music"
            self.music_files = [f for f in os.listdir(self.music_directory) if f.endswith(".mp3")]
            self.current_track = None
            self._initialized = True

    def play_random_song(self):
        if not self.music_files:
            print("No music files found in the music directory.")
            return

        if pygame.mixer.music.get_busy():
            #print("Music is already playing.")
            return

        try:
            song = random.choice(self.music_files)
            pygame.mixer.music.load(os.path.join(self.music_directory, song))
            pygame.mixer.music.play()
            self.current_track = song
            print(f"Now playing: {song}")
        except pygame.error as e:
            print(f"Error playing music: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_track = None

    def play_sound_effect(self, sound_file):
        try:
            sound = pygame.mixer.Sound(os.path.join("data", sound_file))
            sound.play()
        except pygame.error as e:
            print(f"Error playing sound effect: {e}")

    def update(self):
        if not pygame.mixer.music.get_busy():
            self.play_random_song()
