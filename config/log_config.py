import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pytz import timezone

LOGGER_NAME = "prometheus-http-export"

class ColorFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey   = "\x1b[90m"
    green  = "\x1b[92m"
    yellow = "\x1b[93m"
    red    = "\x1b[91m"
    reset  = "\x1b[0m"
    # format = "%(asctime)s | %(levelname)-5.5s | %(message)s"
    format='[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        # logging.INFO: green + format + reset,
        logging.INFO: format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: red + format + reset
    }

    def format(self, record):
        record.levelname = 'WARN' if record.levelname == 'WARNING' else record.levelname
        record.levelname = 'ERROR' if record.levelname == 'CRITICAL' else record.levelname
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
 
    
def create_log():
    def timetz(*args):
        return datetime.now(tz).timetuple()

    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    tz = timezone('America/Chicago')  # UTC, Asia/Shanghai, Europe/Berlin
    logging.Formatter.converter = timetz
    
    log_format = logging.StreamHandler()
    log_format.setFormatter(ColorFormatter())
    
    logging.basicConfig(
        format='[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # logging.StreamHandler(),
            log_format,
            RotatingFileHandler(
                f"./logs/{LOGGER_NAME}.log", mode="a", maxBytes=50000, backupCount=10
            )
        ],
    )

    logger = logging.getLogger(LOGGER_NAME)

    return logger
