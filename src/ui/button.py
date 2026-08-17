from typing import Callable

import pygame
from pygame import Rect, Surface, Vector2

from util.animatedSprite import AnimatedSprite
from ui.ui import UI

class Button(UI):
    DRAW_AREA = True

    def __init__(self, image: Surface, position: Vector2, frame_size: int, press_callable: Callable, area_size: tuple[int, int] = (0, 0)):
        self.press_callable = press_callable
        self.area = Rect(
            position.x + (frame_size - area_size[0]) / 2,
            position.y + (frame_size - area_size[1]) / 2,
            area_size[0],
            area_size[1]
        )
        self.button_animation = AnimatedSprite(image, 0, frame_size)
        self.pressed = False
        super().__init__(image, position)

    def update(self, delta, events):        
        mouse_pos = pygame.mouse.get_pos()

        self.hovered = self.area.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT and self.hovered:
                    if self.press_callable is not None: self.press_callable()
                    self.pressed = True
            if self.pressed and event.type == pygame.MOUSEBUTTONUP:
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

        if self.DRAW_AREA:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                self.area,
                2
            )