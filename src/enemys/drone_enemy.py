from pygame import Vector2

from enemys.pattern_deserializer import EnemyPatternDeserializer
from entities.enemy import Enemy
from game_consts import ENEMYS_PATH, PATTERNS_PATH, SFX_PATH

class DroneEnemy(Enemy):
    MULTIPLIER = 1.1
    SCALE = 128 * MULTIPLIER
    MIDDLE_SCALE = SCALE // 2

    DEFAULT_SPRITESHEET = ENEMYS_PATH + "drone.png"

    MIDDLE_VECTOR = Vector2(MIDDLE_SCALE, MIDDLE_SCALE)
    DRAW_COLLIDER = False
    MIDDLE_VERTICES = [
        Vector2(64, 23) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(104, 64) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(64, 104) * MULTIPLIER - MIDDLE_VECTOR,
        Vector2(23, 64) * MULTIPLIER - MIDDLE_VECTOR
    ]

    DEFAULT_SFX_PATH = SFX_PATH + "drone_default.mp3"

    def __init__(self):
        super().__init__()        
        self._patterns = EnemyPatternDeserializer().deserialize(PATTERNS_PATH + "gaivota.tmj")

    def update(self, delta):
        return super().update(delta)
    