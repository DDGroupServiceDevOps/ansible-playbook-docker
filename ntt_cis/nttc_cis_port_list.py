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
# List, get, create, modify and delete Firewall Port Lists

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_port_list
short_description: List, get, create, modify and delete Firewall Port Lists
description:
    - List, get, create, modify and delete Firewall Port Lists
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
            - The name of the Port List
        required: false
    description:
        description:
            - The description of the Port List
        required: false
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        default: None
    ports:
        description:
            - List of port groups with port_begin and optionally port_end
        required: false
    ports_nil:
        description:
            - Used on updating to remove all ports
        required: false
        choices: [true, false]
    child_port_list:
        description:
            - List of port list names that will be included in this port list
        required: false
    child_port_list_nil
        description:
            - Used on updating to remove all child port lists
        required: false
        choices: [true, false]
    state:
        description:
            - The action to be performed
        required: true
        default: create
        choices: [get_public_ipv4,add_public_ipv4,delete_public_ipv4,
                  list_reserved_ip,unreserve_ip,reserve_ip]
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
# List Port Lists
- nttc_cis_port_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      state: list
# Get a specific Port List
- nttc_cis_port_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "APITEST"
      state: get
# Create a Port List
- nttc_cis_port_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "APITEST"
      description: "API Testing"
      ports:
        - port_begin: 1077
        - port_begin: 1177
          port_end: 1277
      child_port_list:
        - "APITEST_2"
      state: create
# Update a Port List
- nttc_cis_port_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "APITEST"
      description: "API Testing 2"
      ports_nil: True
      child_port_list:
        - "APITEST_3"
      state: update
# Delete a Port List
- nttc_cis_port_list:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "APITEST"
      state: delete
'''

RETURN = '''
port_list:
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

def list_port_list(module, client, network_domain):
    try:
        result = client.list_port_list(network_domain['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list Port Lists - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    if len(result) > 0:
        msg = 'Found %d Port Lists in %s' % (len(result), 
                                             network_domain['name'])
    else:
        msg = 'No Port Lists found'

    module.exit_json(changed=False, msg=msg, port_list=result)


def create_port_list(module, client, network_domain, name, description, ports,
                     child_port_list):
    try:
        result = client.create_port_list(network_domain['id'], name,
                                        description, ports, child_port_list)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not create the Port List - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    msg = 'Successfully created the Port List'
    module.exit_json(changed=True, msg=msg, port_list_id=result)


def update_port_list(module, client, network_domain, name, description, ports,
                     ports_nil, child_port_list, child_port_list_nil):

    try:
        port_list = client.get_port_list_by_name(network_domain['id'], name)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list Port Lists - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    try:
        result = client.update_port_list(network_domain['id'],
                                        port_list['id'], description, ports, 
                                        ports_nil, child_port_list, 
                                        child_port_list_nil)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not update the Port List - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='No Port List found'
        )

    msg = 'Successfully updated the Port List'
    module.exit_json(changed=True, msg=msg, result=result)


def get_port_list(module, client, network_domain, name):
    result = {}
    if name is None:
        module.fail_json(
            changed=False,
            msg='A value for name is required'
        )

    try:
        result = client.get_port_list_by_name(network_domain['id'], name)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve the Port List - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    if result is None:
        module.fail_json(
            changed=False,
            msg='No Port List found'
        )

    msg = 'Found the Port List'

    module.exit_json(changed=False, msg=msg, port_list=result)


def delete_port_list(module, client, network_domain, name):
    try:
        port_list = client.get_port_list_by_name(network_domain['id'], name)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list Port Lists - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    try:
        result = client.remove_port_list(port_list['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not delete the Port List - %s' % e,
        )
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Could not find the Port List - %s' % e,
        )

    msg = 'Successfully deleted the Port List'

    module.exit_json(changed=True, msg=msg, result=result)


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
            description=dict(required=False, type='str'),
            ports=dict(required=False, type='list'),
            ports_nil=dict(required=False, default=False, type='bool'),
            child_port_list=dict(required=False, type='list'),
            child_port_list_nil=dict(required=False, default=False, 
                                     type='bool'),
            network_domain=dict(required=True, type='str'),
            state=dict(default='list', choices=['list','create','delete', 
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
    child_port_list = module.params['child_port_list']
    child_port_list_nil = module.params['child_port_list_nil']
    ports = module.params['ports']
    ports_nil = module.params['ports_nil']

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
        list_port_list(module, client, network_domain)
    elif state == 'create':
        create_port_list(module, client, network_domain, name, description, 
                        ports, child_port_list)
    elif state == 'update':
        update_port_list(module, client, network_domain, name, description, 
                        ports, ports_nil, child_port_list, 
                        child_port_list_nil)
    elif state == 'get':
        get_port_list(module, client, network_domain, name)
    elif state == 'delete':
        delete_port_list(module, client, network_domain, name)

    
if __name__ == '__main__':
    main()