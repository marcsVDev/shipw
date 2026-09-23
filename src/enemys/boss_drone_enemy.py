from enemys.drone_enemy import DroneEnemy
from game_consts import ENEMYS_PATH


class BossDroneEnemy(DroneEnemy):
    """Escolta da nave-mãe com a arte própria do confronto final."""

    DEFAULT_SPRITESHEET = ENEMYS_PATH + "navezinhabossfinal.png"
    ANIMATIONS = {"default": (0,)}
