class EventDispatcher:
    def __init__(self):
        self._events = {}

    def on_event(self, event_name):
        def decorator(func):
            self._events.setdefault(event_name, []).append(func)
            return func
        return decorator

    def dispatch(self, event_name, *args, **kwargs):
        for func in self._events.get(event_name, []):
            func(*args, **kwargs)


# Usage

dispatcher = EventDispatcher()

@dispatcher.on_event("startup")
def on_startup():
    print("Startup event triggered")

@dispatcher.on_event("shutdown")
def on_shutdown():
    print("Shutdown event triggered")

# Triggering events
dispatcher.dispatch("startup")
dispatcher.dispatch("shutdown")