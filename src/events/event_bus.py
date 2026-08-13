from typing import Callable


class EventBus:
    events: dict[str, list[Callable]] = {}

    @staticmethod
    def connect(event: str, func: Callable):
        EventBus.events.setdefault(event, []).append(func)

    @staticmethod
    def emit(event: str):
        for fn in EventBus.events[event]:
            fn()