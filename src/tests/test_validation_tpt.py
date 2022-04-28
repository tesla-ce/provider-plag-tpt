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
""" TeSLA CE TFR validation tests module """
from .utils import get_request


def test_send_zip_filename(mock_tpt_lib_all_ok, tpt_provider):
    '''
    Test send zip filename
    :param mock_tpt_lib_all_ok:
    :param tpt_provider:
    :return:
    '''
    filename = 'valid/lorem.txt.zip'
    sample = get_request(filename=filename, mimetype='application/zip')

    model = {}
    response = tpt_provider.verify(sample, model)

    from tesla_provider import result
    assert isinstance(response, result.VerificationDelayedResult)


def test_send_zip_filename(mock_tpt_lib_all_ok, tpt_provider):
    '''
    Test send zip filename
    :param mock_tpt_lib_all_ok:
    :param tpt_provider:
    :return:
    '''
    filename = 'valid/lorem.txt.zip'
    sample = get_request(filename=filename, mimetype='application/zip')

    model = {}
    response = tpt_provider.verify(sample, model)

    from tesla_ce_provider import result
    assert isinstance(response, result.VerificationDelayedResult)


def test_send_txt_filename(mock_tpt_lib_all_ok, tpt_provider):
    '''
    Test send TXT filename
    :param mock_tpt_lib_all_ok:
    :param tpt_provider:
    :return:
    '''
    filename = 'valid/lorem.txt'
    sample = get_request(filename=filename, mimetype='text/plain')

    model = {}
    response = tpt_provider.verify(sample, model)

    from tesla_ce_provider import result
    assert isinstance(response, result.VerificationDelayedResult)


def test_notification_txt_filename(mock_tpt_lib_all_ok, tpt_provider):
    '''
    Test verify txt filename
    :param mock_tpt_lib_all_ok:
    :param tpt_provider:
    :return:
    '''
    key = 'tpt_check_data'
    info = {}

    try:
        result = tpt_provider.on_notification(key, info)
        assert False
    except NotImplementedError:
        assert True
