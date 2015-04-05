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


class Service():

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
            print 'Error: Invalid port for ' + self.name
            sys.exit(1)

    def __check_usage(self, usage):
        if usage <= float(self.thresh):
            return 0
        else:
            return 1

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

    def is_leaking(self):
        if self.is_java:
            eden = list()
            old = list()
            for counter in range(self.timeout):
                try:
                    output = subprocess.check_output(['/usr/bin/jstat', '-gcutil', str(self.pid)], stderr=PIPE)
                    r1 = re.compile('\s{2,}')
                    r2 = re.compile(',')
                    result = r1.sub(' ', output.split('\n')[1]).split(' ')
                    eden.append(float(r2.sub('.', result[3])))
                    old.append(float(r2.sub('.', result[4])))
                except:
                    print 'Error: could not attach to ' + self.name
                    sys.exit(1)
                time.sleep(1)

            self.eden_avg = self.__calc_avg(eden)
            self.old_avg = self.__calc_avg(old)
            self.heap_usage = str(self.eden_avg) + ', ' + str(self.old_avg)

            if self.__check_usage(self.eden_avg):
                return True
            if self.__check_usage(self.old_avg):
                return True
            return False
        else:
            return False

    def daemon(self, option):
        subprocess.call([self.script, option])


class Cronjob():

    cronfile = '/tmp/cronfile.tmp'

    def __init__(self, filename, interval):

        self.filename = filename
        self.interval = interval

    def __get_crontab(self):
        try:
            old_crontab = subprocess.check_output(['crontab', '-l'], stderr=PIPE).split('\n')
            print old_crontab
            new_crontab = list()
            for line in old_crontab:
                if not re.match('^#.*', line) and line != '' and self.filename not in line:
                    new_crontab.append(line)
            self.crontab = new_crontab
        except:
            self.crontab = list()
        print self.crontab

    def __write_crontab(self):
        if self.crontab == []:
            subprocess.call(['crontab', '-r'], stderr=PIPE)
        else:
            try:
                subprocess.call(['crontab', self.cronfile], stderr=PIPE)
            except:
                print 'Error: could not create crontab'
                sys.exit(1)

    def set(self):
        self.__get_crontab()
        file = open(self.cronfile, 'w')
        self.crontab.append('*/' +  self.interval + ' * * * * ' +  self.filename + ' | logger -t m2m-watchdog 2>&1')
        print self.crontab
        for line in self.crontab:
            file.write(line + '\n')
        file.close()
        self.__write_crontab()


    def delete(self):
        self.__get_crontab()
        self.__write_crontab()


def run(service_list, verbose):
    for name, pidfile, script, port, is_java in service_list:
        service = Service(name, pidfile, script, port, is_java)
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
            print 'Service', service.name, 'is leaking memory (' + service.heap_usage + ')'
            service.daemon('restart')
        else:
            if verbose and service.is_java:
                print 'Service', service.name, 'is not leaking memory (' + service.heap_usage + ')'

def main():

    service_list = [['M2M Gateway', '/home/ptonini/m2m_gateway/m2m_gateway.pid', '/home/ptonini/m2m_gateway/m2mgtw', 2800, True]]

    if len(sys.argv) == 1:
        run(service_list, False)
    else:
        if sys.argv[1] == '-v':
            run(service_list, True)
        elif sys.argv[1] == '-s':
            cronjob = Cronjob(sys.argv[0], sys.argv[2])
            cronjob.set()
        elif sys.argv[1] == '-d':
            cronjob = Cronjob(sys.argv[0], None)
            cronjob.delete()



if __name__ == '__main__':
    main()
