from pygame import Vector2

from entities.enemy import Enemy
from game_consts import ENEMYS_PATH


class EvilDroneEnemy(Enemy):
    """Drone soviético que permanece parado enquanto varre a tela com um raio."""

    LOOK_AT_PLAYER = False
    FRAME_SIZE = 124
    SCALE = 248
    MIDDLE_SCALE = SCALE / 2
    DEFAULT_SPRITESHEET = ENEMYS_PATH + "navedomal-sheet.png"
    ANIMATIONS = {
        "idle": {"frames": (0,), "loop": True},
        "prepare_attack": {
            "frames": tuple(range(8)),
            "loop": False,
            "frame_time": 0.1,
        },
    }
    DEFAULT_ANIMATION = "idle"
    DEFAULT_SFX_PATH = None
    DRAW_COLLIDER = False

    _SPRITE_CENTER = Vector2(FRAME_SIZE / 2)
    _SPRITE_SCALE = SCALE / FRAME_SIZE
    

    SPRITE_VERTICES = (
        (5, 0), (112, 0), (112, 121), (58, 121), (58, 80), (5, 80)
    )

    def __init__(self, patterns=None):
        self._animation_pattern = None
        super().__init__(patterns=patterns)

    def update(self, delta):
        super().update(delta)
        if self.to_destroy or not self._patterns:
            return

        pattern = self._patterns[self._current_pattern]
        if getattr(pattern, "prepares_beam", False):
            if pattern is not self._animation_pattern:
                self._animation_pattern = pattern
                self.play_animation("prepare_attack")
        elif getattr(pattern, "fires_beam", False):
            # A animação é não repetitiva: ao terminar, permanece no frame 7
            # durante toda a varredura do raio.
            return
        elif self._animation.current_animation != "idle":
            self.play_animation("idle")
