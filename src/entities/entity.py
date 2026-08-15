from pygame import Surface


class Entity:
    def __init__(self):
        self.visible = True
        super().__init__()
    def draw(self, screen: Surface):
        pass
    def update(self, delta: float):
        pass