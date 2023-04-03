#!/usr/bin/env python3

from time import struct_time


class Alarm:
    def __init__(self, id: int = None,
                 time: struct_time = None):
        self._id = id
        self._time = time

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int):
        print("fcalled with: {id}")
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

    def to_json(self) -> dict:
        return {"id": self.id, "time": self.time}

    def from_json(self, data: dict):
        self.time = data['time']
        self.id = data['id']


class AlarmGroup:
    def __init__(self):
        pass

    def add_alarm(self):
        pass

    def delete_alarm(self):
        pass


