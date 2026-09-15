import math

import pygame
from pygame import Surface

from ..entity import Entity
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH

class InfiniteVerticalScroller(Entity):
    def __init__(self, image: Surface, velocity: float, running: bool = False):
        super().__init__()

        # Um fundo menor que a viewport deixa o ``screen.fill`` aparecer como
        # uma faixa preta. A escala preserva a proporção e é aplicada uma vez,
        # na criação do cenário, nunca a cada frame.
        scale = max(SCREEN_WIDTH / image.get_width(), SCREEN_HEIGHT / image.get_height(), 1)
        if scale > 1:
            size = (math.ceil(image.get_width() * scale), math.ceil(image.get_height() * scale))
            image = pygame.transform.smoothscale(image, size)

        self.image = image
        self.velocity = velocity
        self.running = running
        self.height = image.get_height()
        self.positions = [-self.height, 0]

    def update(self, delta):
        if not self.running:
            return

        for i in range(len(self.positions)):
            self.positions[i] += self.velocity * delta
            # Normaliza depois do deslocamento. Assim, mesmo uma queda de FPS
            # que avance mais de uma altura não cria lacunas entre os blocos.
            self.positions[i] = self.positions[i] % (self.height * 2) - self.height

    def draw(self, screen):
        for pos in self.positions:
            screen.blit(self.image, (0, round(pos)))

    def run(self):
        self.running = True
