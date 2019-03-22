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
# Get, Create, Update, Delete VLANs

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_vlan
short_description: List, Create, Update, Delete VLANs
description:
    - Get, Create, Delete VLANs
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
    network_domain:
        description:
            - The name of the Cloud Network Domain
        required: true
    name:
        description:
            - The name of the VLAN
        required: true
    description:
        description:
            - The description of the VLAN
        required: false
    ipv4_network_address:
        description:
            - The IPv4 network address for the VLAN
        required: false
    ipv4_prefix_size:
        description:
            - The prefix size for the VLAN (e.g. /24)
        required: false
    ipv6_network_address:
        description:
            - The IPv6 network address for the VLAN (used for searching only)
        required: false
    vlan_type:
        description:
            - The type of VLAN
        required: true
        default: attachedVlan
        choices:
          - [attachedVlan,detachedVlan]
    attached_vlan_gw:
        description:
            - Required if vlan_type == attachedVlan. HIGH == .254, LOW == .1
        required: false
        default: LOW
        choices:
            - [LOW, HIGH]
    detached_vlan_gw:
        description:
            - Required if vlan_type == detachedVlan. IPv4 address of the gw
            - Cannot be the first or last address in the range
        required: false
    detached_vlan_gw_ipv6:
        description:
            - Required if vlan_type == detachedVlan. IPv6 address of the gw
            - Cannot be any of the first 32 addresses in the range
        required: false
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
# Create a VLAN
- name: Get the Infrastructure VLAN
    nttc_cis_vlan:
      region: na
      datacenter: NA9
      network_domain: "APITEST"
      name: "VLAN_TEST"
      ipv4_network_address: "10.0.0.0"
      ipv4_prefix_size: 24
      vlan_type: "detachedVlan"
      detached_vlan_gw: "10.0.0.1"
      wait: True
      state: create
# Update a VLAN
- name: Update the VLAN
    nttc_cis_vlan:
      region: na
      datacenter: NA9
      network_domain: "APITEST"
      name: "VLAN_TEST"
      description: "Test VLAN"
      detached_vlan_gw: "10.0.0.1"
      detached_vlan_gw_ipv6: "xxxx::50"
      wait: True
      state: update
# Delete a VLAN
- name: Delete a VLAN
    nttc_cis_vlan:
      region: na
      datacenter: NA9
      network_domain: "APITEST"
      name: "VLAN_TEST"
      state: delete
# Get a VLAN
- name: Get the Infrastructure VLAN
  nttc_cis_vlan:
    region: na
    datacenter: NA9
    network_domain: "APITEST"
    name: "VLAN_TEST"
    state: get
'''

RETURN = '''
vlan:
    description: Dictionary of the vlan
    contains:
        id:
            description: VLAN ID
            type: string
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        name:
            description: VLAN name
            type: string
            sample: "My network"
        description:
            description: VLAN description
            type: string
            sample: "My network description"
        datacenterId:
            description: Datacenter id/location
            type: string
            sample: NA9
        networkDomainId:
            description: The UUID of the home Cloud Network Domain of the VLAN
            type: string
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        state: Status of the VLAN
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


def create_vlan(module, client, network_domain_id):
    if 'vlan_type' not in module.params:
        module.fail_json(
            changed=False,
            msg='Error: A VLAN Type is required.'
        )
    if 'ipv4_network_address' not in module.params:
        module.fail_json(
            changed=False,
            msg='Error: An IPv4 network address is required.'
        )
    if 'ipv4_prefix_size' not in module.params:
        module.fail_json(
            changed=False,
            msg='Error: An IPv4 Prefix Size is required.'
        )

    datacenter = module.params['datacenter']
    name = module.params['name']
    vlan_type = module.params['vlan_type']
    ipv4_network = module.params['ipv4_network_address']
    ipv4_prefix = module.params['ipv4_prefix_size']

    if vlan_type == 'attachedVlan':
        if 'attached_vlan_gw' not in module.params:
            module.fail_json(
                changed=False,
                msg='Error: An Attached VLAN gateway is required.'
            )
    elif vlan_type == 'detachedVlan':
        if 'detached_vlan_gw' not in module.params:
            module.fail_json(
                changed=False,
                msg='Error: An Detached VLAN gateway is required.'
            )

    try:
        if vlan_type == 'attachedVlan':
            gw = module.params['attached_vlan_gw']
            result = client.create_vlan(
                            networkDomainId=network_domain_id,
                            name=name,
                            description=module.params['description'],
                            privateIpv4NetworkAddress=ipv4_network,
                            privateIpv4PrefixSize=ipv4_prefix,
                            attachedVlan=True,
                            attachedVlan_gatewayAddressing=gw
                        )
        elif vlan_type == 'detachedVlan':
            gw = module.params['detached_vlan_gw']
            result = client.create_vlan(
                            networkDomainId=network_domain_id,
                            name=name,
                            description=module.params['description'],
                            privateIpv4NetworkAddress=ipv4_network,
                            privateIpv4PrefixSize=ipv4_prefix,
                            detachedVlan=True,
                            detachedVlan_ipv4GatewayAddress=gw
                        )
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Error: could not create the VLAN - %s' % e
        )
    if module.params['wait']:
        wait_for_vlan(module, client, name, datacenter, network_domain_id, 
                     'NORMAL')
    msg = 'VLAN %s has been successfully created in %s' % (
           name, module.params['network_domain'])
    try:
        vlans = client.list_vlans(
                    datacenter=datacenter,
                    network_domain_id=network_domain_id
                )
    except NTTCCISAPIException as e:
        msg='Warning: Could not verify the VLAN was created'
    vlan_exists = filter(lambda x: x['name'] == name, vlans)
    vlan = vlan_exists[0]
    module.exit_json(changed=True, msg=msg, vlan=vlan)


def update_vlan(module, client, vlan):
    name = vlan['name']
    datacenter = vlan['datacenterId']
    network_domain_id = vlan['networkDomain']['id']
    ipv4GatewayAddress = module.params['detached_vlan_gw']
    ipv6GatewayAddress = module.params['detached_vlan_gw_ipv6']
    params = {}
    if module.params['new_name'] is not None:
        params['name'] = module.params['new_name']
        name = module.params['new_name']
    if module.params['description']:
        params['description'] = module.params['description']
    if (ipv4GatewayAddress or ipv6GatewayAddress) and not vlan['attached']:
        if ipv4GatewayAddress:
            params['ipv4GatewayAddress'] =  ipv4GatewayAddress
        if ipv6GatewayAddress:
            params['ipv6GatewayAddress'] =  ipv6GatewayAddress

    try:
        result = client.update_vlan(params=params,vlan_id=vlan['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Error: could not update the VLAN - %s' % e
        )
    if module.params['wait']:
        wait_for_vlan(module, client, name, datacenter, 
                      network_domain_id, 'NORMAL')
    msg = 'VLAN %s has been successfully updated in %s' % (
           name, module.params['datacenter'])
    try:
        vlans = client.list_vlans(
                    datacenter=datacenter,
                    network_domain_id=network_domain_id
                )
    except NTTCCISAPIException as e:
        msg='Warning: Could not verify the VLAN was updated'
    vlan_new = filter(lambda x: x['name'] == name, vlans)
    vlan = vlan_new[0]
    module.exit_json(changed=True, msg=msg, vlan=vlan)


def delete_vlan(module, client, vlan):
    vlan_result = True
    name = vlan['name']
    datacenter = vlan['datacenterId']
    network_domain_id = vlan['networkDomain']['id']
    try:
        result = client.delete_vlan(vlan['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Error: could not delete the VLAN - %s' % e,
        )
    if module.params['wait']:
        while vlan_result:
            vlans = client.list_vlans(
                    datacenter=datacenter,
                    network_domain_id=network_domain_id
                )
            vlan_result = filter(lambda x: x['id'] == 
                                           vlan['id'], vlans)
            sleep(module.params['wait_poll_interval'])
    msg = 'VLAN %s has been successfully removed in %s' % (
           vlan['name'], vlan['datacenterId'])    
    module.exit_json(changed=True, msg=msg)


def wait_for_vlan(module, client, name, datacenter, network_domain_id, state):
    actual_state = ''
    vlan = {}
    while actual_state != state:
        try:
            vlans = client.list_vlans(
                    datacenter=datacenter,
                    network_domain_id=network_domain_id
                )
        except NTTCCISAPIException as e:
            module.fail_json(msg='Error: Failed to get a list of VLANS - %s' 
                             % e)
        vlan = filter(lambda x: x['name'] == name, vlans)
        if len(vlan) > 0:
            actual_state = vlan[0]['state']
        else:
            module.fail_json(msg='Error: Failed to gfind the VLAN - %s' 
                             % name)
        sleep(module.params['wait_poll_interval'])


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            name=dict(required=True, type='str'),
            description=dict(required=False, type='str'),
            ipv4_network_address=dict(required=False, type='str'),
            ipv4_prefix_size=dict(required=False, type='int'),
            ipv6_network_address=dict(required=False, type='str'),
            vlan_type=dict(default='attachedVlan', choices=['attachedVlan',
                              'detachedVlan']),
            attached_vlan_gw=dict(required=False,default='LOW', choices=
                                  ['LOW', 'HIGH']),
            detached_vlan_gw=dict(required=False, type='str'),
            detached_vlan_gw_ipv6=dict(required=False, type='str'),
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
    state = module.params['state']
    network_domain_name = module.params['network_domain']
    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    client = NTTCCISClient((credentials[0],credentials[1]),
                          module.params['region'])

    # Get the CND object based on the supplied name
    try:
        networks = client.list_network_domains(datacenter=datacenter)
    except NTTCCISAPIException as e:
        module.fail_json(msg='Error: Failed to get a list of Cloud Network '
                         'Domains - %s' % e)
    network_exists = filter(
                        lambda x: x['name'] == network_domain_name, 
                        networks
                     )
    if not network_exists:
        module.fail_json(msg='Error: Failed to find the Cloud Network Domain'
                             ' Check the network_domain value')
    # Get a list of existing VLANs and check if the new name already exists
    try:
        vlans = client.list_vlans(
                    datacenter=datacenter,
                    network_domain_id=network_exists[0]['id'],
                )
    except NTTCCISAPIException as e:
        module.fail_json(msg='Error: Failed to get a list of VLANs - %s' % e)

    vlan_exists = filter(lambda x: x['name'] == name, vlans)

    # Get the VLAN
    if state == 'get':
        if vlan_exists:
            module.exit_json(
                changed=False,
                msg='VLAN exists',
                vlan=vlan_exists[0]
            )
        else:
            module.exit_json(
                changed=False,
                msg='VLAN not found',
                vlan=None
            )
    # Create the VLAN
    elif state == 'create':
        # Handle case where VLAN name already exists
        if vlan_exists:
            module.exit_json(
                changed=False,
                msg="VLAN already exists",
                vlan=vlan_exists[0]
            )
        create_vlan(module, client, network_exists[0]['id'])
    # Update a VLAN
    elif state == 'update':
        if not vlan_exists:
            module.exit_json(
                changed=False,
                msg='VLAN not found',
            )
        update_vlan(module, client, vlan_exists[0])
    # Delete the VLAN
    elif state == 'delete':
        if not vlan_exists:
            module.exit_json(
                changed=False,
                msg='VLAN not found',
            )
        delete_vlan(module, client, vlan_exists[0])

    
if __name__ == '__main__':
    main()