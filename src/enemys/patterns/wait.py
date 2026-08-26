from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class Wait(EnemyPattern):
    def __init__(self, position: Vector2, duration: float, rotation: float = 0):
        self.time = 0
        super().__init__(position, rotation, duration)
    
    def update(self, delta):
        self.time += delta
    
    @property
    def finished(self):
        return self.time >= self.duration
