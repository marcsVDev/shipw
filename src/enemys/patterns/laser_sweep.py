from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class PrepareLaser(EnemyPattern):
    """Mantém o drone parado enquanto sua animação de ataque é executada."""

    locks_facing = True
    prepares_beam = True

    def __init__(self, position, angle, duration):
        if duration <= 0:
            raise ValueError("A preparação do raio precisa de duração positiva")
        self.elapsed = 0.0
        self.angle = angle % 360
        super().__init__(Vector2(position), LaserSweep._sprite_rotation(self.angle), duration)

    def update(self, delta):
        self.elapsed = min(self.duration, self.elapsed + max(0, delta))

    @property
    def finished(self):
        return self.elapsed >= self.duration


class LaserSweep(EnemyPattern):
    """Mantém o inimigo parado e gira um raio por um arco configurável."""

    locks_facing = True
    fires_beam = True

    def __init__(self, position, start_angle, sweep_angle, clockwise, duration):
        if duration <= 0 or sweep_angle < 0:
            raise ValueError("Duração positiva e arco do raio não negativo")
        self.start_angle = start_angle % 360
        self.sweep_angle = sweep_angle
        self.clockwise = clockwise
        self.elapsed = 0.0
        super().__init__(Vector2(position), self._sprite_rotation(self.start_angle), duration)

    @staticmethod
    def _sprite_rotation(angle):
        direction = Vector2(1, 0).rotate(angle)
        return -Vector2(0, 1).angle_to(direction)

    @property
    def beam_angle(self):
        progress = min(1.0, self.elapsed / self.duration)
        direction = 1 if self.clockwise else -1
        return (self.start_angle + direction * self.sweep_angle * progress) % 360

    @property
    def beam_direction(self):
        return Vector2(1, 0).rotate(self.beam_angle)

    def update(self, delta):
        self.elapsed = min(self.duration, self.elapsed + max(0, delta))
        self.rotation = self._sprite_rotation(self.beam_angle)

    @property
    def finished(self):
        return self.elapsed >= self.duration
