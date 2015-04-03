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
        self.__get_pid(pidfile)
        self.__validate_port(port)

    def __get_pid(self, pidfile):
        if os.path.isfile(pidfile):
            with open(pidfile, "r") as f:
                self.pid = int(f.read())
        else:
            print 'Error: Invalid pidfile for ' + self.name
            sys.exit(1)
        if not isinstance(self.pid, (int, long)):
            print 'Error: Invalid PID for ' + self.name
            sys.exit(1)

    def __validate_port(self, port):
        if port == None:
            self.port = None
        elif 0 < int(port) < 65536:
            self.port = port
        else:
            print 'Error: Invalid port for ' + self.name
            sys.exit(1)

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
        if self.is_java:
            pass
        else:
            return False

    def start(self):

        pass


