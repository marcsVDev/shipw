from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class Wait(EnemyPattern):
    def __init__(self, position, duration):
        self.time = 0
        super().__init__(position, duration)
    
    def update(self, delta):
        self.time += delta
    
    @property
    def finished(self):
        return self.time >= self.duration