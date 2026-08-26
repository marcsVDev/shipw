from abc import ABC, abstractmethod

from pygame import Surface

class Entity(ABC):
    def __init__(self):
        self.visible = True
        self.to_destroy: bool = False
        super().__init__()

    def draw_image(self, screen: Surface, image: Surface, position) -> None:
        if self.visible:
            screen.blit(image, position)

    @abstractmethod
    def draw(self, screen: Surface):
        pass
    
    @abstractmethod
    def update(self, delta: float):
        pass

    def destroy(self): self.to_destroy = True
