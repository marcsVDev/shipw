from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class FlyBy(EnemyPattern):
    """Cruza a tela em linha reta e velocidade constante."""
    # A passagem sempre olha na direção da trajetória, independentemente da
    # posição do jogador.
    locks_facing = True

    def __init__(self, start, end, speed=2200, facing_offset=0):
        start = Vector2(start)
        end = Vector2(end)
        distance = start.distance_to(end)
        if speed <= 0 or distance == 0:
            raise ValueError("FlyBy precisa de velocidade positiva e pontos diferentes")
        super().__init__(start, 0, distance / speed)
        self._direction = (end - start).normalize()
        self._speed = speed
        self._elapsed = 0.0
        self.facing_offset = facing_offset

    def update(self, delta):
        travel_time = min(max(delta, 0), self.duration - self._elapsed)
        self.position += self._direction * self._speed * travel_time
        self._elapsed += travel_time
        self.rotation = -self._direction.angle_to(Vector2(0, 1)) + self.facing_offset

    @property
    def finished(self):
        return self._elapsed >= self.duration
