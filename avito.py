# -*- coding: utf-8 -*-
import json
import requests

from utills import load_config
from service import Service

DEBUG = True


class ApiAvito(Service):
    NAME = 'avito'
    DEBUG = DEBUG
    EMAIL_SUBJECT = u'Новое объявление на AVITO!!!'
    GEO_URL = 'https://www.avito.ru/js/catalog/coords'
    ITEM_URL = 'https://www.avito.ru/js/catalog/items'
    EMAIL_CONFIG = load_config('email_config').PARAMS

    def make_request(self):
        try:
            response = requests.get(self.GEO_URL, headers=self.headers, params=self.params)
            self.status = response.status_code == 200
            response_data = json.loads(response.text) if self.status else {}
            self.items = response_data['coords'] if 'coords' in response_data else {}
        except requests.exceptions.ConnectionError:
            return False
        return super(ApiAvito, self).make_request()

    def get_item(self, item_id, item_latitude, item_longitude):
        response = requests.get(self.ITEM_URL, headers=self.headers, params={
            'id': item_id, 'lat': item_latitude, 'lng': item_longitude
        })
        return json.loads(response.text)


avito = ApiAvito()

while True:
    status = avito.make_request()
    if status:
        for new_item_id in avito.new_items_set:
            avito.logger.log('new item: {}'.format(new_item_id))
            item_data = avito.get_item(
                new_item_id, avito.items[new_item_id]['lat'], avito.items[new_item_id]['lon']
            )['items'][new_item_id]

            avito.sender.send_mail(
                u'<a href="https://avito.ru{item_url}">{title}</a><br>'
                u'<b>Цена:</b> {price} {currency}<br>'
                u'<b>Адрес:</b> {address}<br>'.format(
                    item_url=item_data['url'],
                    title=item_data['title'],
                    price=item_data['price'],
                    currency=item_data['currency'],
                    address=item_data['ext']['address']
                )
            )
    avito.sleep()
