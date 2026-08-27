from enemys.enemy_pattern import EnemyPattern
import pygame

from game_consts import SFX_PATH

class Yell(EnemyPattern):
    def __init__(self, position, rotation, duration, sound_file: str):
        self.sound: pygame.Sound = pygame.mixer.Sound(SFX_PATH + sound_file + ".mp3")
        self.runned = False
        super().__init__(position, rotation, duration)

    def update(self, delta):
        if not self.runned:
            self.sound.play()
            self.runned = True

        return super().update(delta)

    @property
    def finished(self):
        return self.runned