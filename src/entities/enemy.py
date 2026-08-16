from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern
from enemys.patterns.move_to import MoveTo
from entities.character import Character
from game_consts import GameConsts


class Enemy(Character):    
    INITIAL_POSITION = Vector2(0, 0)
    ROTATION_ANGLE = 360    
    DEFAULT_SPRITESHEET = GameConsts.PLAYER_IMG_PATH
    FRAME_SIZE = 64

    ROTATE = True

    def __init__(self):
        self._current_pattern: int = 0
        self._patterns: list[EnemyPattern] = [
            MoveTo(
                Vector2(-100, 100),
                Vector2(GameConsts.SCREEN_WIDTH + 100, 300),
                5
            ),

            MoveTo(
                Vector2(GameConsts.SCREEN_WIDTH + 100, 300),
                Vector2(-100, 500),
                5
            ),

            MoveTo(
                Vector2(-100, 500),
                Vector2(GameConsts.SCREEN_WIDTH + 100, 700),
                5
            ),

            MoveTo(
                Vector2(GameConsts.SCREEN_WIDTH + 100, 700),
                Vector2(-100, 900),
                5
            ),
        ]

        super().__init__()

    def update(self, delta):
        if self._patterns[self._current_pattern].finished:
            if self._current_pattern + 1 >= len(self._patterns):
                self.visible = False # TODO apagar inimigo quando acaba patterns ??
                return       
            
            self._current_pattern += 1          

        self._patterns[self._current_pattern].update(delta)
            
        return super().update(delta)

    def draw(self, screen):
        return super().draw(screen)

    def movement(self, delta):        
        if self.ROTATE:
            self._rotation += self.ROTATION_ANGLE * delta

        self.position = self._patterns[self._current_pattern].position    
    