#!/usr/bin/python3

import subprocess as sp
import argparse
import json
from time import strptime

import sys
sys.path.append('/data/data/com.termux/files/home/lib')
from local_utils import toast


from pprint import pprint as pp

NID = 56
WORK_DIR="/data/data/com.termux/files/home/alarm-light"

def check_for_upcoming_alarm():
    opt = sp.Popen("termux-notification-list", stdout=sp.PIPE)
    opt.wait()
    
    notifications = json.loads(str().join([str(l.decode('utf-8').replace('\n', '')) \
                                           for l in opt.stdout]))
    
    next_alarm = list()
    
    for n in notifications:
        if n['packageName'] == "com.google.android.deskclock"\
           and n['title'] == "Upcoming alarm" and int(n['group']) == 1:
            next_alarm.append(strptime(n['content'].join(''), '%a %H:%M'))
            toast(f"alarm found: {next_alarm[-1]}")



def notification_switch(): # add last updated as content
    sp.run(["termux-notification", "-i", str(NID),\
                    "--ongoing", "--button1", "on", "--button1-action",\
                    f"python3 {WORK_DIR}/pre_alarm_daemon.py --on",\
                    "--button2", "off", "--button2-action",\
                    f"python3 {WORK_DIR}/pre_alarm_daemon.py --off",\
                    "--button3", "kill daemon", "--button3-action",
                    f"python3 {WORK_DIR}/pre_alarm_daemon.py -d -k",\
                    "-t", "bed light"], check=True)

def kill_daemon():
    sp.run("termux-notification-remove", str(NID))
    #add for real daemon


class Remote_Interface:
    #make it easier with keys (use shell=True maybe in that case)
    def __init__(self, address, port, user_name, password):
        last_update = None #time.struct_time
        #NOT SAFE
        ssh_bind = sp.Popen(["/usr/bin/ssh", f"{user_name}@{address}",\
                            "-p", str(port)], stderr=sp.PIPE,\
                            stdin=sp.PIPE, stdout=sp.PIPE)

        

    def check_connection(self)
        pass

    def set_remote_state(self):
        pass

    def get_remote_state(self):
        return



""" example notification
{
    "id": 13,
    "tag": "",
    "key": "0|com.google.android.deskclock|13|null|10161",
    "group": "1",
    "packageName": "com.google.android.deskclock",
    "title": "Upcoming alarm",
    "content": "Mon 08:00",
    "when": "2023-01-23 07:01:21"
}
"""



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemon", action="store_true")
    parser.add_argument("-k", "--kill", action="store_true")
    
    parser.add_argument("-f", "--off", action="store_true") 
    parser.add_argument("-t", "--on", action="store_true")
    
    args=parser.parse_args() 


    #make startup check; use groups instead of nid?

    if args.daemon:
        if args.kill:
            kill_daemon()
        else:
            notification_switch()
            check_for_upcoming_alarm()


    if args.on - args.off:
        toast("change of state: ".join(get_remote_state()))
