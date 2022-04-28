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
""" TeSLA CE TPT Plagiarism module """
import os
import uuid

from tesla_ce_provider import BaseProvider, result, message
from tesla_ce_provider.provider.audit.tp import PlagiarismAudit
from ..tpt_lib import TPTLib
from ..tpt_lib.exceptions import RequestFailed, Timeout
from . import utils


class TPTProvider(BaseProvider):
    """
        TeSLA TPT implementation
    """
    accepted_mimetypes = [
        'application/zip',
        'application/gzip',
        'application/x-tar',
        'application/x-bzip2',
        'application/x-7z-compressed',
        'application/x-rar-compressed',
        'application/x-lzma',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.sun.xml.writer',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/pdf',
        'text/plain',
        'application/rtf',
        'text/html',
        'text/html',
        'application/vnd.ms-works',
        'application/vnd.oasis.opendocument.text'
    ]

    _required_credentials = ['SECRET']

    config = {
        'domain': None,
        'compression_recursive_extract_level': 3,
        'timeout_retries': 0,
        'max_timeout_retries': 3,
        'timeout_between_retries': 60,
        'countdown_multiplier': 2,
        'countdown_initial': 5
    }

    def set_options(self, options):
        """
            Set options for the provider
            :param options: Provider options following provider options_scheme definition
            :type options: dict
        """
        if options is not None:
            permitted_options = self.config.keys()

            for permitted_option in permitted_options:
                if permitted_option in options:
                    self.config[permitted_option] = options[permitted_option]

    _tpt_lib = None

    def _get_tpt_lib(self):
        """
        Return UrkundLib instance
        :return:
        """
        if self._tpt_lib is None:
            if self.config['domain'] is None:
                self.config['domain'] = os.getenv('TPT_URL')
            self._tpt_lib = TPTLib(api_url=self.config['domain'], secret=self.credentials['SECRET'].strip())

        return self._tpt_lib

    def verify(self, request, model):
        """
            Verify a learner request
            :param request: Verification request
            :type request: Request
            :param model: Provider model
            :type model: dict
            :return: Verification result
            :rtype: tesla_provider.VerificationResult
        """

        # Check provided input
        sample_check = utils.check_sample_file(request, self.config['compression_recursive_extract_level'],
                                               self.accepted_mimetypes)

        if not sample_check['valid']:
            return result.VerificationResult(False, error_message=sample_check['msg'],
                                             message_code=sample_check['code'])

        # todo: check configuration activity


        # sample is valid proceed to sent to urkund
        idx = 0
        info = {
            "learner_id": request.learner_id,
            "request_id": request.request_id,
            "external_ids": [],
            "processed_external_ids": {
                "errors": [],
                "corrects": []
            },
            "errors": [],
            "countdown": self.config['countdown_initial'],
            "total_files": len(sample_check['tree_file'])
        }

        for t_file in sample_check['tree_file']:
            if t_file['status'] == 'ACCEPTED':
                file = {
                    "filename": t_file['filename'],
                    "mimetype": t_file['mimetype'],
                    "content": t_file['content']
                }
                external_id = "{}__{}".format(request.request_id, idx)

                try:
                    # send to TPT
                    # TODO: where is data?
                    data = {
                        "activity": {
                            "vle_id": "1",
                            "activity_type": request.activity_id,
                            "activity_id": request.activity_id
                        },
                        "sample_data": utils.construct_sample(file),
                        "learner_id": request.learner_id,
                        "evaluation_id": external_id
                    }
                    response = self._get_tpt_lib().verify_request(data=data)

                    # good response
                    # {"request_id":1,"status_code":"0"}

                    if int(response['status_code']) == 0:
                        aux = {
                            "tpt_external_id": int(response['request_id']),
                            "external_id": external_id,
                            "filename": t_file['filename']
                        }
                        info['external_ids'].append(aux)

                    else:
                        aux = {
                            "code": message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA.value,
                            "filename": t_file['filename'],
                            "tpt_code": response['status_code']
                        }
                        info['processed_external_ids']['errors'].append(aux)

                    idx += 1
                except RequestFailed as err:
                    aux = {
                        "code": message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA.value,
                        "filename": t_file['filename'],
                        "tpt_code": str(err)
                    }

                    info['processed_external_ids']['errors'].append(aux)
                except Timeout:
                    self.config['timeout_retries'] += 1
                    if self.config['timeout_retries'] >= self.config['max_timeout_retries']:
                        aux = {
                            "code": message.provider.Provider.PROVIDER_EXTERNAL_SERVICE_TIMEOUT.value,
                            "filename": t_file['filename'],
                            "tpt_code": None
                        }
                        info['processed_external_ids']['errors'].append(aux)
                    else:
                        return self.verify(request, model)

        # check if there is any sent document valid to check in the future
        if len(info['external_ids']) == 0:
            return result.VerificationResult(False, message_code=message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA.value)
        elif len(info['processed_external_ids']['errors']) > 0 and len(info['external_ids']) > 0:
            return result.VerificationDelayedResult(learner_id=request.learner_id, request_id=request.request_id,
                                                    result=result.VerificationResult(True, message_code=message.provider.Provider.PROVIDER_INVALID_PARTIAL_SAMPLE_DATA.value))

        return result.VerificationDelayedResult(learner_id=request.learner_id, request_id=request.request_id,
                                                result=result.VerificationResult(True))
