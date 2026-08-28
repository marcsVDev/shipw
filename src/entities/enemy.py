from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern
from enemys.patterns.move_to import MoveTo
from enemys.patterns.wait import Wait
from entities.character import Character
from events.event_bus import EventBus
from events.events import Events
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

    def __init__(self):
        self._current_pattern: int = 0
        self._patterns: list[EnemyPattern] = self.PATTERNS

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
            
        super().update(delta)

    def movement(self, delta):  

        self._rotation = self._patterns[self._current_pattern].rotation
        self.position = self._patterns[self._current_pattern].position
