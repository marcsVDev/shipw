from typing import Callable

import pygame
from pygame import Rect, Surface, Vector2

from util.animatedSprite import AnimatedSprite
from ui.ui import UI

class Button(UI):
    def __init__(self, image: Surface, position: Vector2, size: int, press_callable: Callable):
        self.press_callable = press_callable
        self.area = Rect(0, 0, size, size)
        self.button_animation = AnimatedSprite(image, 0, size)
        self.pressed = False
        super().__init__(image, position)

    def update(self, delta, events):        
        mouse_pos = pygame.mouse.get_pos()

        self.hovered = True if self.area.collidepoint(mouse_pos) else False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT and self.hovered:
                    if self.press_callable is not None: self.press_callable()
                    self.pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    self.pressed = False

        if self.pressed:
            self.image = self.button_animation.get_frame(1)
        elif self.hovered:
            self.image = self.button_animation.get_frame(2)
        else:
            self.image = self.button_animation.get_frame(0)
                    

    def draw(self, screen):
        if not self.visible: 
            return
        
        screen.blit(self.image, (self.position.x, self.position.y))