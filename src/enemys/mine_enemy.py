from pygame import Vector2

from entities.enemy import Enemy
from game_consts import ENEMYS_PATH


class MineEnemy(Enemy):
    """Mina gravitacional; o formato de colisão será definido com a arte final."""

    DEFAULT_SPRITESHEET = ENEMYS_PATH + "minaespacial.png"
    MULTIPLIER = 1.0
    FRAME_SIZE = 256
    SCALE = 120 * MULTIPLIER
    MIDDLE_SCALE = SCALE // 2

    

    # TODO: substituir pelos vértices do contorno final da mina.
    # Uma lista vazia faz a Scene ignorar colisão física com esta entidade.
    MIDDLE_VECTOR = Vector2(MIDDLE_SCALE, MIDDLE_SCALE)
    MIDDLE_VERTICES = [
        Vector2(100, 159) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(86, 129.5) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(93, 103) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(129.5, 84) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(166, 103) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(173, 129.5) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(159, 159) * MULTIPLIER - MIDDLE_VECTOR
    ]
    DRAW_COLLIDER = True
    DEFAULT_SFX_PATH = None
