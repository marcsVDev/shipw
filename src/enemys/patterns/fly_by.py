from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class FlyBy(EnemyPattern):
    """Cruza a tela em linha reta e velocidade constante."""

    def __init__(self, start, end, speed=2200):
        start = Vector2(start)
        end = Vector2(end)
        distance = start.distance_to(end)
        if speed <= 0 or distance == 0:
            raise ValueError("FlyBy precisa de velocidade positiva e pontos diferentes")
        super().__init__(start, 0, distance / speed)
        self._direction = (end - start).normalize()
        self._speed = speed
        self._elapsed = 0.0

    def update(self, delta):
        travel_time = min(max(delta, 0), self.duration - self._elapsed)
        self.position += self._direction * self._speed * travel_time
        self._elapsed += travel_time
        self.rotation = -self._direction.angle_to(Vector2(0, 1))

    @property
    def finished(self):
        return self._elapsed >= self.duration
