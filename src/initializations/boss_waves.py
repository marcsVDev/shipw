from dataclasses import dataclass
from math import sin, tau

from pygame import Vector2

from enemys.attacks import RotatingBeamAttack
from enemys.enemy_pattern import EnemyPattern
from enemys.patterns import BoundedPursuit, Charge, FlyBy, LaserSweep, MoveTo, PrepareLaser, Wait
from enemys.waves import EnemySpawn
from game_consts import SCREEN_HEIGHT as H, SCREEN_WIDTH as W


@dataclass(frozen=True)
class RobotSeagullConfig:
    dive_speed: float = 1750.0
    scissor_speed: float = 1600.0
    helix_speed: float = 520.0
    helix_amplitude: float = 360.0
    helix_frequency: float = 0.55


@dataclass(frozen=True)
class LaserShipConfig:
    entry_duration: float = 1.2
    charge_duration: float = 0.9
    fire_duration: float = 1.8
    cooldown_duration: float = 0.5
    leave_duration: float = 1.1
    beam_width: float = 18.0


@dataclass(frozen=True)
class BossWaveSpec:
    name: str
    spawns: tuple[EnemySpawn, ...]
    missile_time: float | None
    rest: float


class SineFlight(EnemyPattern):
    locks_facing = True

    def __init__(self, center_x, start_y, vertical_speed, amplitude, frequency,
                 duration, phase=0.0, mirror=False):
        self.center_x = center_x
        self.start_y = start_y
        self.vertical_speed = vertical_speed
        self.amplitude = amplitude
        self.frequency = frequency
        self.elapsed = 0.0
        self.phase = phase
        self.mirror = -1 if mirror else 1
        super().__init__((center_x, start_y), 0, duration)

    def update(self, delta):
        previous = self.position.copy()
        self.elapsed = min(self.duration, self.elapsed + max(0.0, delta))
        self.position.y = self.start_y + self.vertical_speed * self.elapsed
        self.position.x = self.center_x + self.mirror * self.amplitude * sin(
            tau * self.frequency * self.elapsed + self.phase
        )
        direction = self.position - previous
        if direction.length_squared():
            self.rotation = -Vector2(0, 1).angle_to(direction)

    @property
    def finished(self):
        return self.elapsed >= self.duration


class SnapshotCharge(Charge):
    """Investida que fixa o alvo no início, antes do aviso visual."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._captured = False

    def update(self, delta):
        if not self._captured:
            target = self.target()
            captured = Vector2(target) if target is not None else None
            self.target = lambda: captured
            self._captured = True
        super().update(delta)


def _spawn(enemy, movement, delay=0.0, attack=lambda: None):
    return EnemySpawn(enemy, movement, attack, delay=delay)


def _v_formation(count=4, start_delay=0.0):
    result = []
    for index in range(count):
        side = -1 if index < count / 2 else 1
        rank = index % max(1, count // 2)
        start = Vector2(W * (.29 if side < 0 else .71), H * .19)
        anchor = Vector2(W / 2 + side * (130 + rank * 125), 300 + rank * 70)
        end = Vector2(anchor.x + side * 120, H + 190)
        result.append(_spawn("robot_seagull", lambda s=start, a=anchor, e=end: [
            MoveTo(s, a, .8, -Vector2(0, 1).angle_to(a - s)),
            Wait(a, .45), FlyBy(a, e, 1100)
        ], start_delay + index * .12))
    return result


def _scissor():
    result = []
    for pair in range(3):
        y = H * (.40 + pair * .12)
        for side in (-1, 1):
            start = Vector2(-150 if side < 0 else W + 150, y - 260)
            end = Vector2(W + 150 if side < 0 else -150, y + 260)
            result.append(_spawn("robot_seagull", lambda s=start, e=end: [
                FlyBy(s, e, 1600)
            ], pair * .38))
    return result


def _laser(anchor, outside, angle, sweep=0, clockwise=True,
           delay=0.0, config=LaserShipConfig()):
    return _spawn("laser_ship", lambda: [
        MoveTo(outside, anchor, config.entry_duration,
               LaserSweep._sprite_rotation(angle)),
        PrepareLaser(anchor, angle, config.charge_duration),
        LaserSweep(anchor, angle, sweep, clockwise, config.fire_duration),
        Wait(anchor, config.cooldown_duration,
             LaserSweep._sprite_rotation(angle + (sweep if clockwise else -sweep))),
        MoveTo(anchor, outside, config.leave_duration),
    ], delay, lambda: RotatingBeamAttack(width=config.beam_width))


def _pincer_drones():
    margin = 90
    arena = (margin, margin, W - margin, H - margin)
    result = []
    for pair in range(3):
        for side in (-1, 1):
            anchor = Vector2(W * (.18 if side < 0 else .82), H * .38 + pair * 70)
            start = Vector2(-160 if side < 0 else W + 160, anchor.y)
            result.append(_spawn("boss_drone", lambda s=start, a=anchor, p=pair: [
                MoveTo(s, a, .8), Wait(a, .5 + p * .65),
                BoundedPursuit(a, speed=520, duration=4.2, bounds=arena),
            ]))
    return result


def _helix(config=RobotSeagullConfig()):
    duration = (H + 360) / config.helix_speed
    result = []
    for index in range(10):
        mirror = index % 2 == 1
        center = W / 2 + (-120 if mirror else 120)
        phase = (index // 2) * .45
        result.append(_spawn("robot_seagull", lambda c=center, p=phase, m=mirror: [
            SineFlight(c, -150, config.helix_speed, config.helix_amplitude,
                       config.helix_frequency, duration, p, m)
        ], index * .18))
    return result


def _funnel():
    starts = ((-140, 160), (W + 140, 160), (-140, H * .55), (W + 140, H * .55))
    result = []
    for index in range(8):
        start = Vector2(starts[index % 4])
        result.append(_spawn("robot_seagull", lambda s=start: [
            MoveTo(s, s, .01), SnapshotCharge(s, speed=1600, warning=.65, duration=1.6)
        ], (index // 4) * .22))
    for index in range(4):
        x = W * (.30 if index < 2 else .70)
        start_y = -160 if index % 2 == 0 else H + 160
        end_y = H + 160 if start_y < 0 else -160
        result.append(_spawn("boss_drone", lambda x=x, sy=start_y, ey=end_y: [
            FlyBy((x, sy), (x, ey), 420)
        ]))
    return result


def boss_waves():
    laser = LaserShipConfig()
    return (
        BossWaveSpec("Aquisicao de alvo", tuple(_v_formation()), 4.2, 1.8),
        BossWaveSpec("Tesoura americana", tuple(_scissor()), 2.2, 1.3),
        BossWaveSpec("Corredor de execucao", (
            _laser(Vector2(W / 2 - 179, 390), Vector2(W / 2 - 179, -180), 90),
            _laser(Vector2(W / 2 + 179, 390), Vector2(W / 2 + 179, -180), 90),
        ), 2.6, 1.5),
        BossWaveSpec("Pinca orbital", tuple(_pincer_drones()), 2.6, 1.4),
        BossWaveSpec("Helice bloqueadora", tuple(_helix()) + (
            _laser(Vector2(180, 390), Vector2(-200, 390), 28, 70, True,
                   config=LaserShipConfig(fire_duration=2.2, charge_duration=1.0)),
        ), None, 2.2),
        BossWaveSpec("Portao vermelho", (
            _laser(Vector2(180, 520), Vector2(-200, 520), 345, 24, True,
                   config=LaserShipConfig(fire_duration=3.2)),
            _laser(Vector2(W - 180, 520), Vector2(W + 200, 520), 195, 24, False,
                   config=LaserShipConfig(fire_duration=3.2)),
            *_v_formation(4, 3.6),
        ), 3.4, 1.5),
        BossWaveSpec("Funil de comando", tuple(_funnel()), 2.5, 2.0),
    )
