# -*- coding: utf-8 -*-
import importlib
import smtplib
import socket

from email.mime.text import MIMEText
from datetime import datetime


def load_config(config):
    module_path = 'config.{}'.format(config)
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        module = importlib.import_module('config.default_{}'.format(config))
    return module


class Logger(object):
    def __init__(self, app_name, debug=True):
        self.debug = debug
        if not debug:
            self.output_filename = 'output/{}.log'.format(app_name)

    def log(self, message):
        if self.debug:
            print message
        else:
            output_file = open(self.output_filename, 'a')
            print >> output_file, message
            output_file.close()

    def time_log(self, message):
        self.log('{}: {}' .format(datetime.now().strftime("%d/%m/%y %H:%M:%S"), message))


class EmailSender(object):
    def __init__(self, smtp_host, smtp_port, login, password,
                 email_from, email_to, email_subject, debug=False):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.login = login
        self.password = password
        self.email_from = email_from
        self.email_to = email_to
        self.email_subject = email_subject
        self.debug = debug

    def send_mail(self, message):
        status = False
        try:
            server = smtplib.SMTP()
            server.connect(self.smtp_host, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.login(self.login, self.password)

            msg = smtplib.email.MIMEMultipart.MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ','.join(self.email_to)
            msg['Subject'] = u'{}{}'.format('DEBUG: ' if self.debug else '', self.email_subject)
            msg.attach(MIMEText(message.encode('utf8'), 'html', 'utf-8'))

            server.sendmail(self.email_from, self.email_to, msg.as_string())
            status = True

        except socket.gaierror:
            print u'Invalid params for smtp'
        except smtplib.SMTPAuthenticationError:
            print u'Invalid login/password for smtp'

        return status
