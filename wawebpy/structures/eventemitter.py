from typing import Callable, Dict, List, Any

class EventEmitter:
    """
    Simple event emitter class to register and emit events.

    Allows multiple callbacks per event name and supports passing
    arbitrary arguments to the callbacks.
    """

    def __init__(self):
        """
        Initializes the EventEmitter with an empty dictionary
        to store events and their associated callbacks.
        """
        self.events: Dict[str, List[Callable[..., None]]] = {}

    def on(self, event_name: str, callback: Callable[..., None]) -> None:
        """
        Registers a callback function for a given event name.

        Args:
            event_name: The name of the event to listen for.
            callback: The function to be called when the event is emitted.
        """
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event, calling all registered callbacks with the provided arguments.

        Args:
            event_name: The name of the event to emit.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.
        """
        for callback in self.events.get(event_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error in '{event_name}' callback: {e}")
