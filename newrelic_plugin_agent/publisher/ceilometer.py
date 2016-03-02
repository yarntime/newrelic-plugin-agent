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

import os
import logging
import abc
import stevedore
import ConfigParser
import requests

import base

LOG = logging.getLogger(__name__)

class CeilometerPublisher(base.BasePublisher):
    """"""

    CEILOMETER_ENDPOINT = 'http://{server}:{port}/v2/meters/'
    
    METRIC_DIMENSIONS = ['datacenter_id', 'resource_pool_id',
                         'group_id', 'account_id']
    
    METRIC_ATTRS = ['project_id', 'user_id', 'resource_id']

    def __init__(self, cnf):
        super(CeilometerPublisher, self).__init__('ceilometer', cnf)

        # init
        LOG.info('initialize ceilometer publisher')
        self.http_headers = {
            'Accept' : 'application/json',
            'Content-Type' : 'application/json'
        }
        
        self.dimensions = {}
        self.attrs = {}

        # TODO: parse the cnf file
        if cnf.has_key('config'):
            # old fashion
            configpath = cnf['config']
            if not os.path.exists(configpath):
                raise 'ceilometer publisher config file not found on path %s' % configpath

            parser = ConfigParser.ConfigParser()
            parser.read(configpath)
            
            server = parser.get('metadata', 'monitor_server')
            port = parser.get('metadata', 'monitor_port')
            self.endpoint = CEILOMETER_ENDPOINT.format(server=server, port=port)

            for dim in METRIC_DIMENSIONS:
                self.dimensions[dim] = parser.get('metadata', dem)
            for att in METRIC_ATTRS:
                self.attrs[att] = parser.get('metadata', att)
        else:
            self.endpoint = cnf['endpoint']
            self.x_auth_token = cnf['auth_token']

            for dim in cnf['dimensions']:
                self.dimensions.update(dim)

            for att in cnf['attrs']:
                self.attrs.update(att)

        if not self.x_auth_token:
            LOG.error('ceilometer publisher requires auth token.')
            raise 'ceilometer publisher requires auth token.'
        if not self.endpoint:
            LOG.error('ceilometer publisher requires endpoint. ')
            raise 'ceilometer publisher requires endpoint.'

        self.http_headers['x-auth-token'] = self.x_auth_token
        
        LOG.info('load ceilometer publisher with attributes %s' % str(self.attrs))
        LOG.info('load ceilometer publisher with dimensions %s' % str(self.dimensions))
        LOG.info('initialize ceilometer publisher done')

    def publish_data(self, data):
        """"""
        # TODO: impl it
        meters = self.__construct_ceilometer_metric(data)
        if not meter: return
        
        try:
            for mname, mbody in meters:
                response = requires.post("%s/%s" % (self.endpoint, mname),
                                         headers = self.http_headers,
                                         data = json.dumps(mbody, ensure_ascii=False),
                                         timeout = self.api_timeout)
        except Exception,e:
            LOG.error('report meter %s failed, due to %s' % (mname, str(e)))
            LOG.debug('dump meter body: %s ' % json.dumps(mbody))    

    def __construct_ceilometer_metric(self, data):
        """Transform newrelic format metric structure to ceilometer format.
        
        """
        ceilometer_meters = {}
        if comp is None: return None
        
        # FIXME: we only use the total value
        comp = comp['components']
        metrics = comp['metrics'] if comp.has_key['metrics'] else None
        if metrics:
            for mname,mvalue in metrics:
                obj = {
                    'counter_name' = mname,
                    'counter_type' = 'gauge',
                    'counter_unit' = 'instance',
                    'counter_volumn' = mvalue['total']}
                obj.update(self.attrs)
                obj['resource_metadata'] = self.dimensions
                
                meter = [obj]
                ceilometer_meters[mname] = meter
                
        return ceilometer_meters
    
