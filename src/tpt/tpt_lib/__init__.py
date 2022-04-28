#  Copyright (c) 2020 Roger Muñoz Bernaus
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" TPTLib module """
import requests
import hmac
import hashlib
import time
import json

from .exceptions import InvalidAPIUrl
from .exceptions import InvalidSecret
from .exceptions import RequestFailed

class TPTLib:
    """
        TPTLib class
    """
    _base_url = None
    _config = {
        'base_url': None,
        'secret': None
    }

    def __init__(self, api_url, secret):
        if api_url is None:
            raise InvalidAPIUrl("TPT URL is not defined")
        if secret is None:
            raise InvalidSecret("Secret is not defined")

        self._config['base_url'] = api_url
        self._config['secret'] = secret

    def verify_request(self, data):
        #response = requests.post('{}/api/v1/evaluation/new/'.format(self._config['base_url']), json=data)
        s = requests.Session()
        headers = {"Content-Type": "application/json"}
        data['nonce'] = int(time.time() * 1000)

        request = requests.Request('POST', '{}/api/v1/evaluation/new/'.format(self._config['base_url']), data=json.dumps(data),
                                   headers=headers)
        prepped = request.prepare()
        signature = hmac.new(self._config['secret'].encode('utf8'), prepped.body.encode('utf8'), digestmod=hashlib.sha512)
        prepped.headers['TPT-SIGN'] = signature.hexdigest()

        response = s.send(prepped)

        if int(response.status_code) != 200:
            raise RequestFailed(response.content)

        return response.json()


__all__ = [
    'TPTLib',
    'exceptions'
]
