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
""" Test fixtures module """
from logging import getLogger
import os
import pytest


@pytest.fixture
def tesla_ce_provider_conf():
    '''
    TeSLACE provider conf fixture
    :return:
    '''
    return {
        'provider_class': 'tpt.TPTProvider',
        'provider_desc_file': None,
        'instrument': None,
        'info': None
    }


@pytest.fixture
def tpt_provider(tesla_ce_base_provider):
    '''
    Urkund Provider Fixture
    :param tesla_ce_base_provider:
    :return:
    '''
    from tpt import TPTProvider
    assert isinstance(tesla_ce_base_provider, TPTProvider)

    logger = getLogger('tpt Tests')
    tesla_ce_base_provider.set_logger(logger.info)

    options = {
        'domain': 'http://localhost:8081'
    }
    tesla_ce_base_provider.set_options(options)
    tesla_ce_base_provider.set_credential('SECRET', os.getenv('SECRET', None))

    return tesla_ce_base_provider


@pytest.fixture
def mock_tpt_lib_all_ok(mocker, tpt_provider):
    """
    Mocker urkund lib all methods ok
    :param mocker:
    :param urkund_provider:
    :return:
    """
    mock_module = {
        'status_code': '0',
        'request_id': '3',
        'MOCKED': True
    }
    mocker.patch('tpt.tpt_lib.TPTLib.verify_request', return_value=mock_module)
