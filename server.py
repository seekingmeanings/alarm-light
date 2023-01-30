import socket as sc
from netifaces import interfaces, ifaddresses, AF_INET #interfaces not needed?
import time

from aiy.pins import PIN_A
from gpiozero import LED



from pprint import pprint as pp


def test_server(addr):
        conn, addr = active_sct.accept()

        with conn:
            print(addr)

            while True:
                data = conn.recv(1024)
                if not data:
                    break
                pp(data)
                conn.sendall(data)



# local binding address and port
PORT = 40753
IP_HOST = ifaddresses("wlan0").setdefault(AF_INET, [{'addr':None}])[0]['addr']


asct = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
asct.bind((IP_HOST, PORT))

asct.listen()

while True:
    c, addr = asct.accept()

    with c:
        while True:
            d = list(c.recv(1024))
            if not d:
                break
            elif 