__author__ = 'ptonini'

import subprocess
import os

from lib.crunner import CommandRunner


class Cronjob(CommandRunner):
    cronfile = '/tmp/cronfile.tmp'
    crontab = list()
    is_set = False
    interval = None

    def __init__(self, filename):
        self.filename = filename
        try:
            cur_crontab = subprocess.check_output(['crontab', '-l'], stderr=self.devnull).split('\n')
        except Exception:
            pass
        else:
            for line in cur_crontab:
                if not line.startswith('#') and line != '' and self.filename not in line:
                    self.crontab.append(line)
                elif self.filename in line:
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
                subprocess.check_call(['crontab', self.cronfile], stderr=self.devnull)
            except:
                os.remove(self.cronfile)
                print 'Error: could not alter crontab'
                return False
        os.remove(self.cronfile)
        return True


    def set(self, interval):
        if self.is_set and interval == self.interval:
            print 'Cronjob already set to every', interval, 'minutes'
        else:
            self.interval = interval
            self.crontab.append('*/' + self.interval + ' * * * * ' + self.filename + ' | logger -t m2m-watchdog 2>&1')
            if self.__write_crontab():
                print 'The cronjob is set to every', self.interval, 'minutes'


    def delete(self):
        if self.__write_crontab():
            print 'The cronjob was removed'

    def is_on_crontab(self):
        self.__read_crontab()
        if self.is_set:
            return True
        else:
            return False