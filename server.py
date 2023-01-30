import socket as sc
from netifaces import interfaces, ifaddresses, AF_INET #interfaces not needed?
import time

from aiy.pins import PIN_A
from gpiozero import LED



from pprint import pprint as pp


def test_server(addr):
        conn, addr = active_sct.accept()
        conn.sendall(data)

def get_status():
    pass

def set_status(status: bool):
    

#class timed activiation


# local binding address and port
PORT = 40753
IP_HOST = ifaddresses("wlan0").setdefault(AF_INET, [{'addr':None}])[0]['addr']
IDENTS = {213: get_status, 214: set_status}


asct = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
asct.bind((IP_HOST, PORT))

asct.listen()

while True:
    c, addr = asct.accept()

    with c:
        while True:
            d = tuple(c.recv(1024))
            if not d or not:
                break
            try:
                c.sendall(bytes(IDENTS[int(d[0])](d[:1])))
            except IndexError as e: #not an known identifier
                raise RuntimeError(f"non capisco nulla: {d}\n\n{e}")
