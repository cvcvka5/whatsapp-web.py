from ..logger import logger
from typing import Callable, Dict, List, Any

class EventEmitter:
    """
    Simple event emitter class to register, emit, and remove events.
    """

    def __init__(self):
        self.events: Dict[str, List[Callable[..., None]]] = {}

    def on(self, event_name: str, callback: Callable[..., None]) -> None:
        """Register a callback for an event."""
        self.events.setdefault(event_name, []).append(callback)

    def once(self, event_name: str, callback: Callable[..., None]) -> None:
        """Register a callback that will be called only once."""

        def wrapper(*args, **kwargs):
            self.off(event_name, wrapper)
            callback(*args, **kwargs)

        self.on(event_name, wrapper)

    def off(self, event_name: str, callback: Callable[..., None]) -> None:
        """Remove a specific callback for an event."""
        if event_name in self.events:
            self.events[event_name] = [
                cb for cb in self.events[event_name] if cb != callback
            ]
            if not self.events[event_name]:
                self.events.pop(event_name, None)

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event, invoking all registered callbacks."""
        for callback in self.events.get(event_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Error in '{event_name}' callback: {e}")
                raise RuntimeError(f"An error occurred on a '{event_name}' callback.") from e
