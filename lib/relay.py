from threading import RLock
from lib.utils import locked


class DummyRelay:
    def __init__(self):
        self._state = False
        self._lock = RLock()

    @locked
    def get_state(self) -> bool:
        return self._state

    @locked
    def set_state(self, state: bool):
        self._state = state


class Relay:
    def __init__(self, pin_instance):
        self._relay = pin_instance
        self._lock = RLock()

    @locked
    def get_state(self) -> bool:
        return self._relay.is_lit

    @locked
    def set_state(self, state: bool):
        match state:
            case True:
                self._relay.on()
            case False:
                self._relay.off()
            case _:
                raise TypeError(f"state {state} is not a bool")



