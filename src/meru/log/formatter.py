import logging


class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        record.shortname = record.name.split(".")[-1]
        return super().format(record)
