import logging
from textwrap import wrap


class BotLogger:
    def __init__(self, log_file):
        self.logger = logging.getLogger("bot_logger")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s\n - %(message)s\n')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_debug(self, message):
        self.logger.debug(message)


