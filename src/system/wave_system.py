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
        self.finished = True
        self.waiting = False

    def load_phase(self, phase):
        self.phase = phase
        self.index = -1
        self.remaining = phase.duration if not phase.waves else 2.0
        self.active = []
        self.finished = False
        self.waiting = True

    def update(self, delta):
        if self.finished or self.scene.player is None or self.scene.player.to_destroy:
            return
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
            self.active = [self.registry.create(spawn, self.target_position) for spawn in wave.spawns]
            for enemy in self.active:
                self.scene.add_entity(enemy)
            self.waiting = False
            EventBus.emit(Events.WAVE_STARTED, self.phase, self.index, wave)
        elif all(enemy.to_destroy for enemy in self.active):
            if any(isinstance(entity, EnemyProjectile) and not entity.to_destroy
                   for entity in self.scene.entities):
                return
            self.waiting = True
            self.remaining = self.phase.waves[self.index].rest
            EventBus.emit(Events.WAVE_COMPLETED, self.phase, self.index)

    def target_position(self):
        player = self.scene.player
        return player.position if player is not None and not player.to_destroy else None
