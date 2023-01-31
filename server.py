import time
import socket as sc
from netifaces import ifaddresses, AF_INET # interfaces not needed?

from aiy.pins import PIN_A
from gpiozero import LED


def get_status():
    """
    get tbe current state of the pin and return it
    """
    # use time
    pass


def set_status(desire: bool):
    if desire:
        relay.on()
    elif desire is False:
        relay.off()
    else:
        raise RuntimeError

# class for timed activiation


class TimedQueue:
    pass


# local binding address and port
PORT = 40753
IP_HOST = ifaddresses("wlan0").setdefault(AF_INET, [{'addr': None}])[0]['addr']
IDENTS = {213: get_status, 214: set_status}

# Relay init
relay = LED(PIN_A)


asct = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
asct.bind((IP_HOST, PORT))

asct.listen()

while True:
    c, addr = asct.accept()

    with c:
        while True:
            d = tuple(c.recv(1024))
            if not d:
                break
            try:
                c.sendall(bytes(IDENTS[int(d[0])](*d[:1])))
            except IndexError as e: # not an known identifier
                raise RuntimeError(f"non capisco nulla: {d}") from e
