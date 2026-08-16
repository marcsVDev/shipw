from abc import ABC, abstractmethod

from pygame import Surface


class Entity(ABC):
    def __init__(self):
        self.visible = True
        super().__init__()

    @abstractmethod
    def draw(self, screen: Surface):
        pass
    
    @abstractmethod
    def update(self, delta: float):
        pass