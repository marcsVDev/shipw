from pygame import Vector2

class EnemyPattern:
    def __init__(self, position: Vector2, duration: float):
        self.position: Vector2 = position
        self.duration: float = duration
        ...
        
    def update(self, delta):
        ...

    @property
    def finished(self) -> bool:
        ...