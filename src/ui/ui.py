from pygame import Rect, Surface, Vector2
import pygame

from entities.entity import Entity


class UI(Entity):
    def __init__(self, image: Surface | None = None, position: Vector2 | tuple[int, int] = (0, 0)):
        self._image = image
        self.position = Vector2(position)
        self._rect: Rect | None = None
        super().__init__()

    def draw(self, screen: Surface):
        if self._image is not None:
            self.draw_image(screen, self._image, self.position)

    def update(self, delta: float, events: list[pygame.event.Event]):
        pass

    def scale_image(self, size: tuple[int, int]) -> None:
        if self._image is not None:
            self._image = pygame.transform.scale(self._image, size)

    def align_rect(self) -> None:
        if self._image is not None:
            self._rect = self._image.get_rect(center=self.position)
