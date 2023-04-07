#!/usr/bin/python3

import subprocess as sp

import argparse
import json
import time

from lib.daemon import Daemon
from lib.utils import termux_api_toast as toast


WORK_DIR = "/data/data/com.termux/files/home/alarm-light"


def check_for_upcoming_alarm():  # old
    with sp.Popen("termux-notification-list", stdout=sp.PIPE) as opt:
        opt.wait()

        notifications = json.loads(str().join([str(line.decode('utf-8')
                                                   .replace('\n', ''))
                                               for line in opt.stdout]))
    next_alarm = []

    for n in notifications:
        if n['packageName'] == "com.google.android.deskclock"\
           and n['title'] == "Upcoming alarm" and int(n['group']) == 1:
            next_alarm.append(time.strptime(n['content'].join(''), '%a %H:%M'))
            toast(f"alarm found: {next_alarm[-1]}")


class AlarmDaemon(Daemon):
    class Notification:
        def __init__(self, nid):
            self.nid = nid

        def kill(self):
            sp.run(["termux-notification-remove", str(self.nid)], check=True)

        def update(self, status: str):
            sp.run(["termux-notification", "-i", str(self.nid),
                    "--ongoing", "--button1", "on", "--button1-action",
                    f"python3 {WORK_DIR}/pre_alarm_daemon.py --on",
                    "--button2", "off", "--button2-action",
                    f"python3 {WORK_DIR}/pre_alarm_daemon.py --off",
                    "--button3", "kill daemon", "--button3-action",
                    f"python3 {WORK_DIR}/pre_alarm_daemon.py -d -k",
                    "-t", "bed light", '-c', str(status)],
                   check=True)

    def __init__(self):  # , credentials):
        super().__init__()  # pidfile needed here
        self.alarm_buffer = []

        self.notification = self.Notification(98)
        self.alarm_flags = {"packageName": "com.google.android.deskclock",
                            "title": "Upcoming alarm", "group": 1}

    def run(self):
        pass

    def stop(self):
        super().stop()

    def get_alarms(self):
        with sp.run.run(["termux-notification-list"], shell=True,
                        capture_output=True, timeout=10, text=True,
                        check=True) as opt:
            return [time.strptime(n['content'].join(''), '%a %H:%M')
                    for n in json.loads("".join(
                        [str(line.decode('utf-8').replace('\n', ''))
                         for line in opt.stdou]))
                    if all(self.alarm_flags[flag] == n[flag]
                           for flag in self.alarm_flagsr)]

    def collect_upcoming_alarms(self, alarm_notifications):
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

        # make it iterative
        self.alarm_buffer.append(time.strptime(
            alarm_notifications['content'].join(''), '%a %H:%M'))
        toast(f"alarm found: {self.alarm_buffer[-1]}")

    def notification_switch(self):  # add last updated as content
        sp.run(["termux-notification", "-i", str(self.nid),
                "--ongoing", "--button1", "on", "--button1-action",
                f"python3 {WORK_DIR}/pre_alarm_daemon.py --on",
                "--button2", "off", "--button2-action",
                f"python3 {WORK_DIR}/pre_alarm_daemon.py --off",
                "--button3", "kill daemon", "--button3-action",
                f"python3 {WORK_DIR}/pre_alarm_daemon.py -d -k",
                "-t", "bed light"], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemon", action="store_true")
    parser.add_argument("-k", "--kill", action="store_true")

    parser.add_argument("--off", action="store_true")
    parser.add_argument("--on", action="store_true")

    args = parser.parse_args()

    daemon = AlarmDaemon()

    # need a parse function

    if args.daemon:
        if args.kill:
            daemon.stop()
        daemon.start()

    else:
        # parse args
        pass
