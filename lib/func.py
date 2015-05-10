__author__ = 'ptonini'


import ConfigParser as configparser

def from_file(filename):
    service_list = list()
    config = configparser.ConfigParser()
    config.read(filename)
    cronfile = config.get('global', 'cronfile')
    sampling = config.getint('global', 'sampling')
    threshold = config.getint('global', 'threshold')

    for section in config.sections():
        if section != 'global':
            service_list.append([section, config.get(section, 'pidfile'), config.get(section, 'script'),
                                config.get(section, 'port'), config.getboolean(section, 'is_java')])
    return cronfile, sampling, threshold, service_list


