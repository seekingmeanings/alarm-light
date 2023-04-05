#!/usr/bin/env python3

from time import struct_time
from typing import Union, NewType


class Alarm:
    @property
    def id(self) -> int:
        """
        Public method getter self.id

        @return id
        @rtype int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """
        Public method setter self.id

        @param id
        @type int
        @exception TypeError immutalble
        """
        if self._id:
            raise TypeError("immutable")
        self._id = int(id)

    @property
    def time(self) -> struct_time:
        return self._time

    @time.setter
    def time(self, time: struct_time):
        if self._time:
            raise TypeError("immutable")
        self._time = struct_time(time)

    def __init__(self, id: int = None,
                 time: struct_time = None):
        """
        represents an alarm with time
        """
        self._id = None
        self._time = None

        # safe declaration
        if id:
            self.id = id
        if time:
            self.time = time

    def from_dict(self,  data: dict):
        self.id = data['id']
        self.time = data['time']

    def to_json(self) -> dict:
        return {"id": self.id, "time": self.time}

    def from_json(self, data: dict):
        self.time = data['time']
        self.id = data['id']


class AlarmList:

    AutomaticID = NewType('AutomaticID', Union[int, Alarm])

    def __init__(self):
        self.alst = {}

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
            s, a = args

            if isinstance(a, Alarm):
                args[1] = a.id
                return func(*args, **kwargs)
            elif isinstance(a, int):
                return func(*args, **kwargs)
            else:
                raise TypeError("cant get id")
        return wrapper

    @_use_id
    def get_alarm(self, id: AutomaticID) -> Alarm:
        return self.alst[id]

    @_use_id
    def delete_alarm(self, id: AutomaticID):
        del self.alst[id]

    @_use_id
    def pop_alarm(self, id: AutomaticID) -> Alarm:
        a = self.get_alarm(id)
        self.delete_alarm(id)
        return a
