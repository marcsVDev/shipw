from entities.enemy_beam import EnemyBeam
from entities.guided_missile import GuidedMissile, GuidedMissileConfig
from events.event_bus import EventBus
from events.events import Events
from initializations.boss_waves import boss_waves
from system.system import System
from ui.health_bar import BossHealthBar
from enemys.mother_ship_enemy import MotherShipEnemy


class BossFightSystem(System):
    """Diretor temporal exclusivo da Órbita de Marte."""

    def __init__(self, scene, registry):
        self.scene = scene
        self.registry = registry
        self.phase = None
        self.boss = None
        self.waves = boss_waves()
        self.wave_index = -1
        self.loop_count = 0
        self.wave_elapsed = 0.0
        self.pending = []
        self.active_enemies = []
        self.active_missile = None
        self.missile_created = False
        self.rest_remaining = 0.0
        self.intro_remaining = 0.0
        self.active = False
        self.defeating = False
        self.defeat_elapsed = 0.0
        self.completed = False
        EventBus.connect(Events.PLAYER_DIED, self._player_died)
        EventBus.connect(Events.BOSS_DEFEATED, self._boss_defeated)

    def load_phase(self, phase):
        self.reset()
        self.phase = phase
        if not getattr(phase, "boss_fight", False):
            return
        self.boss = MotherShipEnemy()
        self.scene.add_entity(self.boss, "mother_ship")
        self.scene.add_ui(BossHealthBar(self.boss), "boss_health")
        self.intro_remaining = self.boss.config.entry_duration + 1.0
        self.active = True
        EventBus.emit(Events.BOSS_STARTED, self.boss)

    def reset(self):
        self.phase = None
        self.boss = None
        self.wave_index = -1
        self.loop_count = 0
        self.wave_elapsed = 0.0
        self.pending = []
        self.active_enemies = []
        self.active_missile = None
        self.missile_created = False
        self.rest_remaining = 0.0
        self.intro_remaining = 0.0
        self.active = False
        self.defeating = False
        self.defeat_elapsed = 0.0
        self.completed = False

    def update(self, delta):
        if not self.active or self.completed:
            return
        delta = max(0.0, delta)
        if self.defeating:
            self.defeat_elapsed += delta
            if self.defeat_elapsed >= self.boss.config.defeat_duration and not self.completed:
                self.completed = True
                self.active = False
                EventBus.emit(Events.PHASE_COMPLETED, self.phase)
            return
        player = self.scene.player
        if player is None or player.to_destroy:
            return
        if self.intro_remaining > 0:
            self.intro_remaining -= delta
            if self.intro_remaining <= 0:
                self._begin_next_wave()
            return
        if self.rest_remaining > 0:
            self.rest_remaining -= delta
            if self.rest_remaining <= 0:
                self._begin_next_wave()
            return

        self.wave_elapsed += delta
        self.active_enemies[:] = [enemy for enemy in self.active_enemies if not enemy.to_destroy]
        for enemy in tuple(self.active_enemies):
            if enemy.can_move and enemy.attack:
                enemy.attack.update(enemy, player, delta, self.scene.add_entity)
        self._spawn_due()

        wave = self._current_wave()
        hazards = any((isinstance(entity, EnemyBeam)
                       or getattr(entity, "is_guided_missile", False))
                      and not entity.to_destroy for entity in self.scene.entities)
        attack_wave_done = not self.pending and not self.active_enemies and not hazards
        if (attack_wave_done and wave.missile_time is not None and not self.missile_created
                and self.wave_elapsed >= wave.missile_time - GuidedMissileConfig().telegraph_duration
                and player.time_since_damage >= .75):
            self._launch_missile()

        if self.active_missile is not None and self.active_missile.to_destroy:
            self.active_missile = None

        missile_done = wave.missile_time is None or (
            self.missile_created and self.active_missile is None
        )
        if not self.pending and not self.active_enemies and not hazards and missile_done:
            EventBus.emit(Events.WAVE_COMPLETED, self.phase, self.wave_index)
            self.rest_remaining = max(1.0, wave.rest)

    def _current_wave(self):
        return self.waves[self.wave_index]

    def _begin_next_wave(self):
        if self.wave_index < 6:
            self.wave_index += 1
        else:
            self.wave_index = 1
            self.loop_count += 1
        wave = self._current_wave()
        self.wave_elapsed = 0.0
        self.pending = sorted([[spawn.delay, order, spawn]
                               for order, spawn in enumerate(wave.spawns)])
        self.active_enemies = []
        self.active_missile = None
        self.missile_created = False
        self.rest_remaining = 0.0
        EventBus.emit(Events.WAVE_STARTED, self.phase, self.wave_index, wave)
        self._spawn_due()

    def _spawn_due(self):
        due = [item for item in self.pending if item[0] <= self.wave_elapsed]
        self.pending[:] = [item for item in self.pending if item[0] > self.wave_elapsed]
        for _, _, spawn in due:
            alive_minors = sum(not enemy.to_destroy for enemy in self.active_enemies)
            if alive_minors >= 12:
                self.pending.append([self.wave_elapsed + .1, len(self.pending), spawn])
                continue
            preview = spawn.movement()
            target = self.target_position()
            if (target is not None and preview
                    and preview[0].position.distance_to(target) < 260):
                self.pending.append([self.wave_elapsed + .2, len(self.pending), spawn])
                continue
            enemy = self.registry.create(spawn, self.target_position)
            self.active_enemies.append(enemy)
            self.scene.add_entity(enemy)

    def _launch_missile(self):
        self.missile_created = True
        self.active_missile = GuidedMissile(
            self.boss.launch_position,
            self.target_position, self.boss,
        )
        self.scene.add_entity(self.active_missile)

    def target_position(self):
        player = self.scene.player
        return player.position if player is not None and not player.to_destroy else None

    def _player_died(self, player):
        if not self.active:
            return
        self.active = False
        self.pending.clear()
        self._destroy_hazards()

    def _boss_defeated(self, boss):
        if boss is not self.boss or self.defeating:
            return
        self.defeating = True
        self.pending.clear()
        self._destroy_hazards()

    def _destroy_hazards(self):
        for entity in tuple(self.scene.entities):
            if entity is self.boss or entity is self.scene.player:
                continue
            if (entity in self.active_enemies or isinstance(entity, EnemyBeam)
                    or getattr(entity, "is_guided_missile", False)):
                entity.destroy()
        self.active_enemies.clear()
        self.active_missile = None
