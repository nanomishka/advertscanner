# -*- coding: utf-8 -*-
import json
import requests

from utills import load_config
from service import Service

DEBUG = True


class ApiCian(Service):
    NAME = 'cian'
    DEBUG = DEBUG
    EMAIL_SUBJECT = u'Новое объявление на CIAN!!!'
    GEO_URL = 'http://map.cian.ru/ajax/map/roundabout/'
    EMAIL_CONFIG = load_config('email_config').PARAMS

    def make_request(self):
        try:
            response = requests.get(self.GEO_URL, headers=self.headers, params=self.params)
            self.status = response.status_code == 200
            response_data = json.loads(response.text) if self.status else {}
            self.items = {}
            if response_data and 'data' in response_data:
                for addr, content in response_data['data']['points'].iteritems():
                    for offer in content['offers']:
                        self.items[offer['id']] = 'ok'
        except requests.exceptions.ConnectionError:
            return False
        return super(ApiCian, self).make_request()


cian = ApiCian()

while True:
    status = cian.make_request()
    if status:
        for item_id in cian.new_items_set:
            cian.logger.log('new item: {}'.format(item_id))

            cian.sender.send_mail(
                u'<a href="https://cian.ru/rent/flat/{item_url}/">Ссылка</a><br>'.format(
                    item_url=item_id
                )
            )

    cian.sleep()
