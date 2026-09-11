import pygame

from entities.enemy import Enemy
from game_consts import ENEMYS_PATH


class AsteroidEnemy(Enemy):
    """Asteroide de contato com identidade própria e comportamento base."""

    DEFAULT_SPRITESHEET = ENEMYS_PATH + "meteor_enemy.png"
    LOOK_AT_PLAYER = False

    def __init__(self, patterns=None, flip_x: bool = False):
        self.flip_x = flip_x
        super().__init__(patterns)

    def scale(self, by):
        super().scale(by)
        if self.flip_x:
            self._image = pygame.transform.flip(self._image, True, False)
