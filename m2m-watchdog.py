#!/usr/bin/python
__author__ = 'ptonini'

import sys

from service import Service
from cronjob import Cronjob


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
            print 'Service', service.name, 'is leaking memory', service.heap_usage
            service.daemon('restart')
        else:
            if verbose and service.is_java:
                print 'Service', service.name, 'is not leaking memory'


def main():
    service_list = [
        ['M2M Gateway', '/home/ptonini/m2m_gateway/m2m_gateway.pid', '/home/ptonini/m2m_gateway/m2mgtw', 2800, True]]

    if len(sys.argv) == 1:
        run(service_list, False)
    else:
        if sys.argv[1] == '-v':
            run(service_list, True)
        else:
            cronjob = Cronjob(sys.argv[0])
            if sys.argv[1] == '-s':
                cronjob.set(sys.argv[2])
            elif sys.argv[1] == '-d':
                cronjob.delete()
            elif sys.argv[1] == '-i':
                if cronjob.is_on_crontab():
                    print 'The cronjob is set to every', cronjob.interval, 'minutes'
                    for line in service_list:
                        print 'Monitoring service', line[0]
                else:
                    print 'The cronjob is no set'
            else:
                print 'Invalid option'
                sys.exit(1)


if __name__ == '__main__':
    main()
