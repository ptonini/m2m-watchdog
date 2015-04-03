#!/usr/bin/python
__author__ = 'ptonini'

import psutil
import os
import socket
import subprocess
import sys

class Services():

    def __init__(self, name, pidfile, script, port, is_java, thresh):
        self.name = name
        self.script = script
        self.port = port
        self.is_java = is_java
        self.thresh = thresh
        self.get_pid(self, pidfile)

    def get_pid(self, pidfile):
        if os.path.isfile(self.pidfile):
            with open(self.pidfile, "r") as f:
                self.pid = int(f.read())
        else:
            print 'Error: Invalid pidfile for ' + self.name
        if not isinstance(self.pid, (int, long)):
            print 'Error: Invalid PID for ' + self.name

    def is_not_running(self):
        try:
            psutil.pid_exists(self.pid)
            return False
        except:
            return True

    def is_not_responding(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', self.port))
            s.close()
            return False
        except:
            return True

    def is_leaking(self):
        pass

    def start(self):

        pass


def tcp_port(integer):
    if not 0 < int(integer) < 65536:
        msg = 'invalid port: ' + str(integer)
        return 0
    return int(integer)
