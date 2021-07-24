#!/usr/bin/python
from utils.Singleton import Singleton
import logging
import os
from settings import ROOT_DIR

"""
Created by senalw on 09/17/2018.
"""


class Logger(Singleton):
    instance = None

    def __init__(self, log_file_name='LogAnalyzer',
                 formatter='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        self.logger = logging.getLogger(__name__)
        self.set_file_handler(log_file_name, formatter)

    def set_file_handler(self, log_file_name, formatter):
        handler = logging.FileHandler(os.path.join(ROOT_DIR, "logs/", "%s.log" % log_file_name))
        handler.setLevel(logging.DEBUG)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.INFO)
        formatter = logging.Formatter(formatter)
        handler.setFormatter(formatter)
        self.logger.addHandler(consoleHandler)
        self.logger.addHandler(handler)

    def log_info(self, message):
        self.logger.setLevel(logging.INFO)
        # print("Info, %s," % message)
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.setLevel(logging.WARN)
        # print("Warning, %s," % message)
        self.logger.warn(message)

    def log_errors(self, message):
        self.logger.setLevel(logging.ERROR)
        # print("Error, %s," % message)
        self.logger.error(message)

    def log_debug(self, message):
        self.logger.setLevel(logging.DEBUG)
        # print("Debug, %s," % message)
        self.logger.debug(message)

    def log_critical(self, message):
        self.logger.setLevel(logging.FATAL)
        # print("Critical, %s," % message)
        self.logger.fatal(message)
