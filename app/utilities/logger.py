#!/usr/bin/env python3

import logging

from logging import Formatter, getLogger, StreamHandler
from console.colors import color_name, bg_color_name, set_color


class ColoredFormatter(Formatter):
    def format(self, record):
        message = record.getMessage()
        mapping = {
            'INFO': color_name.CYAN,
            'WARNING': color_name.YELLOW,
            'ERROR': color_name.RED,
            'CRITICAL': bg_color_name.RED,
            'DEBUG': color_name.WHITE,
            'SUCCESS': color_name.GREEN,
        }
        return set_color(
            '%s - %s - %s' % (self.formatTime(record, '%H:%M:%S'), record.levelname, message),
            mapping.get(record.levelname, 'white'),
        )


logger = logging.getLogger(__name__)
handler = StreamHandler()
formatter = ColoredFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
setattr(logger, 'success', lambda message, *args: logger._log(logging.SUCCESS, message, args))
logger.setLevel(logging.DEBUG)
