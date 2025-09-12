from typing import Callable, Dict, List, Any

class EventEmitter:
    def __init__(self):
        self.events: Dict[str, List[Callable[..., None]]] = {}

    def on(self, event_name: str, callback: Callable[..., None]) -> None:
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(*args, **kwargs)