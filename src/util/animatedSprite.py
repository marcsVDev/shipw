"""Controle de animações horizontais em um spritesheet."""

from collections.abc import Iterable, Mapping

from pygame import Rect, Surface


class AnimatedSprite:
    """Reproduz sequências de frames de um spritesheet de uma única linha.

    Sem ``animations``, uma animação chamada ``"default"`` é criada com todos
    os frames da imagem. Isso mantém compatibilidade com o uso antigo.

    Exemplo::

        sprite = AnimatedSprite(sheet, 0.12, 64, {
            "idle": [0, 1, 2, 3],
            "boost": {"frames": [4, 5, 6], "loop": False, "frame_time": 0.06},
        })
        sprite.play("boost")
    """

    def __init__(self, spritesheet: Surface, frame_time: float, size: int, animations: Mapping[str, Iterable[int] | Mapping] | None = None,):
        if size <= 0:
            raise ValueError("size deve ser maior que zero")

        self.spritesheet = spritesheet
        self.frame_time = frame_time
        self.size = size
        self.frames_count = self.spritesheet.get_width() // self.size
        if self.frames_count == 0:
            raise ValueError("o spritesheet não possui frames do tamanho informado")

        self._animations: dict[str, dict] = {}
        self.current_animation: str | None = None
        self.frame = 0  # índice dentro da animação atual
        self.time = 0.0
        self.is_playing = False

        if animations is None:
            self.add_animation("default", range(self.frames_count))
        else:
            for name, config in animations.items():
                if isinstance(config, Mapping):
                    self.add_animation(
                        name,
                        config["frames"],
                        frame_time=config.get("frame_time"),
                        loop=config.get("loop", True),
                    )
                else:
                    self.add_animation(name, config)

        self.play(next(iter(self._animations)))

    def add_animation(self, name: str, frames: Iterable[int], *, frame_time: float | None = None, loop: bool = True,):
        frame_list = list(frames)
        if not frame_list:
            raise ValueError("uma animação precisa ter pelo menos um frame")
        if any(frame < 0 or frame >= self.frames_count for frame in frame_list):
            raise ValueError("frame fora dos limites do spritesheet")
        if frame_time is not None and frame_time < 0:
            raise ValueError("frame_time não pode ser negativo")

        self._animations[name] = {
            "frames": frame_list,
            "frame_time": self.frame_time if frame_time is None else frame_time,
            "loop": loop,
        }
        return self

    def play(self, name: str, *, restart: bool = True):
        if name not in self._animations:
            raise KeyError(f"animação desconhecida: {name}")

        if restart or self.current_animation != name:
            self.current_animation = name
            self.frame = 0
            self.time = 0.0
        self.is_playing = True
        return self

    def stop(self, *, reset: bool = False):
        self.is_playing = False
        self.time = 0.0
        if reset:
            self.frame = 0
        return self

    def pause(self):
        return self.stop()

    def resume(self):
        if self.current_animation is not None:
            self.is_playing = True
        return self

    def update(self, delta: float):
        if not self.is_playing or delta <= 0:
            return

        animation = self._animations[self.current_animation]
        duration = animation["frame_time"]
        if duration <= 0:
            return

        self.time += delta
        while self.time >= duration and self.is_playing:
            self.time -= duration
            self.frame += 1
            if self.frame == len(animation["frames"]):
                if animation["loop"]:
                    self.frame = 0
                else:
                    self.frame -= 1
                    self.is_playing = False

    def get_current_frame(self) -> Surface:
        animation = self._animations[self.current_animation]
        return self.get_frame(animation["frames"][self.frame])

    def get_frame(self, frame: int) -> Surface:
        if frame < 0 or frame >= self.frames_count:
            raise IndexError(f"frame inválido: {frame}")
        return self.spritesheet.subsurface(Rect(frame * self.size, 0, self.size, self.size))
