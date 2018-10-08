#!/usr/bin/env python3
"""
    Setup logger for the project

"""

import logging


loggers = dict()
e_loggers = dict()
i_loggers = dict()


def setup_info_logger(project):
    if project in i_loggers.keys():
        return i_loggers.get(project)
    # create logger
    logger_i = logging.getLogger(project)
    logger_i.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch_i = logging.StreamHandler()
    ch_i.setLevel(logging.INFO)

    # create formatter
    formatter_i = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch_i.setFormatter(formatter_i)

    # add ch to logger
    logger_i.addHandler(ch_i)

    i_loggers.update({project: logger_i})
    return logger_i


def log_info(project, info, args):
    """
    Log the infor passes.
    :param project: string
    :param info: must be a string with number argument spaces
    :param args: must be a tuple
    """
    # create logger
    logger_i = setup_info_logger(project)

    i = info
    if args is not None:
        i = info.format(args)
    logger_i.info(i)


def setup_logger(project):
    if project in loggers.keys():
        return loggers.get(project)
    # create logger
    logger_d = logging.getLogger(project)
    logger_d.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch_d = logging.StreamHandler()
    ch_d.setLevel(logging.DEBUG)

    fh_d = logging.FileHandler('github-debug.log')
    fh_d.setLevel(logging.DEBUG)

    # create formatter
    formatter_d = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch_d.setFormatter(formatter_d)
    fh_d.setFormatter(formatter_d)

    # add ch to logger
    # logger_d.addHandler(ch_d)
    logger_d.addHandler(fh_d)

    loggers.update({project: logger_d})
    return logger_d


def log_debug(project, mssg, args):
    logger_d = setup_logger(project)
    i = mssg
    if args is not None:
        i = mssg.format(args)
    logger_d.debug(i)


def setup_error_logger(project):
    # print(project, project in e_loggers.keys())
    if project in e_loggers.keys():
        return e_loggers.get(project)
    # create logger
    logger_e = logging.getLogger(project)
    logger_e.setLevel(logging.ERROR)

    # create console handler and set level to debug
    ch_e = logging.StreamHandler()
    ch_e.setLevel(logging.ERROR)

    fh_e = logging.FileHandler('github-error.log')
    fh_e.setLevel(logging.ERROR)

    # create formatter
    formatter_e = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch_e.setFormatter(formatter_e)
    fh_e.setFormatter(formatter_e)

    # add ch to logger
    # logger_e.addHandler(ch_e)
    logger_e.addHandler(fh_e)

    e_loggers.update({project: logger_e})
    return logger_e


def log_error(project, mssg, args):
    logger_e = setup_error_logger(project)
    i = mssg
    if args is not None:
        i = mssg.format(args)
    logger_e.error(i)
