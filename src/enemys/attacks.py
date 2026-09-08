"""Ataques seguem update(enemy, player, delta, emit_projectile)."""
from pygame import Vector2

from entities.enemy_projectile import EnemyProjectile
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH


class VolleyAttack:
    def __init__(self, interval=1.5, speed=360, angles=(0,), aimed=True, delay=2):
        if interval <= 0 or speed <= 0 or delay < 0:
            raise ValueError("Intervalo/velocidade devem ser positivos; atraso não negativo")
        self.interval = interval
        self.speed = speed
        self.angles = angles
        self.aimed = aimed
        self.remaining = delay

    def update(self, enemy, player, delta, emit_projectile):
        if player is None or player.to_destroy:
            return
        self.remaining -= delta
        if self.remaining > 0:
            return
        if not (0 <= enemy.position.x <= SCREEN_WIDTH and 0 <= enemy.position.y <= SCREEN_HEIGHT * .7):
            return
        # Sem rajadas acumuladas ao voltar à tela ou após travamento de frame.
        self.remaining = self.interval
        direction = player.position - enemy.position if self.aimed else Vector2(0, 1)
        direction = direction.normalize() if direction.length_squared() else Vector2(0, 1)
        for angle in self.angles:
            emit_projectile(EnemyProjectile(enemy.position, direction.rotate(angle) * self.speed))
