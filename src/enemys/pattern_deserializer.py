"""Conversão de objetos de mapas Tiled (TMJ) para padrões de inimigo."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import json
from pathlib import Path

from pygame import Vector2

from enemys.enemy_pattern import EnemyPattern
from enemys.patterns.move_to import MoveTo
from enemys.patterns.rotate import Rotate
from enemys.patterns.wait import Wait
from enemys.patterns.yell import Yell


class PatternDeserializationError(ValueError):
    """Indica que um objeto de padrão no TMJ não possui uma configuração válida."""


@dataclass(frozen=True)
class PatternContext:
    """Estado atual e dados do objeto Tiled entregues a uma fábrica de padrões."""

    position: Vector2
    rotation: float
    target_position: Vector2
    target_rotation: float
    duration: float
    properties: Mapping[str, object]
    object_id: int | None


@dataclass(frozen=True)
class PatternBuildResult:
    """Padrão criado e o estado a ser usado pelo próximo objeto da sequência."""

    pattern: EnemyPattern
    position: Vector2
    rotation: float


PatternFactory = Callable[[PatternContext], PatternBuildResult]


class EnemyPatternDeserializer:
    """Lê um TMJ e cria padrões através de fábricas registradas por tipo.

    Para suportar um novo padrão, basta registrar uma fábrica com
    :meth:`register`, usando o mesmo ``type`` definido no objeto do Tiled.
    """

    def __init__(self):
        self._factories: dict[str, PatternFactory] = {}
        self.register("move_to", self._build_move_to)
        self.register("wait", self._build_wait)
        self.register("rotate", self._build_rotate)
        self.register("yell", self._build_yell)

    def register(self, pattern_type: str, factory: PatternFactory, *, replace: bool = False) -> None:
        """Registra a fábrica responsável por um ``type`` de objeto do Tiled."""
        normalized_type = pattern_type.strip().lower()
        if not normalized_type:
            raise ValueError("O tipo do padrão não pode ser vazio.")
        if normalized_type in self._factories and not replace:
            raise ValueError(f"Já existe uma fábrica registrada para '{normalized_type}'.")

        self._factories[normalized_type] = factory

    def deserialize(
        self,
        tmj_file: str | Path,
        initial_position: Vector2 | None = None,
        initial_rotation: float = 0,
    ) -> list[EnemyPattern]:
        """Retorna os padrões, na ordem dos objetos visíveis do mapa Tiled."""
        source = Path(tmj_file)
        try:
            map_data = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise PatternDeserializationError(f"TMJ inválido: {source}") from error

        position = Vector2(initial_position) if initial_position is not None else Vector2()
        rotation = float(initial_rotation)
        patterns: list[EnemyPattern] = []

        for tiled_object in self._pattern_objects(map_data):
            pattern_type = str(tiled_object.get("type", "")).strip().lower()
            object_id = tiled_object.get("id")
            if not pattern_type:
                raise PatternDeserializationError(f"Objeto {object_id} não possui 'type'.")

            factory = self._factories.get(pattern_type)
            if factory is None:
                raise PatternDeserializationError(
                    f"Tipo de padrão desconhecido '{pattern_type}' no objeto {object_id}."
                )

            properties = self._properties(tiled_object)
            context = PatternContext(
                position=position,
                rotation=rotation,
                target_position=Vector2(tiled_object["x"], tiled_object["y"]),
                target_rotation=float(tiled_object.get("rotation", 0)),
                duration=self._duration(properties, object_id),
                properties=properties,
                object_id=object_id,
            )
            result = factory(context)
            patterns.append(result.pattern)
            position = Vector2(result.position)
            rotation = result.rotation

        return patterns

    @staticmethod
    def _pattern_objects(map_data: Mapping[str, object]) -> list[Mapping[str, object]]:
        layers = map_data.get("layers")
        if not isinstance(layers, list):
            raise PatternDeserializationError("O TMJ não possui uma lista de camadas válida.")

        objects: list[Mapping[str, object]] = []
        for layer in layers:
            if not isinstance(layer, Mapping) or layer.get("type") != "objectgroup":
                continue
            if not layer.get("visible", True):
                continue

            layer_objects = layer.get("objects", [])
            if not isinstance(layer_objects, list):
                raise PatternDeserializationError("A camada de padrões possui objetos inválidos.")
            objects.extend(
                tiled_object
                for tiled_object in layer_objects
                if isinstance(tiled_object, Mapping) and tiled_object.get("visible", True)
            )

        return objects

    @staticmethod
    def _properties(tiled_object: Mapping[str, object]) -> dict[str, object]:
        raw_properties = tiled_object.get("properties", [])
        if not isinstance(raw_properties, list):
            raise PatternDeserializationError("As propriedades de um padrão devem ser uma lista.")

        return {
            str(property_data["name"]): property_data.get("value")
            for property_data in raw_properties
            if isinstance(property_data, Mapping) and "name" in property_data
        }

    @staticmethod
    def _duration(properties: Mapping[str, object], object_id: int | None) -> float:
        try:
            duration = float(properties["duration"])
        except (KeyError, TypeError, ValueError) as error:
            raise PatternDeserializationError(
                f"O objeto {object_id} precisa da propriedade numérica 'duration'."
            ) from error

        if duration <= 0:
            raise PatternDeserializationError(
                f"A duração do objeto {object_id} deve ser maior que zero."
            )
        return duration

    @staticmethod
    def _build_move_to(context: PatternContext) -> PatternBuildResult:
        return PatternBuildResult(
            MoveTo(context.position, context.target_position, context.duration, context.rotation),
            context.target_position,
            context.rotation,
        )

    @staticmethod
    def _build_wait(context: PatternContext) -> PatternBuildResult:
        return PatternBuildResult(
            Wait(context.position, context.duration, context.rotation),
            context.position,
            context.rotation,
        )

    @staticmethod
    def _build_rotate(context: PatternContext) -> PatternBuildResult:
        return PatternBuildResult(
            Rotate(
                context.position,
                context.rotation,
                context.target_rotation,
                context.duration,
            ),
            context.position,
            context.target_rotation,
        )

    def _build_yell(context: PatternContext) -> PatternBuildResult:
        pass
        return PatternBuildResult(
            Yell(
                context.position,
                context.rotation,
                context.duration,
                context.
            ),
        )