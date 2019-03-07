"""
Copyright (c) 2017 5GTANGO
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the 5GTANGO
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the 5GTANGO project,
funded by the European Commission under Grant number 761493 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the 5GTANGO
partner consortium (www.5gtango.eu).
"""
"""
This is SONATA's TAPI WIM management plugin
"""

import logging
import threading
import concurrent.futures as pool
import requests
import uuid
import time
import os
import yaml, json
from pprint import pprint
from tapi_wrapper.logger import TangoLogger


# logging.basicConfig(level=logging.INFO)
# logging.getLogger('pika').setLevel(logging.ERROR)
# LOG = logging.getLogger("tapi-wrapper:tapi-wrapper")
LOG = TangoLogger.getLogger(__name__ + ':' + __file__, log_level=logging.DEBUG, log_json=True)
# LOG.setLevel(logging.DEBUG)
MAX_DEPLOYMENT_TIME = 5


class TapiWrapperEngine(object):
    """
    Interface class with WIM's T-API
    """

    def __init__(self, **kwargs):
        """
        Initialize TAPI WIM connection.
        :param app_id: string that identifies application

        """

        self.load_config()

        # Threading workers
        # self.thrd_pool = pool.ThreadPoolExecutor(max_workers=100)
        # Track the workers
        self.tasks = []
        # self.thrd_pool.submit()
        self.index = 1000
        # TODO: Create FSM-SSM static flow

    def load_config(self):
        """
        Read configuration file
        :return:
        """

        # connection_file = 'connections_commpilot.txt'
        # entities_file = 'entities.txt'
        #
        # # Get info from VIM and VNFD
        # with open(entities_file, 'r') as efp:
        #     self.entities = efp.readlines()
        #
        # # Get info from VLD -> this is done in main script
        # with open(connection_file, 'r') as cfp:
        #     self.virtual_links = cfp.readlines()

        # self.wim_ip = os.getenv('WIM_IP', '10.1.1.54')
        self.wim_ip = '10.120.0.19'  # PROVIDED BY IA?
        # self.wim_port = os.getenv('WIM_PORT', 8182)
        self.wim_port = 8182

    def get_topology(self):
        """
        Gets topology from WIM to match nodes
        :return:
        """
        # nbi_topology_url = 'http://' + self.wim_ip + ':' + str(self.wim_port) + '/restconf/config/context/topology/0'
        tapi_topology_url = 'http://' + self.wim_ip + ':' + str(self.wim_port) + '/restconf/config/context/topology/0/'
        wim_topology = requests.get(tapi_topology_url)
        return wim_topology.json()

    def generate_cs_from_nap_pair(self, ingress_nap, egress_nap, ingress_ep, egress_ep,
                                  direction='UNIDIRECTIONAL', layer='ETH', requested_capacity=100, latency=None):
        """

        :param uuid:
        :param ingress_nap:
        :param egress_nap:
        :param ingress_ep:
        :param egress_ep:
        :param direction:
        :param layer:
        :param requested_capacity:
        :return call:
        """
        allowed_layer = {'ETH', 'MPLS'}
        special_layer = {'mpls_arp'}
        allowed_direction = {'UNIDIRECTIONAL', 'BIDIRECTIONAL'}
        if direction not in allowed_direction:
            raise ValueError('Direction {} must be one of {}'.format(direction, allowed_direction))
        if not (layer in allowed_layer or layer in special_layer):
            raise ValueError('Layer {} must be one of {}'.format(layer, allowed_layer))
        if layer == 'ETH' or (layer == 'MPLS' and direction == 'UNIDIRECTIONAL'):
            connectivity_service = {
                "uuid": str(self.index),
                "end-point": [
                    {
                        "service-interface-point": "/restconf/config/context/service-interface-point/{}/".format(
                            ingress_ep),
                        "direction": "BIDIRECTIONAL",
                        "layer-protocol-name": "ETH",
                        "role": "SYMMETRIC"
                    },
                    {
                        "service-interface-point": "/restconf/config/context/service-interface-point/{}/".format(
                            egress_ep),
                        "direction": "BIDIRECTIONAL",
                        "layer-protocol-name": "ETH",
                        "role": "SYMMETRIC"
                    }
                ],
                "layer-protocol-name": layer,
                "direction": direction,
                "requested-capacity": {
                    "total-size": {
                        "value": str(requested_capacity / 1e6),
                        "unit": "MBPS"
                    }
                },
                "match": {
                    'ipv4-source': ingress_nap,
                    'ipv4-target': egress_nap,
                    'link-layer-type': "2048"
                }
            }
        elif layer == 'arp':
            connectivity_service = {
                "uuid": str(self.index),
                "end-point": [
                    {
                        "service-interface-point": "/restconf/config/context/service-interface-point/{}/".format(
                            ingress_ep),
                        "direction": "BIDIRECTIONAL",
                        "layer-protocol-name": "ETH",
                        "role": "SYMMETRIC"
                    },
                    {
                        "service-interface-point": "/restconf/config/context/service-interface-point/{}/".format(
                            egress_ep),
                        "direction": "BIDIRECTIONAL",
                        "layer-protocol-name": "ETH",
                        "role": "SYMMETRIC"
                    }
                ],
                "layer-protocol-name": 'ETH',
                "direction": direction,
                "requested-capacity": {
                    "total-size": {
                        "value": str(requested_capacity / 1e6),
                        "unit": "MBPS"
                    }
                },
                "match": {
                    'ipv4-source': ingress_nap,
                    'ipv4-target': egress_nap,
                    'link-layer-type': "2054"
                }
            }
        elif layer == 'mpls_arp' and direction == 'UNIDIRECTIONAL':
            connectivity_service = {
                "uuid": str(self.index),
                "end-point": [
                    {
                        "service-interface-point": "/restconf/config/context/service-interface-point/{}/".format(
                            ingress_ep),
                        "direction": "BIDIRECTIONAL",
                        "layer-protocol-name": "ETH",
                        "role": "SYMMETRIC"
                    },
                    {
                        "service-interface-point": "/restconf/config/context/service-interface-point/{}/".format(
                            egress_ep),
                        "direction": "BIDIRECTIONAL",
                        "layer-protocol-name": "ETH",
                        "role": "SYMMETRIC"
                    }
                ],
                "layer-protocol-name": 'MPLS',
                "direction": direction,
                "requested-capacity": {
                    "total-size": {
                        "value": str(requested_capacity / 1e6),
                        "unit": "MBPS"
                    }
                },
                "match": {
                    'ipv4-source': ingress_nap,
                    'ipv4-target': egress_nap,
                    'link-layer-type': "2054"
                }
            }
        else:
            raise AttributeError('Layer {} is not compatible with direction {}'.format(layer, direction))
        self.index += 1
        return connectivity_service

    def create_connectivity_service(self, cs):
        """
        Call this function per virtual link
        :param cs:
        :return:
        """
        LOG.debug('TapiWrapper: Creating connectivity service {}'.format(cs['uuid']))
        tapi_cs_url = 'http://{}:{}/restconf/config/context/connectivity-service/{}/'.format(
           self.wim_ip, self.wim_port, cs['uuid'])
        headers = {'Content-type': 'application/json'}
        try:
            response = requests.post(tapi_cs_url, json=cs, headers=headers)
        except Exception as e:
            raise e
        else:
            if 200 <= response.status_code < 300:
                return response
            else:
                raise ConnectionError({'msg': response.text, 'code': response.status_code})

    def remove_connectivity_service(self, uuid):
        LOG.debug('TapiWrapper: Removing connectivity service {}'.format(uuid))
        tapi_cs_url = 'http://{}:{}/restconf/config/context/connectivity-service/{}/'.format(
            self.wim_ip, self.wim_port, uuid)
        headers = {'Accept': 'application/json'}
        try:
            response = requests.delete(tapi_cs_url, headers=headers)
        except Exception as e:
            raise e
        else:
            if 200 <= response.status_code < 300:
                return response
            else:
                raise ConnectionError({'msg': response.text, 'code': response.status_code})

    def get_sip_by_name(self, name):
        tapi_sip_url = 'http://{}:{}/restconf/config/context/service-interface-point/'.format(self.wim_ip, self.wim_port)
        sip_list = requests.get(tapi_sip_url).json()
        return list(filter(lambda x: x['name']['value-name'] == name, sip_list))[0]


test = TapiWrapperEngine()
