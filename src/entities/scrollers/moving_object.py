from pygame import Vector2

from entities.entity import Entity
from util.animatedSprite import AnimatedSprite


class MovingObject(Entity):
    def __init__(self, animation_sprite: AnimatedSprite, _from: Vector2, target_direction: Vector2, speed: float):
        self.position = Vector2(_from)
        self.target_direction = target_direction.normalize()
        self.speed = speed
        self.animation_sprite = animation_sprite
        self.can_move = False

        super().__init__()

    def update(self, delta):
        if not self.can_move:
            return

        self.position += self.target_direction * self.speed * delta

        self.animation_sprite.update(delta)

        return super().update(delta)

    def draw(self, screen):
        screen.blit(self.animation_sprite.get_current_frame(), (self.position.x, self.position.y))
        return super().draw(screen)

    def run(self):
        self.can_move = True