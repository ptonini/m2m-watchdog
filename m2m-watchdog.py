#!/usr/bin/python
__author__ = 'ptonini'

import os
import socket
import subprocess
from subprocess import PIPE
import sys
import time
import re

import psutil


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

    def __calc_avg(self, list):
        somatory = 0
        for item in list:
            somatory += item
        return somatory / len(list)

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

    def is_leaking(self, verbose):
        if self.is_java:
            eden = list()
            old = list()
            i = 0
            while i < 5:
                try:
                    output = subprocess.check_output(['/usr/bin/jstat', '-gcutil', str(self.pid)], stderr=PIPE)
                    rex1 = re.compile('\s{2,}')
                    rex2 = re.compile(',')
                    result = rex1.sub(' ', output.split('\n')[1]).split(' ')
                    eden.append(float(rex2.sub('.', result[3])))
                    old.append(float(rex2.sub('.', result[4])))
                except:
                    print 'Error: could not attach to pid ' + str(self.pid) + ' (' + self.name + ')'
                    sys.exit(1)
                time.sleep(1)
                i += 1
            eden_avg = self.__calc_avg(eden)
            old_avg = self.__calc_avg(old)
            print eden_avg, old_avg

            return False
        else:
            return False

    def daemon(self, option):
        subprocess.call([self.script, option])


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

        if service.is_leaking(verbose):
            print 'Service', service.name, 'is leaking memory'
            service.daemon('restart')
        else:
            if verbose and service.is_java:
                print 'Service', service.name, 'is not leaking memory'


service_list = [['M2M Adapter', '/var/run/m2m-adapter.pid', '/etc/init.d/m2m-adapter', None, True, '90:99']]

if len(sys.argv) == 1:
    run(service_list, False)
else:
    if sys.argv[1] == '-v':
        run(service_list, True)
