"""Padrões matemáticos reutilizáveis, independentes da renderização."""
from collections.abc import Callable
from math import sin, tau

from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class ZigZag(EnemyPattern):
    def __init__(self, start, vertical_speed=420, amplitude=180, frequency=.7,
                 duration=3.5, phase=0.0, bounds=None):
        if vertical_speed <= 0 or amplitude < 0 or frequency < 0 or duration <= 0:
            raise ValueError("Parâmetros do zigue-zague são inválidos")
        super().__init__(Vector2(start), 0, duration)
        self.origin = Vector2(start)
        self.vertical_speed, self.amplitude, self.frequency = vertical_speed, amplitude, frequency
        self.phase, self.bounds, self.elapsed = phase, bounds, 0.0

    def update(self, delta):
        self.elapsed = min(self.duration, self.elapsed + max(0, delta))
        x = self.origin.x + self.amplitude * sin(tau * self.frequency * self.elapsed + self.phase)
        if self.bounds:
            x = max(self.bounds[0], min(self.bounds[1], x))
        self.position.update(x, self.origin.y + self.vertical_speed * self.elapsed)

    @property
    def finished(self): return self.elapsed >= self.duration


class Orbit(EnemyPattern):
    def __init__(self, center, radius, angle, angular_speed, center_speed, duration,
                 x_bounds):
        if radius <= 0 or duration <= 0 or x_bounds[0] >= x_bounds[1]:
            raise ValueError("Parâmetros da órbita são inválidos")
        self.center = Vector2(center)
        self.radius, self.angle = radius, angle
        self.angular_speed, self.center_speed = angular_speed, center_speed
        self.x_bounds, self.elapsed = x_bounds, 0.0
        super().__init__(self.point(), 0, duration)

    def point(self): return self.center + Vector2(self.radius, 0).rotate(self.angle)

    def update(self, delta):
        step = min(max(delta, 0), self.duration - self.elapsed)
        self.elapsed += step
        self.angle += self.angular_speed * step
        self.center.x += self.center_speed * step
        if self.center.x < self.x_bounds[0] or self.center.x > self.x_bounds[1]:
            self.center.x = max(self.x_bounds[0], min(self.x_bounds[1], self.center.x))
            self.center_speed *= -1
        self.position = self.point()

    @property
    def finished(self): return self.elapsed >= self.duration


class Float(EnemyPattern):
    def __init__(self, base, drift=(0, 30), amplitude=(90, 45), frequency=(.18, .27),
                 phase=(0, 0), duration=10):
        if duration <= 0 or min(frequency) < 0:
            raise ValueError("Parâmetros de flutuação são inválidos")
        self.base, self.drift = Vector2(base), Vector2(drift)
        self.amplitude, self.frequency, self.phase = Vector2(amplitude), Vector2(frequency), Vector2(phase)
        self.elapsed = 0.0
        super().__init__(base, 0, duration)

    def update(self, delta):
        self.elapsed = min(self.duration, self.elapsed + max(0, delta))
        self.position = self.base + self.drift * self.elapsed + Vector2(
            self.amplitude.x * sin(tau * self.frequency.x * self.elapsed + self.phase.x),
            self.amplitude.y * sin(tau * self.frequency.y * self.elapsed + self.phase.y))

    @property
    def finished(self): return self.elapsed >= self.duration


class Pursuit(EnemyPattern):
    """Investe até alvos sucessivos e prolonga a última investida para fora da tela."""
    def __init__(self, start, charges=3, speed=1800, warning=.45, charge_duration=1.1,
                 interval=.45, reposition=None, exit_bounds=None, exit_margin=160):
        if charges < 1 or min(speed, charge_duration) <= 0 or min(warning, interval) < 0:
            raise ValueError("Parâmetros da perseguição são inválidos")
        self.charges, self.speed, self.warning = charges, speed, warning
        self.charge_duration, self.interval = charge_duration, interval
        self.exit_bounds = exit_bounds
        self.exit_margin = exit_margin
        self._final_duration = charge_duration
        # Mantido no construtor por compatibilidade com configurações existentes.
        # A perseguição agora recomeça do ponto alcançado, sem teletransporte.
        self.reposition = Vector2(reposition or start)
        self.completed_charges, self.elapsed = 0, 0.0
        self.state, self.direction = "warning", None
        self.captured_target: Vector2 | None = None
        self._distance_left = 0.0
        self.target: Callable[[], Vector2 | None] = lambda: None
        duration = charges * (warning + charge_duration) + (charges - 1) * interval
        super().__init__(Vector2(start), 0, duration)

    def bind_target(self, target):
        if target is not None: self.target = target

    def _time_until_outside(self):
        if self.exit_bounds is None:
            return self.charge_duration
        left, top, right, bottom = self.exit_bounds
        left -= self.exit_margin; top -= self.exit_margin
        right += self.exit_margin; bottom += self.exit_margin
        times = []
        if self.direction.x > 0: times.append((right - self.position.x) / self.direction.x)
        elif self.direction.x < 0: times.append((left - self.position.x) / self.direction.x)
        if self.direction.y > 0: times.append((bottom - self.position.y) / self.direction.y)
        elif self.direction.y < 0: times.append((top - self.position.y) / self.direction.y)
        distance = min(value for value in times if value >= 0)
        return distance / self.speed

    @property
    def locks_facing(self): return self.state in ("warning", "charge")

    @property
    def telegraphing(self): return self.state == "warning"

    def update(self, delta):
        remaining = max(0.0, delta)
        while remaining and not self.finished:
            if self.state == "warning":
                step = min(remaining, self.warning - self.elapsed)
                self.elapsed += step; remaining -= step
                if self.elapsed + 1e-9 < self.warning:
                    continue
                self.elapsed = 0.0
                target = self.target()
                self.captured_target = Vector2(target) if target is not None else self.position + Vector2(0, 1)
                direction = self.captured_target - self.position
                self._distance_left = direction.length()
                self.direction = direction.normalize() if direction.length_squared() else Vector2(0, 1)
                self.rotation = -Vector2(0, 1).angle_to(self.direction)
                if self.completed_charges == self.charges - 1:
                    self._final_duration = self._time_until_outside()
                self.state = "charge"
                continue

            if self.state == "wait":
                step = min(remaining, self.interval - self.elapsed)
                self.elapsed += step; remaining -= step
                if self.elapsed + 1e-9 < self.interval:
                    continue
                self.elapsed = 0.0
                self.direction, self.state = None, "warning"
                continue

            final_charge = self.completed_charges == self.charges - 1
            if final_charge:
                step = min(remaining, self._final_duration - self.elapsed)
                self.position += self.direction * self.speed * step
                self.elapsed += step; remaining -= step
                if self.elapsed + 1e-9 < self._final_duration:
                    continue
            else:
                travel = min(self.speed * remaining, self._distance_left)
                step = travel / self.speed
                self.position += self.direction * travel
                self._distance_left -= travel
                remaining -= step
                if self._distance_left > 1e-9:
                    continue
                self.position = self.captured_target.copy()

            self.elapsed = 0.0
            self.completed_charges += 1
            self.state = "done" if self.completed_charges >= self.charges else "wait"

    @property
    def finished(self): return self.state == "done"
