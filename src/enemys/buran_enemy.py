from pygame import Vector2

from entities.enemy import Enemy
from game_consts import ENEMYS_PATH


class BuranEnemy(Enemy):
    """Ônibus espacial que cruza a tela em rasantes alternados."""

    DEFAULT_SPRITESHEET = ENEMYS_PATH + "buran.png"
    DEFAULT_SFX_PATH = None
    FRAME_SIZE = 256
    SCALE = 230
    LOOK_AT_PLAYER = False
    DRAW_COLLIDER = False
    MIDDLE_VERTICES = [
        Vector2(-92, -30), Vector2(-50, -58), Vector2(60, -42),
        Vector2(104, 0), Vector2(60, 42), Vector2(-50, 58),
        Vector2(-92, 30),
    ]

    def __init__(self, patterns=None, flip_x=False):
        self.flip_x = flip_x
        super().__init__(patterns)

    def scale(self, by):
        super().scale(by)
        if self.flip_x:
            import pygame
            self._image = pygame.transform.flip(self._image, True, False)
