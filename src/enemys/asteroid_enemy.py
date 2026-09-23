from pygame import Vector2

from entities.enemy import Enemy
from game_consts import ENEMYS_PATH


class AsteroidEnemy(Enemy):
    """Asteroide de contato com identidade própria e comportamento base."""
    FLIP_Y = True
    MULTIPLIER = 1.1
    SCALE = 128 * MULTIPLIER
    MIDDLE_SCALE = SCALE // 2

    DEFAULT_SPRITESHEET = ENEMYS_PATH + "asteroidenormal.png"
    LOOK_AT_PLAYER = False

    ANIMATION_FRAME_DURATION = 0.10

    MIDDLE_VECTOR = Vector2(MIDDLE_SCALE, MIDDLE_SCALE)
    DRAW_COLLIDER = True
    MIDDLE_VERTICES = [
        Vector2(56, 44) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(38, 69) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(42, 108) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(78, 122) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(111, 124) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(124, 105) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(120, 76) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(90, 51) * MULTIPLIER - MIDDLE_VECTOR
    ]

    def __init__(self, patterns=None, flip_x: bool = False):
        self.flip_x = flip_x
        self.FLIP_X = flip_x
        super().__init__(patterns)
