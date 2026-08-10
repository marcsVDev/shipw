from pygame import Surface


class Entity:
    def __init__(self):
        self.visible = True
    def draw(self, screen: Surface):
        pass
    def update(self, delta: float):
        pass