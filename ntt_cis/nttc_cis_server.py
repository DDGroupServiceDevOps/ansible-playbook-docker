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
# Get, Create, Update, Delete Servers

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nttc_cis_server
short_description: List, Create, Update, Delete Servers
description:
    - Get, Create, Delete Servers
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
        required: false
    vlan:
        description:
            - The name of the vlan in which the server is housed
            - Not used for create
        required: false
    name:
        description:
            - The name of the server
        required: true
    description:
        description:
            - The description of the VLAN
        required: false
    image_id:
        description:
            - The UUID of the Image to use whend creating a new server
            - Use nttc_cis_infrastructure -> state=get_image to get a list
            - of that available images
        required: false
    cpu:
        description:
            - CPU object with the following attributes
            - (speed)  STANADRD, HIGHPERFORMANCE
            - (coresPerSocket) int
        required: false
    memory_gb:
        description:
            - Integer value for the server memory size
        required: false
    network_info:
        description:
            - Network object with the following attributes
            - (primary_nic) (object)
            - (vlan) the name of the server's vlan OR
            - (privateIpv4) the IPv4 address to give the server
            - (additional_nic) (list of objects)
            - (vlan) the name of the server's vlan OR
            - (privateIpv4) the IPv4 address to give the server
        required: false
    primary_dns:
        description:
            - Primary DNS serverto assign to the server
        required: false
    secondary_dns:
        description:
            - Secondary DNS serverto assign to the server
        required: false
    ipv4_gw:
        description:
            - IPv4 default gateway
        required: false
    ipv6_gw:
        description:
            - IPv6 default gateway
        required: false
    disks:
        description:
            - List of disk objects containing
            - (id) UUID of the Image disk (use get_image)
            - (speed) STANDARD,HIGHPERFORMANCE,ECONOMY,PROVISIONEDIOPS
            - (iops) int
        required: false
    disk_id:
        description:
            - the disk UUID when expanding or modifying disks
        required: false
    disk_size:
        description:
            - The disk size when expanding a disk
        required: false
    admin_password:
        description:
            - The administrator/root password to assign to the new server
            - If left blank the module will generate and return one
        required: false
    start:
        description:
            - Whether to start the server after creation
        choices: [true, false]
        required: false
    server_state:
        description:
            - Various server states to check
        default: NORMAL
        required: false
    state:
        description:
            - The action to be performed
        required: true
        default: create
        choices: [create,delete,update,get,start,stop,expand_disk,reboot]
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
# Create a Server
- name: Create a server
  nttc_cis_server:
    region: na
    datacenter: NA9
    name: "APITEST"
    image_id: "44f27606-8787-45be-8ab5-a0a1b7fd009a"
    disks:
      - id: "xxxx"
        speed: "STD"
      - id: "zzzz"
        speed: "PIOPS"
        iops: 50
    cpu:
      speed: "STANDARD"
      count: 1
      coresPerSocket: 2
    network_info:
      network_domain: "xyz"
      primary_nic:
        vlan: "zyx"
      additional_nic:
        - networkAdapter: "VMXNET3"
          vlan: "abc"
          privateIpv4: "10.0.0.20"
  start: True
  state: create
# Update a Server
- name: Update a server
    nttc_cis_server:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "APITEST"
      memory_gb: 4
      cpu:
        count: 2
        coresPerSocket: 2
      wait: True
      state: update
# Delete a Server
- name: Delete a server
    nttc_cis_server:
      region: na
      datacenter: NA9
      name: "APITEST"
      wait: True
      state: delete
# Get a Server
- name: Get a server
    nttc_cis_server:
      region: na
      datacenter: NA9
      network_domain: "xxxx"
      name: "APITEST"
      state: get
# Send a server a Start/Stop/Reboot command
- name: Command a server
    nttc_cis_server:
      region: na
      datacenter: NA9
      network_domain: "APITEST"
      name: "yyyy"
      state: stop
      wait: True
'''

RETURN = '''
server:
    description: Dictionary of the server
    contains:
        id:
            description: server ID
            type: string
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        name:
            description: server name
            type: string
            sample: "My server"
        description:
            description: server description
            type: string
            sample: "My server description"
        datacenterId:
            description: Datacenter id/location
            type: string
            sample: NA9
        networkDomainId:
            description: The UUID of the home Cloud Network Domain of the VLAN
            type: string
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
'''

import json
from ansible.module_utils.basic import *
from ansible.module_utils.nttc_cis import *
from time import sleep
try:
    from ansible.module_utils.v2 import NTTCCISClient, NTTCCISAPIException
    from ansible.module_utils.config import (API_ENDPOINTS, SERVER_STATES, 
                                        DISK_SPEEDS, VARIABLE_IOPS)
    NTTCIS_IMPORTED = True
except:
    NTTCIS_IMPORTED = False


def get_nttc_cis_regions():
    regions = []
    for region in API_ENDPOINTS:
        regions.append(region)
    return regions


def create_server(module, client):
    params = {}
    search_params = {}
    disks = module.params['disks']
    network = module.params['network_info']
    datacenter = module.params['datacenter']
    ngoc = module.params['ngoc']

    if module.params['image_id'] is None:
        module.fail_json(changed=False, msg='A valid OS ID is required.')

    # Check disk configurations
    if disks is not None:
        if len(disks) > 0:
            params['disk'] = []
        for disk in disks:
            if 'id' in disk:
                if 'speed' not in disk:
                    module.fail_json(changed=False, msg='Disk speed is '
                                                        'required.')
                elif ('iops' in disk and disk['speed'] not in VARIABLE_IOPS):
                    module.fail_json(
                        changed=False,
                        msg=('Disk IOPS are required when disk_speed is: %s.' 
                            % (disk['speed']))
                    )
                params['disk'].append(disk)
            else:
                module.fail_json(changed=False, msg='Disks IDs are required.')
    
    # Check and load the network configuration for the server
    params['networkInfo'] = {}
    try:
        if 'primary_nic' in network:
            primary_nic = {}
            if 'network_domain' in network:
                params['networkInfo']['networkDomainId'] = (
                            client.get_network_domain_by_name(
                                name=network['network_domain'],
                                datacenter=module.params['datacenter']
                            )['id'])
            else:
                module.fail_json(changed=False, msg='A Cloud Network Domain '
                                                    ' is required.')
            if 'privateIpv4' in network['primary_nic']:
                primary_nic['privateIpv4'] = (
                                        network['primary_nic']['privateIpv4'])
            elif 'vlan' in network['primary_nic']:
                primary_nic['vlanId'] = client.get_vlan_by_name(
                    name=network['primary_nic']['vlan'],
                    datacenter=module.params['datacenter'],
                    network_domain_id=params['networkInfo']['networkDomainId']
                )['id']
            else:
                module.fail_json(changed=False, msg='An IPv4 address or VLAN '
                                                    ' is required.')
            params['networkInfo']['primaryNic'] = primary_nic
        else:
            module.fail_json(changed=False, msg='Primary NIC required.')
        
        if 'additional_nic' in network:
            additional_nic = []
            for nic in network['additional_nic']:
                new_nic = {}
                if 'networkAdapter' not in nic:
                    module.fail_json(changed=False, msg='NIC Adapter is '
                                                        'required')
                if 'privateIpv4' in nic:
                    new_nic['privateIpv4'] = nic['privateIpv4']
                elif 'vlan' in nic:
                    new_nic['vlanId'] = client.get_vlan_by_name(
                        name=network['nic']['vlan'],
                        datacenter=module.params['datacenter'],
                        network_domain_id=(
                            params['networkInfo']['networkDomainId'])
                    )['id']
                else:
                    module.fail_json(
                            changed=False, 
                            msg='An IPv4 address of VLAN is required for '
                            'additional NICs'
                        )
                additional_nic.append(new_nic)
            params['networkInfo']['additionalNic'] = additional_nic
    except NTTCCISAPIException as e:
        module.fail_json(changed=False, msg='%s' % e)

    network_domain_id = params['networkInfo']['networkDomainId']
    search_params['networkDomainId'] = network_domain_id

    params['imageId'] = module.params['image_id']
    params['name'] = module.params['name']
    params['start'] = module.params['start']
    if module.params['cpu'] is not None:
        params['cpu'] = module.params['cpu']
    if module.params['memory_gb'] is not None:
        params['memoryGb'] = module.params['memory_gb']
    if module.params['primary_dns'] is not None:
        params['primaryDns'] = module.params['primary_dns']
    if module.params['secondary_dns'] is not None:
        params['secondaryDns'] = module.params['secondary_dns']
    if module.params['ipv4_gw'] is not None:
        params['ipv4Gateway'] = module.params['ipv4_gw']
    if module.params['ipv6_gw'] is not None:
        params['ipv6Gateway'] = module.params['ipv6_gw']
    if not ngoc:
        if module.params['admin_password'] is not None:
            params['administratorPassword'] = module.params['admin_password']
        else:
            params['administratorPassword'] = generate_password()


    #module.exit_json(changed=False,msg='',data=params)

    try:
        client.create_server(ngoc, params)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not create the Server - %s' % e
        )

    if module.params['wait']:
        wait_for_server(module, client, params['name'], datacenter,  
                     search_params, 'NORMAL', module.params['start'])

    if ngoc:
        msg = 'Server %s has been successfully created ' % (params['name'])
    else:
        msg = ('Server %s has been successfully created with the password: %s' 
           % (params['name'], params['administratorPassword']))

    try:
        servers = client.list_servers(
                    datacenter=datacenter,
                    params=search_params
                )
    except NTTCCISAPIException as e:
        if ngoc:
            module.fail_json(msg='Failed to get a list of servers')
        else:
            module.fail_json(msg='Failed to get a list of servers - %s.'
                             ' Admin password is: %s' % (
                             e, params['administratorPassword']))

    server_exists = filter(lambda x: x['name'] == params['name'], servers)
    if server_exists:
        server = server_exists[0]
    else:
        server = []
    module.exit_json(changed=True, msg=msg, server=server)


def update_server(module, client, server):
    params = {}
    search_params = {}
    cpu = {}
    network_domain_id = server['networkInfo']['networkDomainId']
    datacenter = server['datacenterId']
    name = server['name']
    params['id'] = server['id']
    search_params['networkDomainId'] = network_domain_id

    if module.params['cpu'] is not None:
        cpu = module.params['cpu']
        if 'count' in cpu:
            params['cpuCount'] = cpu['count']
        if 'coresPerSocket' in cpu:
            params['coresPerSocket'] = cpu['coresPerSocket']
        if 'speed' in cpu:
            params['cpuSpeed'] = cpu['speed']
    if module.params['memory_gb'] is not None:
        params['memoryGb'] = module.params['memory_gb']

    try:
        result = client.reconfigure_server(params=params)
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not update the server - %s' % e
        )

    if module.params['wait']:
        wait_for_server(module, client, name, datacenter,  
                     search_params, 'NORMAL', False, False)

    msg = 'Server has been successfully been updated'

    try:
        servers = client.list_servers(
                    datacenter=datacenter,
                    params=search_params
                )
    except NTTCCISAPIException as e:
        module.fail_json(msg='Failed to get a list of servers - %s' % e)

    server_exists = filter(lambda x: x['name'] == name, servers)
    if server_exists:
        server = server_exists[0]
    else:
        server = []
    module.exit_json(changed=True, msg=msg, server=server)



def expand_disk(module, client, server):
    disk_id = module.params['disk_id']
    disk_size = module.params['disk_size']
    if disk_id is None:
        module.fail_json(changed=False, msg='No disk id provided.')
    if disk_size is None:
        module.fail_json(
            changed=False,
            msg='No size provided. A value larger than 10 is required for '
                'disk_size.'
        )
    name = server['name']
    server_id = server['id']
    network_domain_id = server['networkInfo']['networkDomainId']
    datacenter = server['datacenterId']
    search_params = {}
    search_params['networkDomainId'] = network_domain_id

    try:
        client.expand_disk(
                           server_id=server_id,
                           disk_id=disk_id,
                           disk_size=disk_size
                          )
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not expand the disk - %s' % e
        )

    if module.params['wait']:
        wait_for_server(module, client, name, datacenter,  
                     search_params, 'NORMAL', False, False,
                     wait_poll_interval)

    msg = 'Server disk has been successfully been expanded to %sGB' % (
           disk_size)

    try:
        servers = client.list_servers(
                    datacenter=datacenter,
                    params=search_params
                )
    except NTTCCISAPIException as e:
        module.fail_json(msg='Failed to get a list of servers - %s.' % e)

    server_exists = filter(lambda x: x['name'] == name, servers)
    if server_exists:
        server = server_exists[0]
    else:
        server = []
    module.exit_json(changed=True, msg=msg, server=server)


def server_command(module, client, server):
    name = server['name']
    datacenter = server['datacenterId']
    network_domain_id = server['networkInfo']['networkDomainId']
    search_params = {}
    search_params['networkDomainId'] = network_domain_id
    # Set a default timer unless a lower one has been provided
    if module.params['wait_poll_interval'] < 15:
        wait_poll_interval = module.params['wait_poll_interval']
    else:
        wait_poll_interval = 15

    try:
        if module.params['state'] == "start":
            start_result = client.start_server(server_id=server['id'])
            wait_for_server(module, client, name, datacenter, search_params, 
                            'NORMAL', True, False, wait_poll_interval)
        elif module.params['state'] == "reboot":
            start_result = client.reboot_server(server_id=server['id'])
            wait_for_server(module, client, name, datacenter, search_params, 
                            'NORMAL', True, False, wait_poll_interval)
        elif module.params['state'] == "stop":
            shutdown_result = client.shutdown_server(server_id=server['id'])
            wait_for_server(module, client, name, datacenter, search_params, 
                            'NORMAL', False, True, wait_poll_interval)
        msg = 'Command %s successfully completed on server %s' % (
                                                module.params['state'],
                                                name)
    except NTTCCISAPIException as e:
        module.fail_json(
                changed=False,
                msg='Could not %s the server - %s' % (module.params['state'],
                                                      e)
            )
    module.exit_json(changed=True, msg=msg)


def delete_server(module, client, server):
    server_result = True
    search_params = {}
    name = server['name']
    datacenter = server['datacenterId']
    network_domain_id = server['networkInfo']['networkDomainId']
    search_params['networkDomainId'] = network_domain_id
    # Set a default timer unless a lower one has been provided
    if module.params['wait_poll_interval'] < 30:
        wait_poll_interval = module.params['wait_poll_interval']
    else:
        wait_poll_interval = 30

    # Check if the server is running and shut it down
    if server['started']:
        try:
            shutdown_result = client.shutdown_server(server_id=server['id'])
            wait_for_server(module, client, name, datacenter, search_params, 
                     'NORMAL', False, True, wait_poll_interval)
        except NTTCCISAPIException:
            module.fail_json(
                    changed=False,
                    msg='Could not shutdown the server - %s' % e,
                )
    try:
        result = client.delete_server(server['id'])
    except NTTCCISAPIException as e:
        module.fail_json(
            changed=False,
            msg='Could not delete the server - %s' % e,
        )
    if module.params['wait']:
        while server_result:
            servers = client.list_servers(
                    datacenter=datacenter,
                    params=search_params
                )
            server_result = filter(lambda x: x['id'] == 
                                           server['id'], servers)
            sleep(wait_poll_interval)
    msg = 'Server %s has been successfully removed in %s' % (
           server['name'], server['datacenterId'])    
    module.exit_json(changed=True, msg=msg)


def wait_for_server(module, client, name, datacenter, params, state, 
                    check_for_start=False, check_for_stop=False,
                    wait_poll_interval=None):
    set_state = False
    actual_state = ''
    start_state = ''
    if wait_poll_interval is None:
        wait_poll_interval = module.params['wait_poll_interval']
    server = {}
    while not set_state:
        try:
            servers = client.list_servers(datacenter=datacenter, 
                                          params=params)
        except NTTCCISAPIException as e:
            module.fail_json(msg='Error: Failed to get a list of Server - %s' 
                             % e)
        server = filter(lambda x: x['name'] == name, servers)
        if len(server) > 0:
            actual_state = server[0]['state']
            start_state = server[0]['started']
        else:
            module.fail_json(msg='Error: Failed to find the Server - %s' 
                             % name)
        if actual_state != state or (check_for_start and not start_state):
            sleep(wait_poll_interval)
        if actual_state != state or (check_for_stop and start_state):
            sleep(wait_poll_interval)
        else:
            set_state = True


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(default=None, required=False, type='str'),
            vlan=dict(default=None, required=False, type='str'),
            name=dict(required=True, type='str'),
            description=dict(required=False, type='str'),
            image_id=dict(required=False, type='str'),
            cpu=dict(required=False, type='dict'),
            memory_gb=dict(required=False, type='int'),
            network_info=dict(required=False, type='dict'),
            primary_dns=dict(required=False, type='str'),
            secondary_dns=dict(required=False, type='str'),
            ipv4_gw=dict(required=False, type='str'),
            ipv6_gw=dict(required=False, type='str'),
            disks=dict(required=False, type='list'),
            disk_id=dict(required=False, type='str'),
            disk_size=dict(required=False, type='int'),
            admin_password=dict(required=False, type='str'),
            ngoc=dict(required=False, default=False, type='bool'),
            start=dict(default=True, type='bool'),
            server_state=dict(default='NORMAL', choices=SERVER_STATES),
            started=dict(required=False, default=True, type='bool'),
            new_name=dict(required=False, default=None, type='str'),
            state=dict(default='create', choices=['create', 'delete','get', 
                       'update', 'start', 'stop', 'reboot',
                       'expand_disk']),
            wait=dict(required=False, default=False, type='bool'),
            wait_time=dict(required=False, default=1200, type='int'),
            wait_poll_interval=dict(required=False, default=60, type='int'),
            verify_ssl_cert=dict(required=False, default=True, type='bool')
        )
    )
    
    credentials = get_credentials()
    name = module.params['name']
    datacenter = module.params['datacenter']
    state = module.params['state']
    network_domain_name = module.params['network_domain']
    vlan_name =  module.params['vlan']
    params = {}

    if credentials is False:
        module.fail_json(msg='Could not load the user credentials')

    client = NTTCCISClient((credentials[0],credentials[1]),
                          module.params['region'])

    # Get the CND object based on the supplied name
    if network_domain_name is not None:
        network_domain = client.get_network_domain_by_name(
                                                    name=network_domain_name,
                                                    datacenter=datacenter
                                                )
        params['networkDomainId'] = network_domain['id']

    # Get the VLAN object based on the supplied name
    if vlan_name is not None:
        vlan = client.get_vlan_by_name(
                                        name=vlan_name,
                                        datacenter=datacenter,
                                        network_domain_id=network_domain['id']
                                      )
        params['vlanId'] = vlan['id']

    # Check if the Server exists based on the supplied name
    try:
        servers = client.list_servers(
                    datacenter=datacenter,
                    params=params
                )
    except NTTCCISAPIException as e:
        module.fail_json(msg='Failed to get a list of servers - %s' % e)

    server_exists = filter(lambda x: x['name'] == name, servers)

    # Get the Server
    if state == 'get':
        if server_exists:
            module.exit_json(
                changed=False,
                msg='Server exists',
                server=server_exists[0]
            )
        else:
            module.fail_json(
                changed=False,
                msg='Server not found',
                server=None
            )
    # Create the Server
    elif state == 'create':
        # Handle case where Server name already exists
        if server_exists:
            module.exit_json(
                changed=False,
                msg='Server already exists',
                server=server_exists[0]
            )
        create_server(module, client)
    # Update a Server
    elif state == 'update':
        if not server_exists:
            module.exit_json(
                changed=False,
                msg='Server not found',
            )
        elif server_exists[0]['started']:
            module.fail_json(
                changed=False,
                msg='Server cannot be updated while the it is running',
            )
        update_server(module, client, server_exists[0])
    # Delete the Server
    elif state == 'delete':
        if not server_exists:
            module.exit_json(
                changed=False,
                msg='Server not found',
            )
        delete_server(module, client, server_exists[0])
    # Expand the disk on a Server
    elif state == 'expand_disk':
        if not server_exists:
            module.fail_json(
                changed=False,
                msg='Server not found',
            )
        elif server_exists[0]['started']:
            module.fail_json(
                changed=False,
                msg='Disk cannot be expanded while the server is running',
            )
        expand_disk(module, client, server_exists[0])
    # Start a Server
    elif state == 'start':
        if not server_exists:
            module.fail_json(
                changed=False,
                msg='Server not found',
            )
        elif server_exists[0]['started']:
            module.exit_json(
                changed=False,
                msg='Server is already running',
            )
        server_command(module, client, server_exists[0])
    # Stop a Server
    elif state == 'stop':
        if not server_exists:
            module.fail_json(
                changed=False,
                msg='Server not found',
            )
        elif not server_exists[0]['started']:
            module.exit_json(
                changed=False,
                msg='Server is already stopped',
            )
        server_command(module, client, server_exists[0])
    # Reboot a Server
    elif state == 'reboot':
        if not server_exists:
            module.fail_json(
                changed=False,
                msg='Server not found',
            )
        server_command(module, client, server_exists[0])

    
if __name__ == '__main__':
    main()