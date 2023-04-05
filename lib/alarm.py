#!/usr/bin/env python3

from time import struct_time


class Alarm:
    @property
    def id(self) -> int:
        """
        Public method 

        @return id
        @rtype int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """
        Public method 

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
        self.id = id
        self.time = time
    

    def from_dict(self,  data: dict):
        self.id,  self.time = *data

    def to_json(self) -> dict:
        return {"id": self.id, "time": self.time}

    def from_json(self, data: dict):
        self.time = data['time']
        self.id = data['id']
