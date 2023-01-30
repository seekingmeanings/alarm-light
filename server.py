import socket as sc
from netifaces import interfaces, ifaddresses, AF_INET #interfaces not needed?

import time

#from aiy.pins import PIN_A
#from gpiozero import LED


from pprint import pprint as pp


def test_server(addr):
    with sc.socket(sc.AF_INET, sc.SOCK_STREAM) as active_sct:
        active_sct.bind(addr)
        active_sct.listen()

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
#PORT = 40753
#IP_HOST = ifaddresses("wlan0").setdefault(AF_INET, [{'addr':None}])[0]['addr']

test_server(('localhost', 20876))
