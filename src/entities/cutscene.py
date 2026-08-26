from pygame import Surface

from entities.entity import Entity
from util.animatedSprite import AnimatedSprite


class Cutscene(Entity):
    def __init__(self, animation: AnimatedSprite):
        self.animation = animation
        animation.stop()

        super().__init__()

    def update(self, delta):
        self.animation.update()

        return super().update(delta)

    def draw(self, screen):
        screen.blit(self.animation.get_current_frame(), (0, 0))
        return super().draw(screen)

    def run(self):
        self.animation.play("default")
    