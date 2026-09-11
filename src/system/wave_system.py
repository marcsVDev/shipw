from entities.enemy_projectile import EnemyProjectile
from events.event_bus import EventBus
from events.events import Events
from system.system import System


class WaveSystem(System):
    def __init__(self, scene, registry):
        self.scene = scene
        self.registry = registry
        self.phase = None
        self.index = -1
        self.remaining = 0
        self.active = []
        self.pending = []
        self.finished = True
        self.waiting = False

    def load_phase(self, phase):
        self.phase = phase
        self.index = -1
        self.remaining = phase.duration if not phase.waves else 2.0
        self.active = []
        self.pending = []
        self.finished = False
        self.waiting = True

    def reset(self):
        """Cancela a onda, inclusive spawns ainda agendados."""
        self.phase = None
        self.index = -1
        self.remaining = 0.0
        self.active.clear()
        self.pending.clear()
        self.finished = True
        self.waiting = False

    def update(self, delta):
        if self.finished or self.scene.player is None or self.scene.player.to_destroy:
            return
        # Remove referências imediatamente; ataques/timers pertencem à entidade.
        self.active[:] = [enemy for enemy in self.active if not enemy.to_destroy]
        for enemy in self.active:
            if not enemy.to_destroy and enemy.can_move and enemy.attack:
                enemy.attack.update(enemy, self.scene.player, delta, self.scene.add_entity)
        if self.waiting:
            self.remaining -= delta
            if self.remaining > 0:
                return
            self.index += 1
            if self.index == len(self.phase.waves):
                self.finished = True
                EventBus.emit(Events.PHASE_COMPLETED, self.phase)
                return
            wave = self.phase.waves[self.index]
            self.pending = sorted([[spawn.delay, order, spawn]
                                   for order, spawn in enumerate(wave.spawns)])
            self.active = []
            self.waiting = False
            self._spawn_due()
            EventBus.emit(Events.WAVE_STARTED, self.phase, self.index, wave)
        else:
            for pending in self.pending:
                pending[0] -= delta
            self._spawn_due()
        if not self.waiting and not self.pending and not self.active:
            if any(isinstance(entity, EnemyProjectile) and not entity.to_destroy
                   for entity in self.scene.entities):
                return
            self.waiting = True
            self.remaining = self.phase.waves[self.index].rest
            EventBus.emit(Events.WAVE_COMPLETED, self.phase, self.index)

    def _spawn_due(self):
        due = [item for item in self.pending if item[0] <= 0]
        self.pending[:] = [item for item in self.pending if item[0] > 0]
        for _, _, spawn in due:
            enemy = self.registry.create(spawn, self.target_position)
            self.active.append(enemy)
            self.scene.add_entity(enemy)

    def target_position(self):
        player = self.scene.player
        return player.position if player is not None and not player.to_destroy else None
