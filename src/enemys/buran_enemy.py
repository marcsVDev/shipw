from pygame import Vector2

from entities.enemy import Enemy
from game_consts import ENEMYS_PATH


class BuranEnemy(Enemy):
    """Ônibus espacial que cruza a tela em rasantes alternados."""

    DEFAULT_SPRITESHEET = ENEMYS_PATH + "buran.png"
    DEFAULT_SFX_PATH = None
    FRAME_SIZE = 429
    SCALE = 1200
    LOOK_AT_PLAYER = False
    DRAW_COLLIDER = True
    DRAW_DANGER_LINE = False
    # Contorno convexo em pixels do frame original (exigido pelo SAT).
    SPRITE_VERTICES = (
        (35, 229), (118,183), (312, 183), (386, 118), (403, 118),
        (423, 168), (423, 262), (389, 247), (44, 247),
    )

    def __init__(self, patterns=None, flip_x=False):
        self.flip_x = flip_x
        self.FLIP_X = flip_x
        # O sprite e o colisor usam o mesmo centro e a mesma escala.
        self.MIDDLE_VERTICES = [
            (Vector2(vertex) - Vector2(self.FRAME_SIZE / 2))
            * (self.SCALE / self.FRAME_SIZE)
            for vertex in self.SPRITE_VERTICES
        ]
        super().__init__(patterns)
        self._collider_vertices = self.get_rotated_vertices()
