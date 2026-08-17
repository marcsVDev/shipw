from events.event_bus import EventBus
from events.events import Events
from system.system import System


class Progression(System):
    def __init__(self):
        self._elapsed_time: float = 0
        self._game_started: bool = False

        EventBus.connect(Events.GAME_STARTED, self.game_started)
        super().__init__()

    def update(self, delta):
        if not self._game_started: 
            return
        
        self._elapsed_time += delta

    def game_started(self):
        self._game_started = True
