"""Indicador visual animado usado nos avisos de perigo."""

from pygame import Surface, Vector2

from game_consts import ENEMYS_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from util.animatedSprite import AnimatedSprite
from util.resources import load_image, scaled_frame


class AlertIndicator:
    """Reproduz o alerta de dois frames e o mantém visível na tela."""

    FPS = 12
    FRAME_SIZE = 64
    DISPLAY_SIZE = 96

    def __init__(self):
        self._spritesheet = load_image(ENEMYS_PATH + "alerta.png")
        self._animation = AnimatedSprite(
            self._spritesheet,
            1 / self.FPS,
            self.FRAME_SIZE,
        )

    @property
    def frame_index(self):
        return self._animation.frame_index

    def update(self, delta: float):
        self._animation.update(delta)

    def visible_position(self, position) -> Vector2:
        """Traz um ponto externo para a borda que o inimigo atravessará."""
        half = self.DISPLAY_SIZE / 2
        point = Vector2(position)
        point.x = min(max(point.x, half), SCREEN_WIDTH - half)
        point.y = min(max(point.y, half), SCREEN_HEIGHT - half)
        return point

    def draw(self, screen: Surface, position):
        frame = scaled_frame(
            self._spritesheet,
            self.FRAME_SIZE,
            self._animation.frame_index,
            self.DISPLAY_SIZE,
        )
        screen.blit(frame, frame.get_rect(center=self.visible_position(position)))
