from pydoc import get_pager

from events.event_bus import EventBus
from events.events import Events
from initializations.phases import get_phases
from system.system import System


class Progression(System):

    
    def __init__(self):
        self._elapsed_time: float = 0
        self._game_started: bool = False
        self.phase_index: int = 0
        self.PHASES = get_phases()

        EventBus.connect(Events.GAME_STARTED, self.game_started)
        super().__init__()

    def update(self, delta):
        if not self._game_started: 
            return
        
        self._elapsed_time += delta

        next_index = self.phase_index + 1
        if next_index < len(self.PHASES):
            next_phase = self.PHASES[next_index]
            if self._elapsed_time >= next_phase.starts_at:
                self.phase_index = next_index
                EventBus.emit(Events.PHASE_CHANGED, self.PHASES[self.phase_index])

    def game_started(self):
        self._game_started = True
