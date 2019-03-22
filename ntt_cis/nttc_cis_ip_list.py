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
# List, get, create, modify and delete IP Address Lists

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_ip_list
short_description: List, get, create, modify and delete IP Address Lists
description:
    - List, get, create, modify and delete IP Address Lists
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
            - The name of the IP Address List
        required: false
    description:
        description:
            - The description of the IP Address List
        required: false
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        default: None
    ip_addresses:
        description:
            - List of IP Addresses with begin, end or prefix
        required: false
    ip_addresses_nil:
        description:
            - Used on updating to remove all IP addresses
        required: false
        choices: [true, false]
    child_ip_list:
        description:
            - List of IP adddress UUIDs to be included in this ip address
        required: false
    child_ip_list_nil
        description:
            - Used on updating to remove all child IP address lists
        required: false
        choices: [true, false]
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
# List IP Address Lists
- nttc_cis_ip_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      version: IPV6
      state: list
# Get a specific IP Address List
- nttc_cis_ip_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "APITEST"
      state: get
# Create a IP Address List
- nttc_cis_ip_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      version: IPV4
      name: "APITEST2"
      ip_addresses:
        - begin: "10.0.7.10"
      child_ip_list:
        - "ffffffff-fff-ffff-ffff-ffffffffffff"
      state: create
# Update an IP Address List
  - nttc_cis_ip_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      version: IPV4
      name: "APITEST2"
      ip_addresses:
        - begin: "10.0.7.10"
      child_ip_list_nil: True
      state: update
# Delete a IP Address List
- nttc_cis_ip_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      version: IPV4
      name: "APITEST"
      state: delete
'''

RETURN = '''
ip_address_list:
    description: a single or list of Port List objects or strings
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

def list_ip_list(module, client, network_domain, version):
    try:
        result = client.list_ip_list(network_domain['id'], version)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list IP Address Lists - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    if len(result) > 0:
        msg = 'Found %d IP Address Lists in %s' % (len(result), 
                                             network_domain['name'])
    else:
        msg = 'No IP Address Lists found'

    module.exit_json(changed=False, msg=msg, ip_address_list=result)


def create_ip_list(module, client, network_domain, name, description,
                   ip_addresses, child_ip_list, version):
    try:
        result = client.create_ip_list(network_domain['id'], name,
                                        description, ip_addresses, 
                                        child_ip_list, version)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not create the IP Address List - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    msg = 'Successfully created the IP Address List'
    module.exit_json(changed=True, msg=msg, ip_address_list_id=result)


def update_ip_list(module, client, network_domain, name, description,
                   ip_addresses, ip_addresses_nil, child_ip_list, 
                   child_ip_list_nil, version):

    try:
        ip_address_list = client.get_ip_list_by_name(network_domain['id'], 
                                               name, version)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list IP Address Lists - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    try:
        result = client.update_ip_list(network_domain['id'],
                                        ip_address_list['id'], description, 
                                        ip_addresses,  ip_addresses_nil, 
                                        child_ip_list, child_ip_list_nil)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not update the IP Address List - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='No IP Address List found'
        )

    msg = 'Successfully updated the IP Address List'
    module.exit_json(changed=True, msg=msg, result=result)


def get_ip_list(module, client, network_domain, name, version):
    result = {}
    if name is None:
        module.fail_json(
            changed=False,
            msg='A value for name is required'
        )

    try:
        result = client.get_ip_list_by_name(network_domain['id'], name, 
                                            version)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve the IP Address List - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    if result is None:
        module.fail_json(
            changed=False,
            msg='No IP Address List found'
        )

    msg = 'Found the IP Address List'

    module.exit_json(changed=False, msg=msg, ip_address_list=result)


def delete_ip_list(module, client, network_domain, name, version):
    try:
        ip_address_list = client.get_ip_list_by_name(network_domain['id'], 
                                               name, version)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list IP Address Lists - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    try:
        result = client.remove_ip_list(ip_address_list['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not delete the IP Address List - %s' % e,
        )
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Could not find the IP Address List - %s' % e,
        )

    msg = 'Successfully deleted the IP Address List'

    module.exit_json(changed=True, msg=msg, result=result)


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
            description=dict(required=False, type='str'),
            version=dict(required=False, default=None, type='str', 
                         choices=['IPV4', 'IPV6']),
            ip_addresses=dict(required=False, type='list'),
            ip_addresses_nil=dict(required=False, default=False, type='bool'),
            child_ip_list=dict(required=False, type='list'),
            child_ip_list_nil=dict(required=False, default=False, 
                                   type='bool'),
            network_domain=dict(required=True, type='str'),
            state=dict(default='list', choices=['list', 
                               'create','delete', 
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
    description = module.params['description']
    child_ip_list = module.params['child_ip_list']
    child_ip_list_nil = module.params['child_ip_list_nil']
    ip_addresses = module.params['ip_addresses']
    ip_addresses_nil = module.params['ip_addresses_nil']
    version = module.params['version']

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
        list_ip_list(module, client, network_domain, version)
    elif state == 'create':
        create_ip_list(module, client, network_domain, name, description, 
                        ip_addresses, child_ip_list, version)
    elif state == 'update':
        update_ip_list(module, client, network_domain, name, description, 
                        ip_addresses, ip_addresses_nil, child_ip_list, 
                        child_ip_list_nil, version)
    elif state == 'get':
        get_ip_list(module, client, network_domain, name, version)
    elif state == 'delete':
        delete_ip_list(module, client, network_domain, name, version)

    
if __name__ == '__main__':
    main()