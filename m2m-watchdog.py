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
        self.pidfile = pidfile
        self.__validate_script(script)
        self.__validate_port(port)
        self.is_java = is_java
        self.thresh = thresh

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
            return False
        else:
            return False

    def daemon(self, option):
        print subprocess.call([self.script, option])


class Cronjob():

    def __init__(self, filename, interval):
        self.filename = filename
        self.interval = interval

    def set(self):
        pass

    def delete(self):
        pass


def run(service_list, verbose):
    for name, pidfile, script, port, is_java, thresh in service_list:
        service = Services(name, pidfile, script, port, is_java, thresh)
        if service.is_not_running():
            print 'Service', service.name, 'is not running'
            service.daemon('start')
        else:
            if verbose:
                print 'Service', service.name, 'is running'

        if service.is_not_responding():
            print 'Service', service.name, 'is not responding'
            service.daemon('restart')
        else:
            if verbose and service.port is not None:
                print 'Service', service.name, 'is responding'

        if service.is_leaking():
            print 'Service', service.name, 'is leaking memory'
            service.daemon('restart')
        else:
            if verbose and service.is_java:
                print 'Service', service.name, 'not leaking memory'



service_list = [['M2M Adapter', '/var/run/m2m-adapter.pid','/etc/init.d/m2m-adapter', None, True, '90:99']]



if len(sys.argv) == 1:
    run(service_list, False)
else:
    if sys.argv[1] == '-v':
        run(service_list, True)
