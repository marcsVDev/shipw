from pygame import Vector2
import pygame

from enemys.enemy_pattern import EnemyPattern
from enemys.patterns.move_to import MoveTo
from entities.character import Character
from game_consts import ENEMYS_PATH, SCREEN_WIDTH

class Enemy(Character):    
    INITIAL_POSITION = Vector2(0, 0)
    ROTATION_ANGLE = 360  
    ROTATE = False  
    DEFAULT_SPRITESHEET = ENEMYS_PATH + "meteor_enemy.png"
    FRAME_SIZE = 128
    PATTERNS = [
        MoveTo(
            Vector2(-100, 100),
            Vector2(SCREEN_WIDTH * 0.25, 250),
            0.5
        ),
        MoveTo(
            Vector2(SCREEN_WIDTH * 0.25, 250),
            Vector2(SCREEN_WIDTH * 0.75, 450),
            0.5
        ),
        MoveTo(
            Vector2(SCREEN_WIDTH * 0.75, 450),
            Vector2(SCREEN_WIDTH * 0.25, 650),
            0.5
        ),
        MoveTo(
            Vector2(SCREEN_WIDTH * 0.25, 650),
            Vector2(SCREEN_WIDTH * 0.75, 850),
            0.5
        ),
        MoveTo(
            Vector2(SCREEN_WIDTH * 0.75, 850),
            Vector2(SCREEN_WIDTH + 100, 1000),
            10
        )
    ]

    DEFAULT_SFX_PATH = None

    def __init__(self):
        self._current_pattern: int = 0
        self._patterns: list[EnemyPattern] = self.PATTERNS
        self._sound = pygame.mixer.Sound(self.DEFAULT_SFX_PATH) if self.DEFAULT_SFX_PATH is not None else None
        self.playing_sound = False

        super().__init__()

    def update(self, delta):
        if self._patterns[self._current_pattern].finished:
            if self._current_pattern + 1 >= len(self._patterns):         
                # self.visible = False
                self.destroy()
                return
            
            self._current_pattern += 1

        if self.can_move:
            self._patterns[self._current_pattern].update(delta)

            if (not self.playing_sound and self._sound is not None):
                self._sound.play(-1) 
                self.playing_sound = True                
        elif self.playing_sound:
            self._sound.stop()
            self.playing_sound = False
            
        super().update(delta)

    def movement(self, delta):
        self._rotation = self._patterns[self._current_pattern].rotation
        self.position = self._patterns[self._current_pattern].position
