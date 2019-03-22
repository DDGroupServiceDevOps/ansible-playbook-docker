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
# Get NTTC CIS Cloud Information

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_information
short_description: Get NTTC CIS Cloud Information
description:
    - Get NTTC CIS Cloud Information
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
        required: false
        choices:
          - See NTTC CIS Cloud Web UI
    id:
        description:
            - The id of the infrastructure entity
        required: false
    name:
        description:
            - The name of the infrastructure entity
        required: false
    family:
        description:
            - The family name of the infrastructure entity
        required: false
    id_like:
        description:
            - Boolean for when using wildcards with id
        required: false
        choices:
            - True or False
    name_like:
        description:
            - Boolean for when using wildcards with name
        required: false
        choices:
            - True or False
    state:
        description:
            - The action to be performed
        required: true
        default: get_geo
        choices: [get_geo, get_dc, get_os]
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
# GET Geographic Regions
- name: Get a list of GEOs
    nttc_cis_infrastructure:
      region: na
      name: "North America"
      state: get_geo
# Get Datacenters
- name: Get a list of DCs
    nttc_cis_infrastructure:
      region: na
      state: get_dc
# Get Operating Systems
- name: Get a list of DCs
    nttc_cis_infrastructure:
      region: na
      state: get_os
      name: "UBUNTU*"
      name_like: True
'''

RETURN = '''
object:
    description: Dictionary of the object
    contains:
        id:
            description: Object ID
            type: string
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
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


def get_geo(module, client, geo_id=None, geo_name=None):
    params = {}
    if geo_id is None and geo_name is None:
        module.fail_json(
            changed=False,
            msg='An id or name is required'
            )
    if geo_id is not None:
        params['id'] = geo_id
    if geo_name is not None:
        params['name'] = geo_name

    try:
        result = client.get_geo(params)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get a list of Geos - %s' % e
        )

    if 'geographicRegion' not in result:
        msg = 'No Geos found'
    else:
        if len(result['geographicRegion']) > 0:
            msg = 'Geo found'
        else:
            msg = 'No Geos found'

    module.exit_json(changed=False, msg=msg, data=result)


def get_dc(module, client, dc_id=None):
    params = {}
    if dc_id is not None:
        params['id'] = dc_id
    try:
        result = client.get_dc(params=params)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get a list of DCs - %s' % e
        )

    if 'datacenter' not in result:
        msg = 'No DCs found'
    else:
        if len(result['datacenter']) > 0:
            msg = 'DC found'
        else:
            msg = 'No DCs found'

    module.exit_json(changed=False, msg=msg, data=result)


def get_os(module, client, os_id=None, os_name=None, os_family=None,
           id_like=False, name_like=False):
    params = {}
    if os_id is not None:
        if id_like:
            params['id.LIKE'] = os_id
        else:
            params['id'] = os_id
    if os_name is not None:
        if name_like:
            params['name.LIKE'] = os_name
        else:
            params['name'] = os_name
    if os_family is not None:
        params['family'] = os_family

    try:
        result = client.get_os(params=params)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get a list of operating systems - %s' % e
        )

    if 'operatingSystem' not in result:
        msg = 'No OS found'
    else:
        if len(result['operatingSystem']) > 0:
            msg = 'OS found'
        else:
            msg = 'No OS found'

    module.exit_json(changed=False, msg=msg, data=result)

def get_image(module, client, image_id=None, image_name=None, 
              os_family=None, id_like=False, name_like=False, 
              customer_image=False):
    params = {}
    if image_id is not None:
        if id_like:
            params['id.LIKE'] = image_id
        else:
            params['id'] = image_id
    if image_name is not None:
        if name_like:
            params['name.LIKE'] = image_name
        else:
            params['name'] = image_name
    if os_family is not None:
        params['operatingSystemFamily'] = os_family

    try:
        result = client.get_image(params=params)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get a list of operating systems - %s' % e
        )

    if 'osImage' not in result:
        msg = 'No Images found'
    else:
        if len(result['osImage']) > 0:
            msg = 'Image found'
        else:
            msg = 'No Images found'

    module.exit_json(changed=False, msg=msg, data=result)


def get_customer_image(module, client):
    image_name = module.params['name']
    image_name_like = module.params['name_like']
    image_id = module.params['id']
    image_id_like = module.params['id_like']
    ovf_package = module.params['ovf_package']
    datacenter = module.params['datacenter']
    os_family = module.params['family']

    params = {}
    msg =''
    if image_id is not None:
        if image_id_like:
            params['id.LIKE'] = image_id
        else:
            params['id'] = image_id
    if image_name is not None:
        if image_name_like:
            params['name.LIKE'] = image_name
        else:
            params['name'] = image_name
    if os_family is not None:
        params['operatingSystemFamily'] = os_family

    try:
        result = client.list_customer_image(params=params)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not get a list of customer images  - %s' % e
        )

    if 'customerImage' not in result:
        msg = 'No Images found'
    else:
        if len(result['customerImage']) > 0:
            msg = 'Image found'
        else:
            msg = 'No Images found'

    module.exit_json(changed=False, msg=msg, data=result)

def import_image(module, client):
    image_name = module.params['name']
    description = module.params['description']
    ovf_package = module.params['ovf_package']
    datacenter = module.params['datacenter']
    ngoc = module.params['ngoc']

    wait = module.params['wait']
    image_id = ''
    image = None

    if image_name is None or ovf_package is None or datacenter is None:
        module.fail_json(
            changed=False,
            msg='An image name, OVF Package name and datacenter are required.'
        )

    try:
        result = client.import_customer_image(datacenter, ovf_package, 
                                     image_name, description, ngoc)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not import the OVF package - %s' % e
        )

    try:
        image_id = result['info'][0]['value']
    except (KeyError, IndexError) as e:
        module.fail_json(
            changed=False,
            msg='Could not import the OVF package - %s' % result
        )

    if wait:
        image = wait_for_image_import(module, client, image_id, 'NORMAL')
        if image is None:
            module.fail_json(
                changed=False,
                msg='Could not verify the image import was successfuly'
            )
    else:
        image = result['info'][0]
    
    msg = 'Image %s has been successfully imported in %s' % (image_name, 
          datacenter)

    module.exit_json(changed=True, msg=msg, data=image)


def wait_for_image_import(module, client, image_id, state):
    actual_state = ''
    image = None
    wait_time = module.params['wait_time']
    time = 0
    while actual_state != state and time < wait_time:
        try:
            image = client.get_customer_image(image_id=image_id)
        except NTTCCISAPIException as e:
            module.fail_json(msg='Error: Failed to get the image - %s' % e)
        try:
            actual_state = image['state']
        except (KeyError, IndexError) as e:
            pass
        sleep(module.params['wait_poll_interval'])
        time = time + module.params['wait_poll_interval']
    return image


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=False, type='str'),
            id=dict(required=False, type='str'),
            name=dict(required=False, type='str'),
            description=dict(required=False, type='str'),
            family=dict(required=False, type='str'),
            id_like=dict(required=False, default=False, type='bool'),
            name_like=dict(required=False, default=False, type='bool'),
            customer_image=dict(required=False, default=False, type='bool'),
            ovf_package=dict(required=False, type='str'),
            ngoc=dict(required=False, default=True, type='bool'),
            state=dict(default='get_geo', choices=['get_geo', 'get_dc',
                       'get_os', 'get_image', 'import_image']),
            wait=dict(required=False, default=False, type='bool'),
            wait_time=dict(required=False, default=600, type='int'),
            wait_poll_interval=dict(required=False, default=10, type='int'),
            verify_ssl_cert=dict(required=False, default=True, type='bool')
        )
    )

    
    credentials = get_credentials()
    name = module.params['name']
    region = module.params['region']
    datacenter = module.params['datacenter']
    state = module.params['state']
    infra_id = module.params['id']
    infra_name = module.params['name']
    infra_family = module.params['family']
    id_like = module.params['id_like']
    name_like = module.params['name_like']
    customer_image = module.params['customer_image']
    ovf_package = module.params['ovf_package']
    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    client = NTTCCISClient((credentials[0],credentials[1]),
                          module.params['region'])


    if state == 'get_geo':
        get_geo(module=module, client=client, geo_id=infra_id, 
                geo_name=infra_name)
    elif state == 'get_dc':
        # Handle case where Server name already exists
        get_dc(module=module, client=client, dc_id=infra_id)
    elif state == 'get_os':
        get_os(module=module, client=client, os_id=infra_id, 
               os_name=infra_name, os_family=infra_family,
               id_like=id_like, name_like=name_like)
    elif state == 'get_image' and not customer_image:
        get_image(module=module, client=client, image_id=infra_id, 
               image_name=infra_name, os_family=infra_family,
               id_like=id_like, name_like=name_like,
               customer_image=customer_image)
    elif state == 'get_image' and customer_image:
        get_customer_image(module=module, client=client)
    elif state == 'import_image':
        import_image(module=module, client=client)

    
if __name__ == '__main__':
    main()