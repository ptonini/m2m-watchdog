__author__ = 'ptonini'

import subprocess
import sys

from crunner import CommandRunner


class Cronjob(CommandRunner):
    cronfile = '/tmp/cronfile.tmp'
    crontab = list()
    is_set = False
    interval = None

    def __init__(self, filename):
        self.filename = filename

    def __read_crontab(self):
        try:
            cur_crontab = subprocess.check_output(['crontab', '-l'], stderr=self.devnull).split('\n')
        except:
            pass
        else:
            for line in cur_crontab:
                if not line.startswith('#') and line != '' and self.filename not in line:
                    self.crontab.append(line)
                elif self.filename in line and self.interval == None:
                    self.interval = line.split(' ')[0][2:]
                    self.is_set = True

    def __write_crontab(self):
        file = open(self.cronfile, 'w')
        for line in self.crontab:
            file.write(line + '\n')
        file.close()
        if self.crontab == []:
            subprocess.call(['crontab', '-r'], stderr=self.devnull)
        else:
            try:
                subprocess.call(['crontab', self.cronfile], stderr=self.devnull)
            except:
                print 'Error: could not alter crontab'
                sys.exit(1)

    def set(self, interval):
        self.interval = interval
        self.__read_crontab()
        self.crontab.append('*/' + self.interval + ' * * * * ' + self.filename + ' | logger -t m2m-watchdog 2>&1')
        self.__write_crontab()
        print 'The cronjob is set to every ', self.interval, ' minutes'

    def delete(self):
        self.__read_crontab()
        self.__write_crontab()
        print 'The cronjob was removed'

    def is_on_crontab(self):
        self.__read_crontab()
        if self.is_set:
            return True
        else:
            return False