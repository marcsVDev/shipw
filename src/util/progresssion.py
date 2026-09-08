from events.event_bus import EventBus
from events.events import Events
from initializations.phases import get_phases
from system.system import System


class Progression(System):
    def __init__(self):
        self._game_started = False
        self.phase_index = 0
        self.phases = get_phases()
        EventBus.connect(Events.GAME_STARTED, self.game_started)
        EventBus.connect(Events.PHASE_COMPLETED, self.phase_completed)

    def update(self, delta):
        pass

    def phase_completed(self, phase):
        if not self._game_started or phase is not self.phases[self.phase_index]:
            return
        if self.phase_index + 1 == len(self.phases):
            self._game_started = False
            EventBus.emit(Events.GAME_COMPLETED)
            return
        self.phase_index += 1
        EventBus.emit(Events.PHASE_CHANGED, self.phases[self.phase_index])

    def game_started(self):
        self.phase_index = 0
        self._game_started = True
