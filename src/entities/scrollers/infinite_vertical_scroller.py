from pygame import Surface

from ..entity import Entity

class InfiniteVerticalScroller(Entity):
    def __init__(self, image: Surface, velocity: float, running: bool = False):
        super().__init__()

        self.image = image
        self.velocity = velocity
        self.running = running
        self.height = image.get_height()
        self.positions = [-self.height, 0] 

    def update(self, delta):
        if not self.running: return

        for i in range(len(self.positions)):
            if self.positions[i] > self.height:
                self.positions[i] = min(self.positions) - self.height # coloca em cima da mais alta

            self.positions[i] += self.velocity * delta

    def draw(self, screen):        
        for pos in self.positions:
            screen.blit(self.image, (0, pos))

    def run(self):
        self.running = True
    