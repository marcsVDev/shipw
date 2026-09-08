from pygame import Vector2

class EnemyPattern:
    def __init__(self, position: Vector2, rotation: float, duration: float):
        self.position: Vector2 = position
        self.duration: float = duration
        self.rotation: float = rotation
        ...
        
    def update(self, delta):
        ...

    def bind_target(self, target):
        """Provider opcional da posição atual do jogador; padrões fixos ignoram."""
        pass

    @property
    def finished(self) -> bool:
        ...
