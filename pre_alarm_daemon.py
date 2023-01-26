#!/usr/bin/python3

import subprocess as sp
from paramiko import client.SHHClient

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
    
    #close the ssh connection
    

class Remote_Interface: # extends paramiko.client.SSHClient   or just API??
    def __init__(self, host_name, host_port, host_user_name, host_password):
        last_update = None #time.struct_time
        
        def _make_bind(n, p, u, pw):
            ssh_bind = SSHClient()
            ssh_bind.load_system_host_keys()
            try:
                ssh_bind.connect(hostname=str(n), port=int(p),\
                                 username=str(u), password=str(pw))
            except ValueError as e:
                raise ValueError(f"u stoopid:\n{e}")
        
        make_bind(host_name, host_port, host_user_name, host_password)
        # ssh_bind = px.spawn(f"/usr/bin/ssh {user_name}@{address} -p {str(port)})

    def check_connection(self):
        pass

    def set_remote_state(self):
        pass

    def get_remote_state(self):
        pass



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

class alarm_daemon:
    def __init__(self, credentials):
        remote_interface = Remote_Interface(*credentials)

    @staticmethod
    def find_notification():
        with opt as sp.run(["termux-notification-list"], shell=True,\
                           capture_output=True, timeout=5, text=True):

            notifications = json.loads(str().join([str(l.decode('utf-8')\
                                                       .replace('\n', ''))\
                                                   for l in opt.stdout]))
        nots = list()

        for n in notifications:
            if n['packageName'] == "com.google.android.deskclock"\
               and n['title'] == "Upcoming alarm" and int(n['group']) == 1:
                nots.append(n)

        return [ n if (n['packageName'] == "com.google.android.deskclock"\
                       and n['title'] == "Upcoming alarm" and int(n['group']) ==1)\
                 else None
                 for n in notifications ] #remove all occurencys of None

    def collect_upcoming_alarms(self):
        next_alarm.append(strptime(n['content'].join(''), '%a %H:%M'))
        toast(f"alarm found: {next_alarm[-1]}")




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
            #loop???
            check_for_upcoming_alarm()


    if args.on - args.off:
        toast("change of state: ".join(get_remote_state()))
