from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern


class Charge(EnemyPattern):
    """Avisa, captura a posição do alvo e avança em linha reta até sair."""
    def __init__(self, position, speed=1800, warning=.55, duration=2.5):
        if speed <= 0 or warning < 0 or duration <= 0:
            raise ValueError("Velocidade/duração positivas e aviso não negativo")
        super().__init__(Vector2(position), 0, duration)
        self.speed = speed
        self.warning = warning
        self.time = 0.0
        self.direction = None
        self.target = lambda: None

    def bind_target(self, target):
        if target is not None:
            self.target = target

    @property
    def telegraphing(self):
        return self.time < self.warning

    def update(self, delta):
        before = max(0, self.time - self.warning)
        self.time += delta
        if self.time < self.warning:
            return
        if self.direction is None:
            target = self.target()
            direction = Vector2(target) - self.position if target is not None else Vector2(0, 1)
            self.direction = direction.normalize() if direction.length_squared() else Vector2(0, 1)
        travel = min(self.duration, self.time - self.warning) - min(self.duration, before)
        self.position += self.direction * self.speed * travel

    @property
    def finished(self):
        return self.time >= self.warning + self.duration
