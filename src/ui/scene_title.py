from pygame import Font, Vector2

from events.event_bus import EventBus
from events.events import Events
from game_consts import SCREEN_WIDTH
from initializations.misc import get_font
from ui.ui import UI


class SceneTitle(UI):  
    START_CYCLE = 5
    DECREASE = 30
    CYCLE = 0.1
    COLOR_FONT = (0xFF, 0xFF, 0xFF)
    POSITION = Vector2(SCREEN_WIDTH//2, 0 + 40)
    def __init__(self, title: str):
        super().__init__(position=self.POSITION)
        self.title: str = title
        self._font: Font = get_font(32)
        self._alpha = 0xFF
        self._elapsed_time = 0
        self._disappear = False

    def update(self, delta, events):
        if not self.visible or self._alpha <= 0: 
            self.visible = False
            self.to_destroy = True
            return
        
        self._elapsed_time += delta

        if self._disappear and self._elapsed_time >= self.CYCLE:            
            self._alpha = max(0, self._alpha - self.DECREASE)
            self._elapsed_time = 0

        if self._elapsed_time >= self.START_CYCLE:
            self._disappear = True
            self._elapsed_time = 0
        
    def draw(self, screen):
        if not self.visible:
            return

        render = self._font.render(self.title, False, self.COLOR_FONT)
        render.set_alpha(self._alpha)

        screen.blit(render, render.get_rect(center=self.position))
