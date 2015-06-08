__author__ = 'ptonini'


import ConfigParser as configparser

def get_config_from_file(filename):
    service_list = list()
    config = configparser.ConfigParser()
    config.read(filename)
    for section in config.sections():
        if section == 'global':
            cronfile = config.get(section, 'cronfile')
            sampling = config.getint(section, 'sampling')
            threshold = config.getint(section, 'threshold')
        else:
            service_list.append([section, config.get(section, 'pidfile'), config.get(section, 'script'),
                                config.get(section, 'port'), config.getboolean(section, 'is_java')])
    return cronfile, sampling, threshold, service_list


