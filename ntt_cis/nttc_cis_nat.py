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
# List, Add and Remove NAT entries

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_network
short_description: List, Add and Remove NAT entries
description:
    - List, Add and Remove NAT entries
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
    internal_ip:
        description:
            - The internal IP address of the NAT
        required: false
    external_ip:
        description:
            - The external IP address of the NAT
        required: false
    id:
        description:
            - The UUID of the NAT rule
        required: false
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
# List NAT rules
- nttc_cis_nat:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      state: list_nat_rule
# Get a specific NAT rule
- nttc_cis_nat:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      id: "ffffffff-fff-ffff-ffff-ffffffffffff"
      state: get_nat_rule
# Create a NAT rule
- nttc_cis_nat:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      internal_ip: "x.x.x.x"
      external_ip: "y.y.y.y"
      state: create_nat_rule
# Delete a NAT rule
- nttc_cis_nat:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      id: "ffffffff-fff-ffff-ffff-ffffffffffff"
      state: delete_nat_rule
'''

RETURN = '''
nat_rule:
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

def list_nat_rule(module, client, network_domain):
    try:
        result = client.list_nat_rule(network_domain['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not retrieve a list of NAT(s) - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )
    if len(result) > 0:
        msg = 'Found %d NAT(s) in %s' % (len(result), network_domain['name'])
    else:
        msg = 'No NAT(s) found'

    module.exit_json(changed=False, msg=msg, nat=result)


def create_nat_rule(module, client, network_domain, internal_ip, external_ip):
    if internal_ip is None or external_ip is None:
        module.fail_json(
            changed=False,
            msg='Valid internal_ip and external_ip values are required'
        )

    try:
        result = client.create_nat_rule(network_domain['id'], internal_ip,
                                        external_ip)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not create the NAT rule - %s' % e,)
    except KeyError:
        module.fail_json(
            changed=False,
            msg='Network Domain is invalid'
        )

    msg = 'Successfully created the NAT rule'
    module.exit_json(changed=True, msg=msg, nat_rule_id=result)



def get_nat_rule(module, client, nat_rule_id):
    if nat_rule_id is None:
        module.fail_json(
            changed=False,
            msg='A value for id is required'
        )

    try:
        result = client.get_nat_rule(nat_rule_id)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get the NAT rule - %s' % e,
        )
    msg = 'Found the NAT rule'

    module.exit_json(changed=False, msg=msg, nat=result)


def delete_nat_rule(module, client, nat_rule_id):
    if nat_rule_id is None:
        module.fail_json(
            changed=False,
            msg='A value for id is required'
        )
    try:
        result = client.remove_nat_rule(nat_rule_id)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not delete the NAT rule - %s' % e,
        )
    msg = 'Successfully deleted the NAT rule'

    module.exit_json(changed=True, msg=msg)


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
            network_domain=dict(required=True, type='str'),
            internal_ip=dict(required=False, default=None, type='str'),
            external_ip=dict(required=False, default=None, type='str'),
            id=dict(default=None, type='str'),
            state=dict(default='list_nat_rule', choices=['list_nat_rule', 
                               'create_nat_rule','delete_nat_rule', 
                               'get_nat_rule']),
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
    object_id = module.params['id']
    internal_ip = module.params['internal_ip']
    external_ip = module.params['external_ip']

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

    if state == 'list_nat_rule':
        list_nat_rule(module, client, network_domain)
    elif state == 'create_nat_rule':
        create_nat_rule(module, client, network_domain, internal_ip, 
                        external_ip)
    elif state == 'get_nat_rule':
        get_nat_rule(module, client, object_id)
    elif state == 'delete_nat_rule':
        delete_nat_rule(module, client, object_id)

    
if __name__ == '__main__':
    main()