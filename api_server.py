#!/usr/bin/env python3

import time
from flask import Flask, request
from flask_restful import Api, Resource, reqparse

#from aiy.pins import PIN_A
#from gpiozero import LED

from lib.alarm import Alarm, AlarmList
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
        p.add_argument("id", location="args", type=int,
                       required=False, default=None)
        pargs = p.parse_args()
        if pargs.id:
            try:
                return self.alarms.get_alarm(pargs.id), 200
            except IndexError:
                return {"not found"},  404
        return self.alarms.data, 200  # FIXME: need __repr__

    def post(self):
        p = reqparse.RequestParser()
        p.add_argument("time", location="args", type=int, required=True)
        pargs = p.parse_args()

        # store time as struct_time

        new_alarm = Alarm(time=pargs.time)
        # add to list and generate id
        self.alarms.add_alarm(new_alarm)
        return new_alarm, 200

    def delete(self):
        p = reqparse.RequestParser()
        p.add_argument("id", location="args",  type=int,  required=True)
        pargs = p.parse_args()
        self.alarms.delete_alarm(pargs.id)


class AlarmServer(Daemon):
    def __init__(self, host, port):
        self.queue = SafeQueue()
        self.alarms = AlarmList()

        self.app = Flask(__name__)
        self.api = Api(self.app)

        self.api.add_resource(AlarmAccess, "/rest",
                              resource_class_kwargs={"alarms": self.alarms})
        logging.info("initialized api")

    def run(self):
        # TODO: start two threads
        self.app.run()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int,
                   help="port of the server", default=5034)
    p.add_argument("--host", type=str, default="localhost", help="hostname")
    p.add_argument("-d", "--daemon", action="store_true")
    pargs = p.parse_args()

    logging.basicConfig(level=logging.INFO)

    server = AlarmServer(pargs.host, pargs.port)

    if pargs.daemon:
        server.start()
    else:
        server.run()

