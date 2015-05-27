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

import logging
import json

import base

LOG = logging.getLogger(__name__)

class FilePublisher(base.BasePublisher):

    def __init__(self, cnf):
        super(FilePublisher, self).__init__('file', cnf)

        LOG.info('initialize file publisher')

        rfh = None
        datafile = self.cnf['path']

        # Handling other configuration options in the query string
        try:
            max_bytes = int(self.cnf['max_bytes'])
            backup_count = int(self.cnf['backup_count'])
        except ValueError:
            LOG.error('max_bytes and backup_count should be '
                      'numbers.')
            return

        # create rotating file handler
        rfh = logging.handlers.RotatingFileHandler(
            datafile, encoding='utf8', maxBytes=max_bytes,
            backupCount=backup_count)

        self.publisher_logger = logging.Logger('publisher.file')
        self.publisher_logger.propagate = False
        self.publisher_logger.setLevel(logging.INFO)
        rfh.setLevel(logging.INFO)
        self.publisher_logger.addHandler(rfh)

        LOG.info('initialize file publisher done.')

    def publish_data(self, data):
        """File publish will publish the metrics collected into file. Support rotation.
        
        """
        
        if self.publisher_logger and data:
            if not isinstance(data, dict):
                LOG.error('publish data format error, dict expected.')
                return

            if self.publisher_logger is None:
                return

            try:
                self.publisher_logger.info(json.dumps(data, ensure_ascii=False))
            except Exception,e:
                LOG.error(str(e))
