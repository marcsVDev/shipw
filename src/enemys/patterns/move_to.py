from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class MoveTo(EnemyPattern):
    def __init__(self, start_position: Vector2, end_position: Vector2, duration: float, rotation: float = 0):
        self._star_position: Vector2 = start_position
        self._end_position: Vector2 = end_position
        self.time = 0
        super().__init__(start_position, rotation, duration)
    
    def update(self, delta):
        self.time += delta

        t = min(self.time / self.duration, 1.0) # para no 100%

        self.position = self._star_position.lerp(self._end_position, t)    
    
    @property
    def finished(self):
        return self.time >= self.duration
