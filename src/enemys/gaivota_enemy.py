from pygame import Vector2

from enemys.pattern_deserializer import EnemyPatternDeserializer
from enemys.patterns.move_to import MoveTo
from entities.enemy import Enemy
from game_consts import ASSETS_PATH, ENEMYS_PATH, SCREEN_WIDTH


class GaivotaEnemy(Enemy):
    DEFAULT_SPRITESHEET = ENEMYS_PATH + "gaivota.png"
    PATTERNS = EnemyPatternDeserializer().deserialize(ASSETS_PATH+"patterns/test_pattern.tmj")
