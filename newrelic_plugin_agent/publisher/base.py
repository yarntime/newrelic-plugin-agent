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

import abc 
import six
import stevedore
import logging

LOG = logging.getLogger(__name__)

class PublisherManager(object):
    """
    
    """
    def __init__(self, cnf, namespace='newrelic_plugin_agent.publisher'):
        self.cnf = cnf
        self.publishers = []

        try:
            publishers = self.cnf.get('Publisher')
            for publisher in publishers.keys():
                driver = stevedore.driver.DriverManager(namespace, publisher)
                self.publishers.append(driver.driver(publishers[publisher]))
        except Exception,e:
            LOG.error('loading publisher puging %s failed.' % str(publisher))
            LOG.error(str(e))

    def publish_data(self, data):
        """"""

        for publisher in self.publishers:
            try:
                publisher.publish_data(data)
            except Exception,e:
                LOG.error('publisher %s failed to publish data %s' % (publisher.name, str(data)))

@six.add_metaclass(abc.ABCMeta)
class BasePublisher(object):

    def __init__(self, name, config):
        self.cnf = config
        self.name = name

    @abc.abstractmethod
    def publish_data(self, data):
        raise NotImplementedError('TBD')

