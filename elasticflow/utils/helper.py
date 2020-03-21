import logging
from copy import copy
from logging import Formatter

from termcolor import colored


class ColoredFormatter(Formatter):
    MAPPING = {
        'DEBUG': dict(color='white', on_color=None),  # white
        'INFO': dict(color='white', on_color=None),  # cyan
        'WARNING': dict(color='yellow', on_color='on_grey'),  # yellow
        'ERROR': dict(color='white', on_color='on_red'),  # 31 for red
        # white on red bg
        'CRITICAL': dict(color='white', on_color='on_green'),
    }

    PREFIX = '\033['
    SUFFIX = '\033[0m'

    def format(self, record):
        cr = copy(record)
        seq = self.MAPPING.get(
            cr.levelname, self.MAPPING['INFO'])  # default white
        cr.msg = colored(cr.msg, **seq)
        return super().format(cr)


def set_logger(context, verbose: bool=False):

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger(context)
    logger.propagate = False
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        formatter = ColoredFormatter(
            '%(levelname)-.1s:' + context + ':[%(filename).3s:%(funcName).3s:%(lineno)3d]:%(message)s', datefmt='%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_handler.setFormatter(formatter)
        logger.handlers = []
        logger.addHandler(console_handler)

    return logger
