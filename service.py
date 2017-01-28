# -*- coding: utf-8 -*-
import sys
import random

from time import sleep
from utills import Logger, EmailSender


class Service(object):
    NAME = ''
    DEBUG = True
    EMAIL_CONFIG = {}
    EMAIL_SUBJECT = ''

    def __init__(self):
        self.headers = self.read_config('headers')
        self.params = self.read_config('params')
        self.logger = Logger(self.NAME, self.DEBUG)
        self.sender = EmailSender(email_subject=self.EMAIL_SUBJECT, debug=self.DEBUG,
                                  **self.EMAIL_CONFIG)

        self.status = False
        self.items = []
        self.prev_items_set = set()
        self.cur_items_set = set()
        self.new_items_set = set()

        status = self.make_request()
        if not status:
            sys.exit("Error connection")

    def read_config(self, config):
        try:
            conf_file_name = 'config/{}_{}'.format(self.NAME, config)
            config_file = open(conf_file_name, 'r')
        except IOError:
            default_conf_file_name = 'config/default_{}_{}'.format(self.NAME, config)
            config_file = open(default_conf_file_name, 'r')

        conf_data = config_file.read().split('\n')
        config = {}
        for param in conf_data:
            if param:
                param_name, param_data = param.split(':', 1)
                config[param_name] = param_data
        return config

    def make_request(self):
        if self.status:
            self.cur_items_set = set(self.items)
            self.logger.time_log(str(len(self.cur_items_set)))
        else:
            self.logger.time_log('---------------')

        # CHECK IN DEBUG MODE
        if self.DEBUG and len(self.prev_items_set) and random.randint(1, 2) == 1:
            delete_item = list(self.prev_items_set)[random.randint(1, len(self.prev_items_set))-1]
            self.logger.log('remove {}'.format(delete_item))
            self.prev_items_set.remove(delete_item)

        self.new_items_set = self.cur_items_set.difference(self.prev_items_set)
        self.prev_items_set = self.cur_items_set
        return self.status

    def sleep(self):
        sleep_time = 10 if self.DEBUG else random.randint(60, 60*5)
        sleep(sleep_time)
