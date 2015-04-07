#!/usr/bin/python
__author__ = 'ptonini'

import sys

import ConfigParser

import lib.services as services
import lib.cronjobs as cronjobs


def read_config(filename):
    service_list = list()
    config = ConfigParser.ConfigParser()
    config.read(filename)
    for section in config.sections():
        service_list.append([section, config.get(section, 'pidfile'), config.get(section, 'script'),
                            config.get(section, 'port'), config.getboolean(section, 'is_java')])
    return service_list

def run(service_list, verbose):
    for name, pidfile, script, port, is_java in service_list:
        service = services.Service(name, pidfile, script, port, is_java)
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

    service_list = read_config('/home/ptonini/m2m_gateway/m2m-watchdog.conf')

    if len(sys.argv) == 1:
        run(service_list, False)
    else:
        if sys.argv[1] == '-v':
            run(service_list, True)
        else:
            cronjob = cronjobs.Cronjob(sys.argv[0])
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
