from copy import deepcopy
from pygame import Vector2
import pygame

from enemys.enemy_pattern import EnemyPattern
from enemys.patterns.move_to import MoveTo
from entities.character import Character
from game_consts import ENEMYS_PATH, SCREEN_WIDTH
from util.resources import load_sound

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

    def __init__(self, patterns=None):
        self._current_pattern: int = 0
        self._patterns: list[EnemyPattern] = deepcopy(self.PATTERNS) if patterns is None else patterns
        self.attack = None
        self._sound = load_sound(self.DEFAULT_SFX_PATH) if self.DEFAULT_SFX_PATH is not None else None
        self._channel = None
        self.playing_sound = False

        super().__init__()

    def update(self, delta):
        if not self._patterns:
            self.destroy()
            return
        if self._patterns[self._current_pattern].finished:
            if self._current_pattern + 1 >= len(self._patterns):         
                # self.visible = False
                self.destroy()
                return
            
            self._current_pattern += 1

        if self.can_move:
            self._patterns[self._current_pattern].update(delta)

            if (not self.playing_sound and self._sound is not None):
                self._channel = self._sound.play(-1)
                self.playing_sound = True                
        elif self.playing_sound:
            self.stop_sound()
            
        super().update(delta)        

    def configure(self, patterns, attack=None):
        """Recebe comportamentos novos por instância, sem compartilhar timers."""
        if not patterns:
            raise ValueError("O inimigo precisa de pelo menos um movimento")
        self._patterns = patterns
        self._current_pattern = 0
        self.position = patterns[0].position.copy()
        self.attack = attack
        self.game_started()
        self.update(0)
        return self

    def movement(self, delta):
        self._rotation = self._patterns[self._current_pattern].rotation
        self.position = self._patterns[self._current_pattern].position

    def draw(self, screen):
        super().draw(screen)
        if self.visible and self._patterns and getattr(self._patterns[self._current_pattern], "telegraphing", False):
            pygame.draw.circle(screen, (255, 90, 60), self.position, int(self.SCALE * .55), 3)

    def destroy(self):
        self.stop_sound()
        super().destroy()

    def stop_sound(self):
        if self._channel is not None and self._channel.get_sound() is self._sound:
            self._channel.stop()
        self._channel = None

        self.playing_sound = False
        
