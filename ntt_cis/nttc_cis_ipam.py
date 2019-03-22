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
# IP Address Management

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_network
short_description: IP Address Management
description:
    - IP Address Management
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
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        default: None
    vlan:
        description:
            - The name of a VLAN
        required: false
    ip_address:
        description:
            - An IPv4 or IPv6 address
        required: false
    version:
        description:
            - The IP version
        required: false
        choices: [4, 6]
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
# List Public IPv4 blocks
- nttc_cis_ipam:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      state: list_public_ipv4
# Get a specific public IPv4 block
- nttc_cis_ipam:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      id: "ffffffff-fff-ffff-ffff-ffffffffffff"
      state: get_public_ipv4
# Add a public IPv4 block
- nttc_cis_ipam:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      state: add_public_ipv4
# Delete a public IPv4 block
- nttc_cis_ipam:
      region: na
      datacenter: NA9
      network_domain: "UCaaS RnD"
      id: "ffffffff-fff-ffff-ffff-ffffffffffff"
      state: delete_public_ipv4
# List IP Reservations
  - nttc_cis_ipam:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      vlan: "yyyy"
      state: list_reserved_ip
      version: 4
# Reserve an IP Address
- nttc_cis_ipam:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      vlan: "yyyy"
      ip_address: "xxxx::xxxx"
      version: 6
      state: reserve_ip
# Unreserve an IP Address
- nttc_cis_ipam:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      vlan: "yyyy"
      ip_address: "xxxx::xxxx"
      version: 6
      state: unreserve_ip
'''

RETURN = '''
ip_object:
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


def list_public_ipv4(module, client, network_domain):
    try:
        result = client.list_public_ipv4(network_domain['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not list the public IPv4 blocks - %s' % e,
        )
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    if len(result) > 0:
        msg = 'Found %d public IPv4 blocks in %s' % (
                   len(result), network_domain['name'])
    else:
        msg = 'No public IPv4 blocks found'

    module.exit_json(changed=False, msg=msg, public_ipv4_blocks=result)


def get_public_ipv4(module, client, public_ipv4_block_id):
    if public_ipv4_block_id is None:
        module.fail_json(
            changed=False,
            msg='A value for id is required'
        )

    try:
        result = client.get_public_ipv4(public_ipv4_block_id)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get the public IPv4 block - %s' % e,
        )
    msg = 'Found the public IPv4 block'

    module.exit_json(changed=False, msg=msg, public_ipv4_block=result)



def add_public_ipv4(module, client, network_domain):
    try:
        result = client.add_public_ipv4(network_domain['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not add a public IPv4 block - %s' % e
        )
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    msg = 'Successfully added a public IPv4 block in %s' % (
                                                    network_domain['name'])

    module.exit_json(changed=True, msg=msg, public_ipv4_block_id=result)


def delete_public_ipv4(module, client, public_ipv4_block_id):
    if public_ipv4_block_id is None:
        module.fail_json(
            changed=False,
            msg='A value for id is required'
        )
    try:
        result = client.remove_public_ipv4(public_ipv4_block_id)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not delete the public IPv4 block - %s' % e,
        )
    msg = 'Successfully deleted the public IPv4 block'

    module.exit_json(changed=True, msg=msg)


def list_reserved_ip(module, client, datacenter, vlan, version):
    try:
        vlan_id = vlan['id']
    except KeyError:
        vlan_id = None

    if version != 4 and version != 6:
        module.fail_json(changed=False, msg='Invalid IP version - %s' %
                         version)

    try:
        result = client.list_reserved_ip(vlan_id, datacenter, version)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not list the private IPv%d reservations - %s' % (
                version, e)
        )

    if len(result) > 0:
        msg = 'Found %d private IPv%d reservations ' % (len(result), version)
    else:
        msg = 'No private IPv%d reservations found' % version

    module.exit_json(changed=False, msg=msg, private_ip=result)


def reserve_ip(module, client, vlan, ip_address, description,
                         version):
    try:
        vlan_id = vlan['id']
    except KeyError:
        module.fail_json(changed=False,
                        msg='A valid VLAN is required')

    try:
        result = client.reserve_ip(vlan_id, ip_address, description,
                                           version)
    except NTTCCISAPIException as e:
        module.fail_json(
                    changed=False,
                    msg='Could not reserve the private IPv%d address - %s' % (
                        version, e)
                )
    if result != ip_address:
        module.fail_json(
                    changed=False,
                    msg='Could not reserve the private IPv%d address - %s' % (
                        version, ip_address)
                )
    msg = 'Successfully reserved to the private IPv%d address' % version

    module.exit_json(changed=True, msg=msg, reserved_private_ip=result)


def unreserve_ip(module, client, vlan, ip_address, version):
    try:
        vlan_id = vlan['id']
    except KeyError:
        module.fail_json(changed=False,
                        msg='A valid VLAN is required')

    try:
        result = client.unreserve_ip(vlan_id, ip_address, version)
    except NTTCCISAPIException as e:
        module.fail_json(
                changed=False,
                msg='Could not unreserve the private IPv%d address - %s' % (
                    version, e)
            )
    msg = 'Successfully unreserved the private IPv%d address' % version

    module.exit_json(changed=True, msg=msg)


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
            description=dict(required=False, type='str'),
            network_domain=dict(required=True, type='str'),
            vlan=dict(required=False, default=None, type='str'),
            ip_address=dict(required=False, default=None, type='str'),
            version=dict(required=False, default=4, choices=[4,6], 
                         type='int'),
            id=dict(default=None, type='str'),
            state=dict(default='list_public_ipv4', choices=['get_public_ipv4', 
                               'add_public_ipv4', 'delete_public_ipv4',
                               'list_reserved_ip', 'unreserve_ip',
                               'reserve_ip']),
            verify_ssl_cert=dict(required=False, default=True, type='bool')
        )
    )
    network_exists = []
    vlan = {}
    credentials = get_credentials()
    name = module.params['name']
    network_domain = module.params['network_domain']
    vlan_name = module.params['vlan']
    datacenter = module.params['datacenter']
    description = module.params['description']
    state = module.params['state']
    object_id = module.params['id']
    ip_address = module.params['ip_address']
    version = module.params['version']
    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    client = NTTCCISClient((credentials[0],credentials[1]),
                          module.params['region'])

    # Find the provided Cloud Network Domain
    try:
        networks = client.list_network_domains(datacenter=datacenter)
    except NTTCCISAPIException as e:
        module.fail_json(msg='Error: Failed to get a list of Cloud Network '
                         'Domains - %s' % e)
    network_exists = filter(lambda x: x['name'] == network_domain, networks)
    if not network_exists:
        module.fail_json(
                changed=False,
                msg='Cloud Network Domain not found',
            )

    # find the provided VLAN
    if vlan_name is not None:
        try:
            vlans = client.list_vlans(
                    datacenter=datacenter,
                    network_domain_id=network_exists[0]['id'],
                )
            vlan_exists = filter(lambda x: x['name'] == vlan_name, vlans)
            vlan = vlan_exists[0]
        except NTTCCISAPIException as e:
            pass
        except KeyError:
            module.fail_json(changed=False,
                             msg='A valid Network Domain is required')
        except IndexError:
            pass
        

    if state == 'list_public_ipv4':
        list_public_ipv4(module, client, network_exists[0])
    elif state == 'add_public_ipv4':
        add_public_ipv4(module, client, network_exists[0])
    elif state == 'get_public_ipv4':
        get_public_ipv4(module, client, object_id)
    elif state == 'delete_public_ipv4':
        delete_public_ipv4(module, client, object_id)
    elif state == 'list_reserved_ip':
        list_reserved_ip(module, client, datacenter, vlan, version)
    elif state == 'reserve_ip':
        reserve_ip(module, client, vlan, ip_address, description,
                           version)
    elif state == 'unreserve_ip':
        unreserve_ip(module, client, vlan, ip_address, version)

    
if __name__ == '__main__':
    main()