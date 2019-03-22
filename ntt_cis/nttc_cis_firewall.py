#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 NTT Communications Cloud Infrastructure Services
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   - NTTC CIS
#
# List, Get, Create, Modify and Delete Firewall rules

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_firewall
short_description: List, Get, Create, Modify and Delete Firewall rules
description:
    - List, Get, Create, Modify and Delete Firewall rules
version_added: "1.1"
author: "Ken Sinfield"
options:
    region:
        description:
            - The geographical region
        required: false
        default: na
        choices:
          - Valid values can be found in nttcis.common.config.py under
            APIENDPOINTS
    datacenter:
        description:
            - The datacenter name
        required: true
        choices:
          - See NTTC CIS Cloud Web UI
    name:
        description:
            - The name of the Cloud Network Domain
        required: False
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        default: None
    action:
        description:
            - The firewall rule action
        required: false
        default: ACCEPT_DECISIVELY
        choices: [ACCEPT_DECISIVELY, DENY]
    version:
        description:
            - The IP version
        required: false
        default: IPV4
        choices: [IPV4, IPv6]
    protocol:
        description:
            - The protocol
        required: false
        default: TCP
        choices: [TCP, UDP, IP, ICMP]
    src_ip:
        description:
            - The source IP address
        required: false
    src_ip_prefix:
        description:
            - The source IP prefix size
    src_ip_list:
        description:
            - The name of an existing IP address list
        required: false
    dst_ip:
        description:
            - The destination IP address
        required: false
    dst_ip_prefix:
        description:
            - The destination IP prefix size
    dst_ip_list:
        description:
            - The name of an existing IP address list
        required: false
    src_port_start:
        description:
            - The starting source port
            - omit all src port details for ANY
        required: false
    src_port_end:
        description:
            - The end of the port range
    src_port_list:
        description:
            - The name of an existing port list
        required: false
    dst_port_start:
        description:
            - The starting destination port
            - omit all dst port details for ANY
        required: false
    dst_port_end:
        description:
            - The end of the port range
    dst_port_list:
        description:
            - The name of an existing port list
        required: false
    enabled:
        description: 
            - Whether to enable the firewall rule
        required: false
        default: true
        choices: [true, false]
    position:
        description:
            - Position of the firewall rule
            - If BEFORE or AFTER are used a position_to value is required
        required: false
        default: LAST
        choices: [FIRST, LAST, BEFORE, AFTER]
    position_to:
        description:
            - The name of an existing firewall rule to position the new rule
            - relative to
        required: false
    state:
        description:
            - The action to be performed
        required: true
        default: create
        choices: [list, get, create, update, delete]
    verify_ssl_cert:
        description:
            - Enable/Disable SSL certificate verification
        required: false
        default: true
        choices: [true, false]
notes:
    - N/A
requirements:
    - NTTC CIS Provider v2
'''

EXAMPLES = '''
# List firewall rules
- nttc_cis_firewall:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      state: list
# Get a specific firewall rule
- nttc_cis_firewall:
      region: na
      datacenter: NA9
      network_domain: "xxxx
      name: "wwww"
      state: get
# Create a firewall rule
- nttc_cis_firewall:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "wwww"
      protocol: "UDP"
      version: "IPV6"
      src_ip_list: "yyyy"
      dst_ip_list: "zzzz"
      src_port_start: "ANY"
      dst_port_list: "vvvv"
      enabled: True
      state: create
# Update a firewall rule
- nttc_cis_firewall:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "wwww"
      protocol: "TCP"
      version: "IPV6"
      dst_ip_list: "zzzz"
      src_ip: "ffff:ffff:ffff:ffff::"
      src_ip_prefix: "64"
      src_port_start: "ANY"
      dst_port_list: "vvvv"
      enabled: True
# Delete a firewall rule
- nttc_cis_firewall:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "wwww"
      state: delete
'''

RETURN = '''
fw_rule:
    description: a single or list of IP address objects or strings
    contains:
        id:
            description: Network Domain ID
            type: string
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        description:
            description: Network Domain description
            type: string
            sample: "My network description"
        datacenterId:
            description: Datacenter id/location
            type: string
            sample: NA3
'''

import json
from ansible.module_utils.basic import *
from ansible.module_utils.nttc_cis import *
from time import sleep
try:
    from ansible.module_utils.v2 import NTTCCISClient, NTTCCISAPIException
    from ansible.module_utils.config import API_ENDPOINTS
    NTTCIS_IMPORTED = True
except:
    NTTCIS_IMPORTED = False


def get_nttc_cis_regions():
    regions = []
    for region in API_ENDPOINTS:
        regions.append(region)
    return regions

def list_fw_rule(module, client, network_domain):
    try:
        result = client.list_fw_rules(network_domain['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list of firewall rules - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    if len(result) > 0:
        msg = 'Found %d firewall rules in %s' % (len(result), 
                                                 network_domain['name'])
    else:
        msg = 'No firewall rules found'

    module.exit_json(changed=False, msg=msg, data=result)


def create_fw_rule(module, client, network_domain):
    result = {}
    args = module.params
    error = 'IP Address'

    try:   
        if args['src_ip_list'] is not None:
            args['src_ip_list'] = client.get_ip_list_by_name(
                                                        network_domain['id'],
                                                        args['src_ip_list'],
                                                        args['version']
                                                    )['id']
        if args['dst_ip_list'] is not None:
            args['dst_ip_list'] = client.get_ip_list_by_name(
                                                        network_domain['id'],
                                                        args['dst_ip_list'],
                                                        args['version']
                                                    )['id']
        error = 'Port List'
        if args['src_port_list'] is not None:
            args['src_port_list'] = client.get_port_list_by_name(
                                                        network_domain['id'],
                                                        args['src_port_list']
                                                    )['id']
        if args['dst_port_list'] is not None:
            args['dst_port_list'] = client.get_port_list_by_name(
                                                        network_domain['id'],
                                                        args['dst_port_list']
                                                    )['id']
    except NTTCCISAPIException as e:
        module.fail_json(changed=False, msg='Invalid %s List - %s' % 
                                            (error, e))
    except Exception as e:
        module.fail_json(changed=False, msg='Invalid %s List - %s' %
                                            (error, e))

    try:
        result = client.create_fw_rule(network_domain['id'], args['name'],
                                       args['action'], args['version'],
                                       args['protocol'], args['src_ip'],
                                       args['src_ip_prefix'],
                                       args['src_ip_list'], args['dst_ip'],
                                       args['dst_ip_prefix'], 
                                       args['dst_ip_list'], 
                                       args['src_port_start'],
                                       args['src_port_end'],
                                       args['src_port_list'], 
                                       args['dst_port_start'],
                                       args['dst_port_end'],
                                       args['dst_port_list'], args['enabled'],
                                       args['position'], args['position_to'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not create the firewall rule - %s' % e)
    except Exception as e:
        module.fail_json(changed=False, msg='Invalid data - %s' % e)

    msg = 'Successfully created the firewall rule'
    module.exit_json(changed=True, msg=msg, data=result)


def get_fw_rule(module, client, network_domain, name):
    result = {}
    if name is None:
        module.fail_json(changed=False, msg='A value for name is required')

    try:
        result = client.get_fw_rule_by_name(network_domain['id'], name)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get the firewall rule - %s' % e,
        )
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    msg = 'Found the firewall rule'

    module.exit_json(changed=False, msg=msg, data=result)


def update_fw_rule(module, client, network_domain):
    result = {}
    args = module.params
    fw_rule_id = ''
    error = 'IP Address'

    try:
        fw_rule_id = client.get_fw_rule_by_name(network_domain['id'],
                                                args['name']
                                            )['id']
    except NTTCCISAPIException as e:
        module.fail_json(changed=False, msg='%s' % e)
    except KeyError as e:
        module.fail_json(changed=False, msg='Invalid firewall rule name - %s' 
                                            % e)

    try:   
        if args['src_ip_list'] is not None:
            args['src_ip_list'] = client.get_ip_list_by_name(
                                                        network_domain['id'],
                                                        args['src_ip_list'],
                                                        args['version']
                                                    )['id']
        if args['dst_ip_list'] is not None:
            args['dst_ip_list'] = client.get_ip_list_by_name(
                                                        network_domain['id'],
                                                        args['dst_ip_list'],
                                                        args['version']
                                                    )['id']
        error = 'Port List'
        if args['src_port_list'] is not None:
            args['src_port_list'] = client.get_port_list_by_name(
                                                        network_domain['id'],
                                                        args['src_port_list']
                                                    )['id']
        if args['dst_port_list'] is not None:
            args['dst_port_list'] = client.get_port_list_by_name(
                                                        network_domain['id'],
                                                        args['dst_port_list']
                                                    )['id']
    except NTTCCISAPIException as e:
        module.fail_json(changed=False, msg='Invalid %s List - %s' % 
                                            (error, e))
    except Exception as e:
        module.fail_json(changed=False, msg='Invalid %s List - %s' %
                                            (error, e))

    try:
        result = client.update_fw_rule(fw_rule_id, args['action'],
                                       args['protocol'], args['src_ip'],
                                       args['src_ip_prefix'],
                                       args['src_ip_list'], args['dst_ip'],
                                       args['dst_ip_prefix'], 
                                       args['dst_ip_list'], 
                                       args['src_port_start'],
                                       args['src_port_end'],
                                       args['src_port_list'], 
                                       args['dst_port_start'],
                                       args['dst_port_end'],
                                       args['dst_port_list'], args['enabled'],
                                       args['position'], args['position_to'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not update the firewall rule - %s' % e)
    except KeyError as e:
        module.fail_json(changed=False, msg='Invalid data - %s' % e)

    msg = 'Successfully updated the firewall rule'
    module.exit_json(changed=True, msg=msg, data=result)


def delete_fw_rule(module, client, network_domain, name):
    try:
        fw_rule = client.get_fw_rule_by_name(network_domain['id'], name)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list of firewall rules - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    try:
        result = client.remove_fw_rule(fw_rule['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not delete the firewall rule - %s' % e,
        )
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Could not find the firewall rule - %s' % e,
        )

    msg = 'Successfully deleted the firewall rule'

    module.exit_json(changed=True, msg=msg, result=result)


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
            network_domain=dict(required=True, type='str'),
            action=dict(default='ACCEPT_DECISIVELY', 
                        choices=['ACCEPT_DECISIVELY', 'DENY']),
            version=dict(required=False, default=None, 
                         choices=['IPV4', 'IPV6']),
            protocol=dict(default='TCP',
                          choices=['TCP', 'UDP', 'IP', 'ICMP']),
            src_ip=dict(required=False, type='str'),
            src_ip_prefix=dict(required=False, type='str'),
            src_ip_list=dict(required=False, type='str'),
            dst_ip=dict(required=False, type='str'),
            dst_ip_prefix=dict(required=False, type='str'),
            dst_ip_list=dict(required=False, type='str'),
            src_port_start=dict(required=False, default=None, type='str'),
            src_port_end=dict(required=False, default=None, type='str'),
            src_port_list=dict(required=False, default=None, type='str'),
            dst_port_start=dict(required=False, default=None, type='str'),
            dst_port_end=dict(required=False, default=None, type='str'),
            dst_port_list=dict(required=False, default=None, type='str'),
            enabled=dict(default=True, type='bool'),
            position=dict(default='LAST',
                          choices=['FIRST', 'LAST', 'BEFORE', 'AFTER']),
            position_to=dict(required=False, default=None, type='str'),
            state=dict(default='list', choices=['list', 'create','delete', 
                               'get','update']),
            verify_ssl_cert=dict(required=False, default=True, type='bool')
        )
    )
    network_exists = []
    network_domain = {}
    credentials = get_credentials()
    name = module.params['name']
    network_domain_name = module.params['network_domain']
    datacenter = module.params['datacenter']
    state = module.params['state']

    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    client = NTTCCISClient((credentials[0],credentials[1]),
                          module.params['region'])

    # Find the provided Cloud Network Domain
    try:
        networks = client.list_network_domains(datacenter=datacenter)
        network_exists = filter(lambda x: x['name'] == network_domain_name, 
                            networks)
        network_domain = network_exists[0]
    except NTTCCISAPIException as e:
        module.fail_json(msg='Error: Failed to get a list of Cloud Network '
                         'Domains - %s' % e)
    except IndexError:
        module.fail_json(
                changed=False,
                msg='Cloud Network Domain not found',
            )

    if state == 'list':
        list_fw_rule(module, client, network_domain)
    elif state == 'create':
        create_fw_rule(module, client, network_domain)
    elif state == 'get':
        get_fw_rule(module, client, network_domain, name)
    elif state == 'update':
        update_fw_rule(module, client, network_domain)
    elif state == 'delete':
        delete_fw_rule(module, client, network_domain, name)

    
if __name__ == '__main__':
    main()