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


class AttractionAttack:
    """Aplica no jogador uma atração contínua em direção ao inimigo."""

    def __init__(self, strength=2400, minimum_distance=90):
        if strength <= 0 or minimum_distance <= 0:
            raise ValueError("Força e distância mínima devem ser positivas")
        self.strength = strength
        self.minimum_distance = minimum_distance

    def update(self, enemy, player, delta, emit_projectile):
        offset = enemy.position - player.position
        if offset.length_squared() == 0 or not hasattr(player, "apply_force"):
            return
        distance = offset.length()
        intensity = self.strength * self.minimum_distance / max(distance, self.minimum_distance)
        player.apply_force(offset.normalize() * intensity)
