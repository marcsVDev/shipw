import pygame
from pygame import Surface, Vector2

from entity import Entity
from event_bus import EventBus

class Player(Entity):
    def __init__(self):
        self.image: Surface = pygame.image.load("player.png").convert_alpha()
        self.position: Vector2 = Vector2(0, 0)
        self.speed = 500
        self.can_move = True

    def update(self, delta):
        if self.can_move: 
            self.movement(delta)
        

    def draw(self, screen: Surface):
        screen.blit(self.image, (self.position.x, self.position.y))

    def movement(self, delta):
        keys = pygame.key.get_pressed()

        direction = Vector2(0, 0)

        if keys[pygame.K_w]:
            direction.y -= 1

        if keys[pygame.K_s]:
            direction.y += 1

        if keys[pygame.K_a]:
            direction.x -= 1

        if keys[pygame.K_d]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.position += direction * self.speed * delta