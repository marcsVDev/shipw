from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern
from util.resources import load_sound

class Yell(EnemyPattern):
    """Passo instantâneo que sinaliza, uma única vez, o início de um ataque."""

    locks_facing = True

    def __init__(self, position, sound_path: str, rotation=0):
        self.sound = load_sound(sound_path)
        self._played = False
        super().__init__(Vector2(position), rotation, 0)

    def update(self, delta):
        if not self._played:
            self.sound.play()
            self._played = True

    @property
    def finished(self):
        return self._played
