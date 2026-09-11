from abc import ABC, abstractmethod

from pygame import Vector2

class EnemyPattern(ABC):
    """Contrato comum para cada passo de movimento de um inimigo."""

    locks_facing = False

    def __init__(self, position: Vector2, rotation: float, duration: float):
        if duration < 0:
            raise ValueError("A duração de um padrão não pode ser negativa")
        self.position = Vector2(position)
        self.duration: float = duration
        self.rotation: float = rotation

    @abstractmethod
    def update(self, delta):
        ...

    def bind_target(self, target):
        """Provider opcional da posição atual do jogador; padrões fixos ignoram."""
        return None

    @property
    @abstractmethod
    def finished(self) -> bool:
        ...
