from collections.abc import Callable

import pygame

from entities.entity import Entity
from util.animatedSprite import AnimatedSprite


class Cutscene(Entity):
    def __init__(
            self,
            animation: AnimatedSprite,
            display_size: tuple[int, int] | None = None,
            on_complete: Callable[[], None] | None = None,
            show_first_frame: bool = False,
    ):
        self.animation = animation
        self.display_size = display_size
        self.on_complete = on_complete
        self.show_first_frame = show_first_frame
        self._started = False
        self._completion_emitted = False
        self._rendered_frame = None
        self._rendered_frame_index = None
        animation.stop(reset=True)

        super().__init__()

    def update(self, delta):
        was_playing = self.animation.is_playing
        self.animation.update(delta)

        if (self._started and was_playing and not self.animation.is_playing
                and not self._completion_emitted):
            self._completion_emitted = True
            if self.on_complete is not None:
                self.on_complete()

        return super().update(delta)

    def draw(self, screen):
        if not self._started and not self.show_first_frame:
            return
        frame = self.animation.get_current_frame()
        if self.display_size is not None:
            if self._rendered_frame_index != self.animation.frame_index:
                self._rendered_frame = pygame.transform.scale(frame, self.display_size)
                self._rendered_frame_index = self.animation.frame_index
            frame = self._rendered_frame
        self.draw_image(screen, frame, (0, 0))
        return super().draw(screen)

    def run(self):
        self._started = True
        self._completion_emitted = False
        self.animation.play("default")
