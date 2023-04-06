"""Generic linux daemon base class for python 3.x.

from: http://web.archive.org/web/20131017130434/\
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
cc: Unknown
"""

import sys
import os
import time
import atexit
import signal


class Daemon:
    """
    "A generic daemon class.
    Usage: subclass the daemon class and overide the run() method
    """

    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        """
        Daemonize class. UNIX double fork mechanism.
        """

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            raise RuntimeError("fork 1 failed") from err

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.unmask(0)

        # do second for
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            raise RuntimeError("fork 2 failed") from err

        # redirect standart file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(f"{pid}\n")

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        start the daemon
        """

        # check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            sys.stderr.write(f"pidfile {self.pidfile} already exists." +
                             "Daemon already running?\n")
            sys.exit(0)

        # start the Daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        stop the daemon
        """

        # get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            sys.stderr.write(f"pidfile {self.pidfile} does not exist" +
                             "Daemon not running?\n")
            return  # not an error in a restart

        # try killing the Daemon process
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                raise RuntimeError("couldnt kill") from err

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by
        start() or restart()
        """
