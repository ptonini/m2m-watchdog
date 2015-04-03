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
        self.is_java = is_java
        self.thresh = thresh
        self.pidfile = pidfile
        self.__validate_port(port)
        self.__validate_script(script)

    def __validate_script(self, script):
        if os.path.isfile(script):
            self.script = script
        else:
            print 'Error: Invalid init script for', self.name

    def __validate_port(self, port):
        if port == None:
            self.port = None
        elif 0 < int(port) < 65536:
            self.port = port
        else:
            print 'Error: Invalid port for ' + self.name
            sys.exit(1)

    def is_not_running(self):
        if os.path.isfile(self.pidfile):
            with open(self.pidfile, "r") as f:
                self.pid = int(f.read())
            try:
                psutil.pid_exists(self.pid)
                return False
            except:
                return True
        else:
            return True

    def is_not_responding(self):
        if self.port != None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', self.port))
                s.close()
                return False
            except:
                return True
        else:
            return False

    def is_leaking(self):
        if self.is_java:
            pass
        else:
            return False

    def daemon(self, option):
        print subprocess.call([self.script, option])


service = Services('MySQL', '/var/run/mysqld/mysqld.pid','/etc/init.d/mysql', 3306, False, None)

print service.name
print service.pidfile
if service.is_not_running():
    print 'Service', service.name, 'is not running'
else:
    print 'Service', service.name, 'is running'
#service.daemon('start')