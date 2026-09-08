from typing import Callable


class EventBus:
    events: dict[str, list[Callable]] = {}

    @staticmethod
    def connect(event: str, func: Callable):
        EventBus.events.setdefault(event, []).append(func)

    @staticmethod
    def disconnect(event: str, func: Callable):
        listeners = EventBus.events.get(event, [])
        if func in listeners:
            listeners.remove(func)

    @staticmethod
    def emit(event: str, *args):
        for fn in tuple(EventBus.events.get(event, [])):
            fn(*args)
