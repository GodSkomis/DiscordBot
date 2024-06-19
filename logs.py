import os
import logging
import logging.config
import queue
import settings

from datetime import datetime
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler


LOGS_BASE_DIR = os.path.join(settings.BASE_PATH, 'logs')
if not os.path.exists(LOGS_BASE_DIR):
    os.makedirs(LOGS_BASE_DIR)


def current_date_file_name(suffix: str = None):
    file_name = datetime.now().strftime("%Y-%m-%d")
    if suffix:
        file_name = f"{file_name}.{suffix}"
    file_name = f"{file_name}.log"
    return os.path.join(LOGS_BASE_DIR, file_name)


LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': { 
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    } 
}


logging.config.dictConfig(LOGGING_CONFIG)


# INFO LOGGER
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] (%(name)s) - %(message)s',
    datefmt='%H:%M:%S'
)
file_handler = TimedRotatingFileHandler(
    filename=current_date_file_name(),
    when='midnight',
    backupCount=5
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)


log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
queue_handler.setLevel(logging.INFO)
root = logging.getLogger()
root.addHandler(queue_handler)
queue_listener = QueueListener(log_queue, file_handler)
queue_listener.start()


# WARNING LOGGER
file_warn_handler = TimedRotatingFileHandler(
    filename=current_date_file_name(suffix="warning"),
    when='midnight',
    backupCount=5
)
file_warn_handler.setFormatter(formatter)
file_warn_handler.setLevel(logging.WARNING)


log_warn_queue = queue.Queue()
queue_warn_handler = QueueHandler(log_warn_queue)
queue_warn_handler.setLevel(logging.WARNING)
root = logging.getLogger()
root.addHandler(queue_warn_handler)
queue_warn_listener = QueueListener(log_warn_queue, file_warn_handler)
queue_warn_listener.start()
