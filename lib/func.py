__author__ = 'ptonini'


import ConfigParser as configparser

def read_config(filename):
    service_list = list()
    config = configparser.ConfigParser()
    config.read(filename)
    for section in config.sections():
        service_list.append([section, config.get(section, 'pidfile'), config.get(section, 'script'),
                            config.get(section, 'port'), config.getboolean(section, 'is_java')])
    return service_list


