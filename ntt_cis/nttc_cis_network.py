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
# List, Create, Delete Cloud Network Domains (CND)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_network
short_description: List, Create, Delete Cloud Network Domains (CND)
description:
    - List, Create, Delete Cloud Network Domains (CND)
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
        required: true
    description:
        description:
            - The description of the Cloud Network Domain
        required: false
    network_type:
        description:
            - The type of Cloud Network Domain
        required: true
        default: None
        choices:
          - [ADVANCED,ESSENTIALS,ENTERPRISE]
    new_name:
        description:
            - The new name of the Cloud Network Domain, used when updating
        required: true
    state:
        description:
            - The action to be performed
        required: true
        default: create
        choices: [create, delete, update, get]
    wait:
        description:
            - Should Ansible wait for the task to complete before continuing
        required: false
        default: false
        choices: [true, false]
    wait_time:
        description: The maximum time the Ansible should wait for the task
                     to complete in seconds
        required: false
        default: 600
    wait_poll_interval:
        description:
            - The time in between checking the status of the task in seconds
        required: false
        default: 10
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
# Create a Cloud Network Domain
- nttc_cis_network:
  region: na
  location: NA9
  name: "xxxxx"
  network_type: "ESSENTIALS"
  description: "A test Network Domain"
  state: present
  wait: True
# Delete a Cloud Network Domain
- nttc_cis_network:
  region: na
  location: NA9
  name: "xxxxx"
  state: absent
  wait: True
# List a Cloud Network Domain
- nttc_cis_network:
  region: na
  datacenter: NA9
  name: "xxxxx"
  state: query
'''

RETURN = '''
network:
    description: Dictionary of the network domain
    contains:
        id:
            description: Network Domain ID
            type: string
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        name:
            description: Network Domain name
            type: string
            sample: "My network"
        description:
            description: Network Domain description
            type: string
            sample: "My network description"
        datacenterId:
            description: Datacenter id/location
            type: string
            sample: NA3
        state: Status of the Network Domain
            type: string
            sample: NORMAL
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


def create_network_domain(module, client, datacenter, name, description):
    if 'network_type' not in module.params:
        module.fail_json(
            changed=False,
            msg='Error: A Network Type is required.'
        )
    if module.params['network_type'] is None:
        module.fail_json(
            changed=False,
            msg='Error: A Network Type is required.'
        )
    network_type = module.params['network_type']

    try:
        result = client.create_network_domain(datacenter, name, network_type,
                                              description)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Error: could not create the Cloud Network Domain - %s' % e,
        )
    if module.params['wait']:
        wait_for_network_domain(module, client, name, datacenter, 'NORMAL')
    msg = 'Cloud Network Domain %s has been successfully created in %s' % (
           name, datacenter)
    try:
        networks = client.list_network_domains(datacenter=datacenter)
    except NTTCCISAPIException as e:
        msg='Warning: Could not verify the Cloud Network Domain was created'
    network_domain = filter(lambda x: x['name'] == name, networks)
    network = network_domain[0]
    module.exit_json(changed=True, msg=msg, network=network)


def update_network_domain(module, client, network_domain):
    name = network_domain['name']
    datacenter = network_domain['datacenterId']
    params = {}
    if module.params['network_type'] is not None:
        params['type'] = module.params['network_type']
    if module.params['new_name'] is not None:
        params['name'] = module.params['new_name']
        name = module.params['new_name']
    if module.params['description']:
        params['description'] = module.params['description']

    try:
        result = client.update_network_domain(params, network_domain['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Error: could not update the Cloud Network Domain - %s' % e
        )
    if module.params['wait']:
        wait_for_network_domain(module, client, name, datacenter, 'NORMAL')
    msg = 'Cloud Network Domain %s has been successfully updated in %s' % (
           name, datacenter)
    try:
        networks = client.list_network_domains(datacenter=datacenter)
    except NTTCCISAPIException as e:
        msg='Warning: Could not verify the Cloud Network Domain was updated'
    network_domain_new = filter(lambda x: x['name'] == name, networks)
    network = network_domain_new[0]
    module.exit_json(changed=True, msg=msg, network=network)


def delete_network_domain(module, client, network_domain):
    network_domain_result = True
    try:
        result = client.delete_network_domain(network_domain['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Error: could not delete the Cloud Network Domain - %s' % e,
        )
    if module.params['wait']:
        while network_domain_result:
            networks = client.list_network_domains(datacenter=
                                           network_domain['datacenterId'])
            network_domain_result = filter(lambda x: x['id'] == 
                                           network_domain['id'],
                                           networks)
            sleep(module.params['wait_poll_interval'])
    msg = 'Cloud Network Domain %s has been successfully removed in %s' % (
           network_domain['name'], network_domain['datacenterId'])    
    module.exit_json(changed=True, msg=msg)


def wait_for_network_domain(module, client, name, datacenter, state):
    actual_state = ''
    network = {}
    while actual_state != state:
        try:
            networks = client.list_network_domains(datacenter=datacenter)
        except NTTCCISAPIException as e:
            module.fail_json(msg='Error: Failed to get a list of Cloud '
                                 'Network Domains - %s' % e)
        network_domain = filter(lambda x: x['name'] == name, networks)
        actual_state = network_domain[0]['state']
        sleep(module.params['wait_poll_interval'])


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            name=dict(required=True, type='str'),
            description=dict(required=False, type='str'),
            network_type=dict(default=None, choices=['ADVANCED',
                              'ESSENTIALS', 'ENTERPRISE']),
            new_name=dict(required=False, default=None, type='str'),
            state=dict(default='create', choices=['create', 'delete',
                       'get', 'update']),
            wait=dict(required=False, default=False, type='bool'),
            wait_time=dict(required=False, default=600, type='int'),
            wait_poll_interval=dict(required=False, default=10, type='int'),
            verify_ssl_cert=dict(required=False, default=True, type='bool')
        )
    )
    
    credentials = get_credentials()
    name = module.params['name']
    datacenter = module.params['datacenter']
    description = module.params['description']
    state = module.params['state']
    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    client = NTTCCISClient((credentials[0],credentials[1]),
                          module.params['region'])

    # Get a list of existing CNDs and check if the new name already exists
    try:
        networks = client.list_network_domains(datacenter=datacenter)
    except NTTCCISAPIException as e:
        module.fail_json(msg='Error: Failed to get a list of Cloud Network '
                         'Domains - %s' % e)
    network_exists = filter(lambda x: x['name'] == name, networks)

    # List Cloud Network Domains
    if state == 'get':
        if network_exists:
            module.exit_json(
                changed=False,
                msg='Cloud Network Domain exists',
                network=network_exists[0]
            )
        else:
            module.exit_json(
                changed=False,
                msg='Cloud Network Domain not found',
                network=None
            )
    # Create the Cloud Network Domain
    elif state == 'create':
        # Handle case where CND name already exists
        if network_exists:
            module.exit_json(
                changed=False,
                msg="Cloud Network Domain already exists",
                network=network_exists[0]
            )
        create_network_domain(module, client, datacenter, name, description)
    # Update a Cloud Network Domain
    elif state == 'update':
        if not network_exists:
            module.exit_json(
                changed=False,
                msg='Cloud Network Domain not found',
            )
        update_network_domain(module, client, network_exists[0])
    # Delete the Cloud Network Domain
    elif state == 'delete':
        if not network_exists:
            module.exit_json(
                changed=False,
                msg='Cloud Network Domain not found',
            )
        delete_network_domain(module, client, network_exists[0])

    
if __name__ == '__main__':
    main()