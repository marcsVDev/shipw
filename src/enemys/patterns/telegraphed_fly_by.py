from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class TelegraphedFlyBy(EnemyPattern):
    """Indica a faixa de risco antes de percorrê-la em velocidade constante."""
    locks_facing = True

    def __init__(self, start, end, speed=1800, warning=.8, spin_speed=0,
                 initial_rotation=None):
        start, end = Vector2(start), Vector2(end)
        distance = start.distance_to(end)
        if distance == 0 or speed <= 0 or warning < 0:
            raise ValueError("Trajetória avisada inválida")
        self.start, self.end = start, end
        self.direction = (end - start).normalize()
        self.speed, self.warning, self.spin_speed = speed, warning, spin_speed
        self.elapsed = 0.0
        path_rotation = -Vector2(0, 1).angle_to(self.direction)
        super().__init__(start, path_rotation if initial_rotation is None else initial_rotation,
                         warning + distance / speed)

    @property
    def telegraphing(self): return self.elapsed < self.warning

    @property
    def danger_line(self): return self.start, self.end

    def update(self, delta):
        old = self.elapsed
        self.elapsed = min(self.duration, self.elapsed + max(delta, 0))
        travel = max(0, self.elapsed - self.warning) - max(0, old - self.warning)
        self.position += self.direction * self.speed * travel
        if self.elapsed >= self.warning:
            self.rotation += self.spin_speed * max(delta, 0)

    @property
    def finished(self): return self.elapsed >= self.duration
