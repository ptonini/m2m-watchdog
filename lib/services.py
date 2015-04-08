__author__ = 'ptonini'

import os
import sys
import socket
import time
import subprocess
import re

import psutil

from lib.crunner import CommandRunner


class Service(CommandRunner):
    def __init__(self, name, pidfile, script, port, is_java, sampling, threshold):
        self.name = name
        self.__validate_script(script)
        self.__validate_port(port)
        self.__validate_pid(pidfile)
        self.is_java = is_java
        self.sampling = sampling
        self.thresh = threshold

    def __validate_script(self, script):
        if os.path.isfile(script):
            self.script = script
        else:
            print 'Error: Invalid init script for', self.name

    def __validate_port(self, port):
        if port == '':
            self.port = None
        elif 0 < int(port) < 65536:
            self.port = int(port)
        else:
            print 'Error: Invalid port for', self.name
            sys.exit(1)

    def __validate_pid(self, pidfile):
        try:
            if os.path.isfile(pidfile):
                with open(pidfile, 'r') as f:
                    self.pid = int(f.read())
        except Exception:
            print 'Error: Invalid pidfile for', self.name
            sys.exit(1)

    def __check_usage(self, usage):
        if usage <= float(self.thresh):
            return True
        else:
            return False

    def __calc_avg(self, list):
        sum = 0
        for item in list:
            sum += item
        return sum / len(list)

    def is_not_running(self):
        try:
            psutil.pid_exists(self.pid)
        except Exception:
            return True
        else:
            return False

    def is_not_responding(self):
        if self.port != None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(('localhost', self.port))
            except Exception:
                return True
            else:
                s.close()
                return False
        else:
            return False

    def is_leaking(self):
        if self.is_java:
            eden, old = list(), list()
            for counter in range(self.sampling):
                try:
                    output = subprocess.check_output(['/usr/bin/jstat', '-gcutil', str(self.pid)],
                                                     stderr=self.devnull, env={'LANG': 'C'})
                except Exception:
                    print 'Error: could not attach to', self.name
                    sys.exit(1)
                else:
                    status_line = output.split('\n')[1].lstrip()
                    values = re.split('\s{1,}', status_line)
                    eden.append(float(values[2]))
                    old.append(float(values[3]))
                    time.sleep(1)
            self.eden_avg = self.__calc_avg(eden)
            self.old_avg = self.__calc_avg(old)
            self.heap_usage = self.eden_avg, self.old_avg
            if self.__check_usage(self.eden_avg) and self.__check_usage(self.old_avg):
                return True
            else:
                return False
        else:
            return False

    def daemon(self, option):
        subprocess.call([self.script, option])
