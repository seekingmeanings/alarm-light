#!/usr/bin/env python3

import time
from flask import Flask, request
from flask_restful import Api, Resource, reqparse

#from aiy.pins import PIN_A
#from gpiozero import LED

from lib.alarm import Alarm
from lib.daemon import Daemon

import queue
from threading import RLock

import logging
import argparse

class SafeQueue(queue.Queue):
    def __init__(self):
        super().__init__()
        self._lock = RLock()

    def locked_access(f):
        def wrapper(*args, **kwargs):
            with args[0]._lock:
                return super(queue.Queue,
                             args[0]).f(*args, **kwargs)
        return wrapper

    def put(self, itm):
        with self._lock:
            super().put(itm)

    def get(self):
        with self._lock:
            # weird workaround, but wfm
            if super().empty():
                return
            return super().get()




class AlarmAccess(Resource):
    def __init__(self, alarms):
        super().__init__()
        self.alarms = alarms

    def get(self):
        p = reqparse.RequestParser()
        p.add_argument("id",  location="args",  type=int,  required=False,  default=None)
        pargs = p.parse_args()
        if pargs.id:
            try:
                return {pargs.id: self.alarms[pargs.id]},  200
            except IndexError:
                return {"not found"},  404
        return self.alarms,  200

    def post(self):
        p = reqparse.RequestParser()
        p.add_argument("time",  location="args", type=int, required=True)
        pargs = p.parse_args()
        
        # safe definition
        n = len(self.alarms)
        self.alarms[n] = Alarm(id=n,  time=pargs.time)
        return

    def delete(self):
        p = reqparse.RequestParser()
        p.add_argument("id",  location="args",  type=int,  required=True)
        pargs = p.parse_args()
        del(self.alarms[pargs.id])


class AlarmServer(Daemon):
    def __init__(self, host, port):
        self.queue = SafeQueue()
        self.alarms = {}

        self.app = Flask(__name__)
        self.api = Api(self.app)

        self.api.add_resource(AlarmAccess, "/rest",
                              resource_class_kwargs={"alarms": self.alarms})
        logging.info("initialized api")

    def run(self):
        # start a thread
        pass


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int,
                   help="port of the server", default=5034)
    p.add_argument("--host", type=str, default="localhost", help="hostname")
    p.add_argument("-d", "--daemon", action="store_true")
    pargs = p.parse_args()

    logging.basicConfig(level=logging.INFO)

    AlarmServer(pargs.host, pargs.port)
