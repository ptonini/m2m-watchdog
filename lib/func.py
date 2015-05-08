__author__ = 'ptonini'


import ConfigParser as configparser

def get_config_from_file(filename):
    global_vars, service_list = list(), list()
    config = configparser.ConfigParser()
    config.read(filename)
    for section in config.sections():
        if section == 'global':
            global_vars = [config.get(section, 'cronfile'), config.getint(section, 'sampling'),
                           config.getint(section, 'threshold'), ]
        else:
            service_list.append([section, config.get(section, 'pidfile'), config.get(section, 'script'),
                                config.get(section, 'port'), config.getboolean(section, 'is_java')])
    return global_vars, service_list


