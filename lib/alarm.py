#!/usr/bin/env python3

from typing import Union, NewType
from threading import RLock


def locked(func):
    def wrapper(*args, **kwargs):
        s = args[0]
        with s._lock:
            return func(*args, **kwargs)
    return wrapper


# user395760 on stackowerflow
def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and not attr.startswith("__"):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


class Alarm:
    sse = NewType('seconds_since_epoch', int)

    @property
    def id(self) -> int:
        """
        Public method getter self.id

        @return id
        @rtype int
        """
        with self._lock:
            return self._id

    @id.setter
    def id(self, id: int):
        """
        Public method setter self.id

        @param id
        @type int
        @exception TypeError immutalble
        """
        with self._lock:
            if self._id:
                raise TypeError("immutable")
            self._id = int(id)

    @property
    def time(self) -> sse:
        with self._lock:
            return self._time

    @time.setter
    def time(self, time: sse):
        with self._lock:
            if self._time:
                raise TypeError("immutable")
            self._time = int(time)

    def __init__(self, id: int = None,
                 time: sse = None):
        """
        represents an alarm with time
        """
        self._lock = RLock()

        self._id = None
        self._time = None

        # safe declaration
        if id:
            self.id = id
        if time:
            self.time = time

    @locked
    def from_dict(self,  data: dict):
        self.id = data['id']
        self.time = data['time']

    @locked
    def to_json(self) -> dict:
        return {"id": self.id, "time": self.time}

    @locked
    def from_json(self, data: dict):
        self.time = data['time']
        self.id = data['id']


class AlarmList:

    AutomaticID = NewType('AutomaticID', Union[int, Alarm])

    def __init__(self):
        self._lock = RLock()
        self.alst = {}

    @locked
    def add_alarm(self, alarm: Alarm):
        if not alarm.id:
            # give him his own id
            n = len(self.alst)
            alarm.id = n
            self.alst[n] = alarm
        else:
            if alarm.id in self.alst:
                raise IndexError("can't assing id, already used")
            self.alst[alarm.id] = alarm

    def _use_id(func):
        def wrapper(*args, **kwargs):
            if len(args) > 2:
                # WARNING: check for id in kwargs
                raise TypeError()
            # make mutable copy
            args = list(args)
            s, a = args

            if isinstance(a, Alarm):
                args[1] = a.id
                return func(*args, **kwargs)
            elif isinstance(a, int):
                return func(*args, **kwargs)
            else:
                raise TypeError("cant get id")
        return wrapper

    @locked
    @_use_id
    def get_alarm(self, id: AutomaticID) -> Alarm:
        return self.alst[id]

    @locked
    @_use_id
    def delete_alarm(self, id: AutomaticID):
        del self.alst[id]

    @locked
    @_use_id
    def pop_alarm(self, id: AutomaticID) -> Alarm:
        a = self.get_alarm(id)
        self.delete_alarm(id)
        return a

    @locked
    def list_all(self) -> list:
        return [a.to_json() for a in self.alst.values()]

    @property
    def all(self) -> dict:
        with self._lock:
            return self.alst
