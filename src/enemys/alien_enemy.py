from pygame import Vector2

from entities.enemy import Enemy
from game_consts import ENEMYS_PATH


class AlienEnemy(Enemy):
    """Piloto alienígena que atravessa a tela em rasantes horizontais."""

    LOOK_AT_PLAYER = False
    DEFAULT_SPRITESHEET = ENEMYS_PATH + "alien.png"
    DEFAULT_SFX_PATH = None
    FRAME_SIZE = 128
    SCALE = 256
    DRAW_COLLIDER = False

    _SPRITE_CENTER = Vector2(FRAME_SIZE / 2)
    _SPRITE_SCALE = SCALE / FRAME_SIZE
    # Aproximação convexa da silhueta completa (nave e piloto).
    MIDDLE_VERTICES = [
        (Vector2(2, 18) - _SPRITE_CENTER) * _SPRITE_SCALE,
        (Vector2(124, 18) - _SPRITE_CENTER) * _SPRITE_SCALE,
        (Vector2(124, 105) - _SPRITE_CENTER) * _SPRITE_SCALE,
        (Vector2(2, 105) - _SPRITE_CENTER) * _SPRITE_SCALE,
    ]

