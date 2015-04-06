__author__ = 'ptonini'

import os
import sys
import socket
import time
import subprocess
import re

import psutil

from crunner import CommandRunner


class Service(CommandRunner):
    timeout = 3
    thresh = 99


    def __init__(self, name, pidfile, script, port, is_java):
        self.name = name
        self.pidfile = pidfile
        self.__validate_script(script)
        self.__validate_port(port)
        self.is_java = is_java

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
            print 'Error: Invalid port for', self.name
            sys.exit(1)

    def __check_usage(self, usage):
        if usage <= float(self.thresh):
            return 0
        else:
            return 1

    def __calc_avg(self, list):
        sum = 0
        for item in list:
            sum += item
        return sum / len(list)

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
            eden, old = list(), list()
            for counter in range(self.timeout):
                try:
                    output = subprocess.check_output(['LANG=C; /usr/bin/jstat -gcutil ' + str(self.pid)],
                                                     stderr=self.devnull, shell=True)
                except:
                    print 'Error: could not attach to ' + self.name
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
