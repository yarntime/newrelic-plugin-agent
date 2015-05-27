#
# Copyright 2015 chinaskycloud.com.cn
#
# Author: Chunyang Liu <liucy@chinaskycloud.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import logging
import requests

import six
import abc

import base

LOG = logging.getLogger(__name__)

class NEWRELICPublisher(base.BasePublisher):
    """"""

    PLATFORM_URL = 'https://platform-api.newrelic.com/platform/v1/metrics'
    def __init__(self, cnf):
        super(NEWRELICPublisher, self).__init__('ceilometer', cnf)

        LOG.info('initialize NEWRELIC Publisher')
        self.http_headers = {'Accept': 'application/json',
                             'Content-Type': 'application/json'}

        self.endpoint = cnf['endpoint']
        self.license_key = cnf['license_key']
        self.proxies = None
        self.api_timeout = 10

        self.verify_ssl_cert = True if cnf['verify_ssl_cert'] == 'true' else False
        if not self.endpoint:
            LOG.error('newrelic publisher endpoint not specified.')
            self.endpoint = PLATFORM_URL

        try:
            self.api_timeout = int(cnf['api_timeout'])
        except ValueError:
            LOG.error('newrelic api timeout value error. use default value.')

        if 'proxy' in cnf:
            self.proxies = {
                'http': cnf['proxy'],
                'https': cnf['proxy']
            }

        if self.license_key:
            self.http_headers['X-License-Key'] = self.license_key

        LOG.info('initialize NEWRELIC publisher done')

    def publish_data(self, data):
        """Create the headers and payload to send to NewRelic platform as a
        JSON encoded POST body.
        
        """

        try:
            response = requests.post(self.endpoint,
                                     headers=self.http_headers,
                                     proxies=self.proxies,
                                     data=json.dumps(data, ensure_ascii=False),
                                     timeout=self.api_timeout,
                                     verify=self.verify_ssl_cert)
            LOGGER.debug('Response: %s: %r',
                         response.status_code,
                         response.content.strip())
        except requests.ConnectionError as error:
            LOGGER.error('Error reporting stats: %s', error)
        except requests.Timeout as error:
            LOGGER.error('TimeoutError reporting stats: %s', error)

