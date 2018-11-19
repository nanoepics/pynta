# -*- coding: utf-8 -*-
"""
    pynta.util.log.py
    =================

    Adding log capacities to PyNTA


    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: AGPLv3, see LICENSE for more details
"""
import logging


DEFAULT_FMT = "[%(levelname)8s]%(asctime)s %(name)s: %(message)s"

def get_logger(name='pynta', add_null_handler=True):
    logger = logging.getLogger(name) #, add_null_handler=add_null_handler)
    return logger


PYNTA_LOGGER = get_logger()


def log_to_screen(level=logging.INFO, fmt=None):
    fmt = fmt or DEFAULT_FMT
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(fmt)
    PYNTA_LOGGER.addHandler(handler)
    return

def log_to_file(filename, level=logging.INFO, fmt=None):
    fmt = fmt or DEFAULT_FMT
    handler = logging.FileHandler(filename)
    handler.setLevel(level)
    handler.setFormatter(fmt)
    PYNTA_LOGGER.addHandler(handler)
    return
