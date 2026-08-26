from pygame import Vector2
from pygame.math import lerp

from enemys.enemy_pattern import EnemyPattern


class Rotate(EnemyPattern):
    def __init__(
        self,
        position: Vector2,
        start_rotation: float,
        target_rotation: float,
        duration: float,
    ):
        self._start_rotation = start_rotation
        self._target_rotation = target_rotation
        self.time = 0.0
        super().__init__(position, start_rotation, duration)

    def update(self, delta: float):
        self.time += delta
        progress = min(self.time / self.duration, 1.0)
        self.rotation = lerp(self._start_rotation, self._target_rotation, progress)

    @property
    def finished(self) -> bool:
        return self.time >= self.duration
