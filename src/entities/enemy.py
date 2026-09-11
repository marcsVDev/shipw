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
    LOOK_AT_PLAYER = False
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
    DRAW_COLLIDER = True

    def __init__(self, patterns=None):
        self._current_pattern: int = 0
        self._patterns: list[EnemyPattern] = deepcopy(self.PATTERNS) if patterns is None else patterns
        self.attack = None
        self._target_provider = lambda: None
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

    def configure(self, patterns, attack=None, target=None):
        """Recebe comportamentos novos por instância, sem compartilhar timers."""
        if not patterns:
            raise ValueError("O inimigo precisa de pelo menos um movimento")
        self._patterns = patterns
        self._current_pattern = 0
        self.position = patterns[0].position.copy()
        self.attack = attack
        self.bind_target(target)
        self.game_started()
        self.update(0)
        return self

    def movement(self, delta):
        pattern = self._patterns[self._current_pattern]
        self.position = pattern.position
        self._rotation = pattern.rotation
        if self.LOOK_AT_PLAYER and not pattern.locks_facing:
            target = self._target_provider()
            if target is not None:
                direction = Vector2(target) - self.position
                if direction.length_squared():
                    # Os sprites de inimigos apontam para baixo em rotação zero.
                    self._rotation = -Vector2(0, 1).angle_to(direction)

    def bind_target(self, target):
        """Define um provider da posição do alvo, sem acoplar o inimigo à Scene."""
        self._target_provider = target if target is not None else lambda: None

    def draw(self, screen):
        super().draw(screen)
        pattern = self._patterns[self._current_pattern] if self._patterns else None
        if self.visible and pattern and getattr(pattern, "telegraphing", False):
            pygame.draw.circle(screen, (255, 90, 60), self.position, int(self.SCALE * .55), 3)
            danger_line = getattr(pattern, "danger_line", None)
            if danger_line:
                pygame.draw.line(screen, (255, 90, 60), *danger_line, 5)

    def destroy(self):
        self.stop_sound()
        super().destroy()

    def stop_sound(self):
        if self._channel is not None and self._channel.get_sound() is self._sound:
            self._channel.stop()
        self._channel = None

        self.playing_sound = False
        
