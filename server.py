#!/usr/bin/python3
import time
import socket as sc
from netifaces import ifaddresses, AF_INET # interfaces not needed?

from aiy.pins import PIN_A
from gpiozero import LED

from lib.daemon import Daemon
from queue import Queue


class TimeHandler(Daemon):
    transfer_codes = {213: get_status, 214: set_status}  # ??????

    def __init__(self, port, interface='wlan0', listening_ip=None):
        self._port = port  # make safe randint
        super().__init__(f"{self._port}.pidfile")
        
        self._listen_ip = listening_ip if listening_ip \
            else ifaddresses(interface)
                .setdefault(AF_INET, 
                            [{'addr': None}])[0]['addr']

        self.relay = LED(Pin_A)    
        self.queue = Queue()

    def get_status(self):
        """
        get tbe current state of the pin and return it
        """
        return self.relay.is_lit

    def get_queue(self):
        return self.queue


    def run(self):
        # TODO: make safe bind
        self.asct = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        self.asct.bind((self._listen_ip, self._port))

        self.asct.listen()

        while True:
            c, addr = self.asct.accept()
            with c:
                while True:
                    d = tuple(c.recv(1024))
                    if not d:
                        break
                    try:
                        # lazy shortcut to call the right function
                        # TODO: sign function return with time
                        c.sendall(bytes(IDENTS[int(d[0])](*d[:1])))
                    except IndexError as e: # not an known identifier
                        raise RuntimeError(f"non capisco nulla: {d}") from e


if __name__ == "__main__":
    daemon = TimeHandler(6434)
    daemon.start()