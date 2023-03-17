#!/usr/bin/python3
import time
import socket as sc
from netifaces import ifaddresses, AF_INET # interfaces not needed?

from aiy.pins import PIN_A
from gpiozero import LED

from lib.daemon import Daemon
from queue import Queue


class TimeHandler(Daemon):
    def __init__(self, port, interface='wlan0', listening_ip=None):
        self._port = port  # make safe randint
        super().__init__(f"{self._port}.pidfile")
        
        self._listen_ip = listening_ip if listening_ip \
            else ifaddresses(interface)\
                 .setdefault(AF_INET,
                             [{'addr': None}])[0]['addr']
        self.asct = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        self._package_len = 1024
        
        self.relay = LED(PIN_A)    
        self.queue = Queue()

        self.func_codes = {
            42: self.get_codes,
            213: self.get_status,
            214: self.get_queue
        }

    def get_codes(self) -> dict:
        return self.func_codes
        
    def get_status(self):
        """
        get tbe current state of the pin and return it
        """
        return self.relay.is_lit

    def get_queue(self):
        return self.queue

    def _get_con_data(self, con) -> bytes:
        """
        algorithm from:
        https://docs.python.org/3/howto/sockets.html#socket-howto
        """
        cache = []
        while True:
            cache.append(con.recv(self._package_len))
            if cache[-1] == b'':
                break
        return b''.join(cache)

    def _send_con_data(self, con, data):  # aint that useless
        """
        alorithm from:
        https://docs.python.org/3/howto/sockets.html#socket-howto
        """
        totalsent = 0
        while totalsent < len(data):
            sent = con.send(data[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        
    def run(self):
        with self.asct.bind((self._listen_ip, self._port)) as sc:
            sc.listen()

            while True:
                c, addr = self.asct.accept()
                with c:
                    rec_data = self._get_con_data(c) 
                    try:
                        # lazy shortcut to call the right function
                        # TODO: sign function return with time
                            
                        c.sendall(
                            bytes(
                                transfer_codes[
                                    int(rec_data[0])](
                                        *rec_data[:1])))
                    except IndexError as e: # not an known identifier
                        raise RuntimeError(
                            f"non capisco nulla: {rec_data}") from e


if __name__ == "__main__":
    daemon = TimeHandler(6434)
    daemon.start()