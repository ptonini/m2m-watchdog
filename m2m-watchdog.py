#!/usr/bin/python
__author__ = 'ptonini'

import sys
import os

import lib.classes as classes
import lib.func as func


def run(service_list, verbose, sampling, threshold):
    for name, pidfile, script, port, is_java in service_list:
        service = classes.Service(name, pidfile, script, port, is_java, sampling, threshold)
        if service.is_running() and verbose:
            print 'Service', service.name, 'is running'
        if  service.need_restart == False and service.is_not_responding():
            print 'Service', service.name, 'is not responding'
        else:
            if verbose and service.port is not None and service.need_restart == False:
                print 'Service', service.name, 'is responding'
        if service.need_restart == False and service.is_leaking():
            print 'Service', service.name, 'is leaking memory'
        else:
            if verbose and service.is_java and service.need_restart == False:
                print 'Service', service.name, 'is not leaking memory'
        if service.need_restart:
            print 'Restarting service ' + service.name + '...',
            service.daemon('restart')


def main():
    cronfile, sampling, threshold, service_list = func.get_config_from_file('./m2m-watchdog.conf')
    if len(sys.argv) == 1:
        run(service_list, False, sampling, threshold)
    else:
        if sys.argv[1] == '-v':
            run(service_list, True, sampling, threshold)
        else:
            cronjob = classes.Cronjob(sys.argv[0], cronfile)
            if sys.argv[1] == '-s':
                cronjob.set(sys.argv[2])
            elif sys.argv[1] == '-d':
                cronjob.delete()
            elif sys.argv[1] == '-i':
                if cronjob.is_set:
                    print 'The cronjob is set to every', cronjob.interval, 'minutes'
                    for line in service_list:
                        print 'Monitoring service', line[0]
                else:
                    print 'The cronjob is not set'
            else:
                print 'Invalid option'
                sys.exit(1)


if __name__ == '__main__':
    if os.geteuid() != 0:
        print 'You need to have root privileges to run this script.'
        sys.exit(1)
    main()