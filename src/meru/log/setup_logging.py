import logging
import logging.config
import os


_LOGCONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "console": {
            "class": "meru.log.formatter.ConsoleFormatter",
            "format": "%(asctime)s %(name)-15s %(levelname)-10s %(processName)-12s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "meru.log.colorstreamhandler.ColorStreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "console",
        },
        "journald": {
            "class": "systemd.journal.JournaldLogHandler",
        },
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "meru": {
            "level": "DEBUG",  # logging.getLevelName(settings.LOG_LEVEL),
            "handlers": ["console", "journald"],
            "propagate": False,
        },
        "aiocache.base": {"handlers": ["null"], "propagate": False},
    },
    "root": {
        "level": "DEBUG",  # logging.getLevelName(settings.LOG_LEVEL),
        "handlers": ["console"],
    },
}


def setup_logging():
    if os.environ.get("IS_MANAGED_BY_SYSTEMD", 0) == 0:
        _LOGCONFIG["handlers"]["journald"] = {"class": "logging.NullHandler"}
    else:
        _LOGCONFIG["handlers"]["console"] = {"class": "logging.NullHandler"}

    logging.config.dictConfig(_LOGCONFIG)
