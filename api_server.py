#!/usr/bin/env python3

from dataclasses import dataclass
import time
from flask import Flask  # , request
from flask_restful import Api, Resource, reqparse

# from aiy.pins import PIN_A
# from gpiozero import LED

from lib.alarm import Alarm, AlarmList
from lib.daemon import Daemon

from threading import Thread

from lib.relay import Relay
from lib.relay import DummyRelay

import logging
import argparse


class ConfigEndpoint(Resource):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def get(self):
        d = {}
        for a in dir(self.config):
            if not a.startswith("_") and not callable(a):
                d[a] = getattr(self.config, a)
        print(d)
        return d, 200

    def post(self):
        p = reqparse.RequestParser()
        p.add_argument("var", type=str,
                       required=True, location="args")
        p.add_argument("type", type=str, required=True, location="args")
        p.add_argument("val", required=True, location="args")
        pargs = p.parse_args()

        try:
            match pargs.type:
                case "str":
                    converted_val = str(pargs.val)
                case "int":
                    converted_val = int(pargs.val)
                case "dict":
                    converted_val = dict(pargs.val)
                case "list":
                    converted_val = list(pargs.val)
                case _:
                    raise TypeError()
        except TypeError:
            return {"message": "unknown type"}, 400
        setattr(self.config, pargs.var, converted_val)

        return {pargs.var: converted_val}, 200


class AlarmEndpoint(Resource):
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
        return {"alarms": self.alarms.list_all()}, 200

    def post(self):
        p = reqparse.RequestParser()
        p.add_argument("time", location="args", type=int, required=True)
        pargs = p.parse_args()

        # store time as struct_time

        new_alarm = Alarm(time=pargs.time)
        # add to list and generate id
        self.alarms.add_alarm(new_alarm)

        logging.info(f"created alarm {new_alarm}")
        return new_alarm.to_json(), 200

    def delete(self):
        p = reqparse.RequestParser()
        p.add_argument("id", location="args", type=int, required=True)
        pargs = p.parse_args()
        self.alarms.delete_alarm(pargs.id)


class StateEndpoint(Resource):
    def __init__(self, relay):
        self.relay = relay

    def get(self):
        return {"state": self.relay.get_state()}, 200

    def post(self):
        p = reqparse.RequestParser()
        p.add_argument("state", location="args", type=bool, required=True)
        pargs = p.parse_args()

        self.relay.set_state(pargs.state)
        return self.get()


class AlarmServer(Daemon):
    @dataclass
    class Config:
        on_before_alarm_time = 1800
        alarm_check_precision = 2

    def __init__(self, host: str, port: int, dummy_relay=False):
        self.config = self.Config()
        self.alarms = AlarmList()

        # FIXME: call contstructor with arguments
        self.relay = DummyRelay() if dummy_relay else Relay()

        # temporary store items
        self._host = host
        self._port = port

        # configure api
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(AlarmEndpoint, "/rest/alarm",
                              resource_class_kwargs={"alarms": self.alarms})
        self.api.add_resource(ConfigEndpoint, "/rest/config",
                              resource_class_kwargs={"config": self.config})
        self.api.add_resource(StateEndpoint, "/rest/state",
                              resource_class_kwargs={"relay": self.relay})
        logging.info("initialized api")

        self.api_thread_hook = Thread(target=self.start_api, daemon=True)
        self.led_thread_hook = Thread(target=self.led_thread, daemon=True)
        logging.info("threads initialized")

    def start_api(self):
        logging.info(f"starting api thread on {self._host}")
        self.app.run(self._host)

    def led_thread(self):
        while True:
            for alarm in self.alarms.all.values():
                if time.time() + self.config.on_before_alarm_time > alarm.time:
                    logging.info("ring, ring")
                    self.relay.set_state(True)
                    # alarm has been used so we can delete it
                    self.alarms.delete_alarm(alarm)
                    # need to start iteration again cause the array changed
                    break
            time.sleep(self.config.alarm_check_precision)

    def button_thread(self):
        pass

    def run(self):
        self.api_thread_hook.start()
        self.led_thread_hook.start()

        self.api_thread_hook.join()
        self.led_thread_hook.join()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int,
                   help="port of the server", default=5034)
    p.add_argument("--host", type=str, default="localhost", help="hostname")
    p.add_argument("-d", "--daemon", action="store_true")
    p.add_argument("-k", "--kill", action="store_true",
                   help="kill a running daemon")
    p.add_argument("--dummy", action="store_true",
                   help="uses a dummy relay for testing")
    pargs = p.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    server = AlarmServer(pargs.host, pargs.port, pargs.dummy)

    if pargs.daemon:
        if pargs.kill:
            raise NotADirectoryError()
        else:
            server.start()
    else:
        server.run()
