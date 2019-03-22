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
#   - Ken Sinfield <ken.sinfield@cis.ntt.com>
#
# NTTC CIS Cloud API Provider (MCP 2.0)

import requests as REQ
import sys
from config import (HTTP_HEADERS, API_VERSION, API_ENDPOINTS, 
                                  DEFAULT_REGION)

class NTTCCISAPIException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "<NTTCCISAPIException: msg='%s'>" % (self.msg)

    def __repr__(self):
        return "<NTTCCISAPIException: msg='%s'>" % (self.msg)


class NTTCCISClient():
    def __init__(self, credentials, region):
        self.credentials = credentials
        self.region = region
        self.home_geo = self.get_user_home_geo()
        self.org_id = self.get_org_id()
        self.base_url = ('https://%s/caas/%s/%s/' % 
                         (API_ENDPOINTS[region]['host'], API_VERSION, 
                         self.org_id))

    def __repr__(self):
        return ('Username: %s\nHome Geo: %s\nOrg Id: %s\nSupplied Region: %s'
                '\nBase URL: %s' % (self.credentials[0], self.home_geo, 
                self.org_id, self.region, self.base_url))

    def get_user_home_geo(self):
        url = ('https://%s/caas/%s/user/myUser' % 
               (API_ENDPOINTS[DEFAULT_REGION]['host'], API_VERSION))
        response = self.api_get_call(url, None)
        if response != None:
            return response.json()['organization']['homeGeoApiHost']
        else:
            raise NTTCCISAPIException('Could not determine the Home Geo for'
                                     'user: %s') % (self.credentials[0])

    def get_org_id(self):
        url = ('https://%s/caas/%s/user/myUser' % 
              (API_ENDPOINTS[DEFAULT_REGION]['host'], API_VERSION))
        response = self.api_get_call(url, None)
        if response != None:
            return response.json()['organization']['id']
        else:
            raise NTTCCISAPIException('Could not determine the Org Id for'
                                     'user: %s') % (self.credentials[0])


    '''
    NETWORK FUNCTIONS
    '''
    def list_network_domains(self, network_domain_id=None, datacenter=None, 
                             name=None, network_type=None, state=None):  
        params = {} 
        if network_domain_id is not None:
            params['id'] = network_domain_id
        if datacenter is not None:
            params['datacenterId'] = datacenter
        if name is not None:
            params['name'] = name
        if network_type is not None:
            params['type'] = network_type
        if state is not None:
            params['state'] = state

        url = self.base_url + 'network/networkDomain'

        response = self.api_get_call(url, params)
        if response != None:
            if response.json()['totalCount'] > 0:
                return response.json()['networkDomain']
            else:
                raise NTTCCISAPIException('No Network Domain found with '
                                         'the parameters %s' % (
                                          str(params)))
        else:
            raise NTTCCISAPIException('Could not get a list of '
                                     'network domains')

    def get_network_domain_by_name(self, name=None, datacenter=None):
        if name is None:
            raise NTTCCISAPIException('A Cloud Network Domain is required.')
        if datacenter is None:
            raise NTTCCISAPIException('A Datacenter is required.')

        try:
            networks = self.list_network_domains(datacenter=datacenter)
        except Exception as e:
            raise NTTCCISAPIException('Failed to get a list of Cloud Network '
                             'Domains - %s' % e)
        network_exists = filter(lambda x: x['name'] == name, networks)
        if not network_exists:
            raise NTTCCISAPIException('Failed to find the Cloud Network '
                                      'Domain.')
        else:
            return network_exists[0]


    def create_network_domain(self, datacenter=None, name=None, 
                              network_type=None, description=None):
        params = {}
        if datacenter is not None:
            params['datacenterId'] = datacenter
        if name is not None:
            params['name'] = name
        if network_type is not None:
            params['type'] = network_type
        if description is not None:
            params['description'] = description

        url = self.base_url + 'network/deployNetworkDomain'

        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the create '
                                         'Cloud Network Domain request was '
                                         'accepted')
        else:
            raise NTTCCISAPIException('No response from the API')


    def update_network_domain(self, params, network_domain_id=None):
        if network_domain_id is not None:
            params['id'] = network_domain_id

        url = self.base_url + 'network/editNetworkDomain'

        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the update '
                                         'Cloud Network Domain request was '
                                         'accepted')
        else:
            raise NTTCCISAPIException('No response from the API')


    def delete_network_domain(self, network_domain_id=None):
        params = {}
        if network_domain_id is not None:
            params['id'] = network_domain_id
        else:
            raise NTTCCISAPIException('No Cloud Network Domain ID supplied')

        url = self.base_url + 'network/deleteNetworkDomain'

        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the delete '
                                         'Cloud Network Domain request was '
                                         'accepted')
        else:
            raise NTTCCISAPIException('No response from the API')


    def list_vlans(self, datacenter=None, network_domain_id=None, name=None,
                   ipv4_network_address=None, ipv6_network_address=None, 
                   state=None, attached=None):
        params = {}
        if datacenter is not None:
            params['datacenterId'] = datacenter
        if network_domain_id is not None:
            params['networkDomainId'] = network_domain_id
        if name is not None:
            params['name'] = name
        if ipv4_network_address is not None:
            params['privateIpv4Address'] = ipv4_network_address
        if ipv6_network_address is not None:
            params['ipv6Address'] = ipv6_network_address
        if state is not None:
            params['state'] = state
        if attached is not None:
            params['attached'] = attached

        url = self.base_url + 'network/vlan'
        response = self.api_get_call(url, params)
        if response != None:
            if 'vlan' in response.json():
                return response.json()['vlan']
            else:
                return []
        else:
            raise NTTCCISAPIException('Could not get a list of VLANs')


    def get_vlan_by_name(
                     self, 
                     name=None, 
                     datacenter=None, 
                     network_domain_id=None
                    ):
        if name is None:
            raise NTTCCISAPIException('A VLAN is required.')
        try:
            vlans = self.list_vlans(
                        datacenter=datacenter,
                        network_domain_id=network_domain_id
                    )
        except Exception as e:
            raise NTTCCISAPIException('Failed to get a list of VLANs - %s' 
                                      % e)

        vlan_exists = filter(lambda x: x['name'] == name, vlans)
        if not vlan_exists:
            raise NTTCCISAPIException('Failed to find the VLAN. Check the '
                                      'vlan value')
        else:
            return vlan_exists[0]


    def create_vlan(
                    self, 
                    networkDomainId=None, 
                    name=None,
                    description=None, 
                    privateIpv4NetworkAddress=None, 
                    privateIpv4PrefixSize=None,
                    attachedVlan=False, 
                    detachedVlan=False,
                    attachedVlan_gatewayAddressing=None,
                    detachedVlan_ipv4GatewayAddress=None
                    ):
        params = {}
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description
        if networkDomainId is not None:
            params['networkDomainId'] = networkDomainId
        if privateIpv4NetworkAddress is not None:
            params['privateIpv4NetworkAddress'] = privateIpv4NetworkAddress
        if privateIpv4PrefixSize is not None:
            params['privateIpv4PrefixSize'] = privateIpv4PrefixSize
        if attachedVlan:
            params['attachedVlan'] = {}
            params['attachedVlan']['gatewayAddressing'] = (
                attachedVlan_gatewayAddressing)
        elif detachedVlan:
            params['detachedVlan'] = {}
            params['detachedVlan']['ipv4GatewayAddress'] = (
                detachedVlan_ipv4GatewayAddress)

        url = self.base_url + 'network/deployVlan'

        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the create '
                                         'VLAN request was accepted')
        else:
            raise NTTCCISAPIException('No response from the API')

    def update_vlan(self, params=None, vlan_id=None):
        if vlan_id is not None:
            params['id'] = vlan_id

        url = self.base_url + 'network/editVlan'

        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the update '
                                         'VLAN request was accepted')
        else:
            raise NTTCCISAPIException('No response from the API')

    def delete_vlan(self, vlan_id=None):
        params = {}
        if vlan_id is not None:
            params['id'] = vlan_id
        else:
            raise NTTCCISAPIException('No VLAN ID supplied')

        url = self.base_url + 'network/deleteVlan'

        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the delete '
                                         'VLAN request was accepted')
        else:
            raise NTTCCISAPIException('No response from the API')


    def list_servers(self, datacenter=None, params=None):
        url = self.base_url + 'server/server'
        response = self.api_get_call(url, params)
        if response != None:
            if 'server' in response.json():
                return response.json()['server']
            else:
                return []
        else:
            raise NTTCCISAPIException('Could not get a list of servers')


    def create_server(self, ngoc, params):
        if ngoc:
            url = self.base_url + 'server/deployUncustomizedServer'
        else:
            url = self.base_url + 'server/deployServer'
        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the create '
                                         'server request was accepted')
        else:
            raise NTTCCISAPIException('No response from the API')


    def reconfigure_server(self, params):
        url = self.base_url + 'server/reconfigureServer'
        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the update '
                                         'server request was accepted')
        else:
            raise NTTCCISAPIException('No response from the API')


    def delete_server(self, server_id=None):
        params = {}
        if server_id is not None:
            params['id'] = server_id
        else:
            raise NTTCCISAPIException('No server ID supplied')

        url = self.base_url + 'server/deleteServer'

        response = self.api_post_call(url, params)
        if response != None:
            if response.json()['requestId'] != None:
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the delete '
                                          'Server request was accepted')
        else:
            raise NTTCCISAPIException('No response from the API')


    def shutdown_server(self, server_id=None):
        params = {}
        if server_id is not None:
            params['id'] = server_id
        else:
            raise NTTCCISAPIException('No server ID supplied')

        url = self.base_url + 'server/shutdownServer'
        response = self.api_post_call(url, params)
        if response != None:
            if 'requestId' in response.json():
                return response.json()
            elif 'responseCode' in response.json():
                if response.json()['responseCode'] == 'SERVER_STOPPED':
                    return {}
                else:
                    raise NTTCCISAPIException('Could not confirm that the '
                                         'shutdown server request was '
                                         'accepted')
            else:
                raise NTTCCISAPIException('Could not confirm that the '
                                         'shutdown server request was '
                                         'accepted')
        else:
            raise NTTCCISAPIException('No response from the API')

    def start_server(self, server_id=None):
        params = {}
        if server_id is not None:
            params['id'] = server_id
        else:
            raise NTTCCISAPIException('No server ID supplied')

        url = self.base_url + 'server/startServer'
        response = self.api_post_call(url, params)
        if response != None:
            if 'requestId' in response.json():
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the '
                                         'start server request was '
                                         'accepted')
        else:
            raise NTTCCISAPIException('No response from the API')

    def reboot_server(self, server_id=None):
        params = {}
        if server_id is not None:
            params['id'] = server_id
        else:
            raise NTTCCISAPIException('No server ID supplied')

        url = self.base_url + 'server/rebootServer'
        response = self.api_post_call(url, params)
        if response != None:
            if 'requestId' in response.json():
                return response.json()
            else:
                raise NTTCCISAPIException('Could not confirm that the '
                                         'reboot server request was '
                                         'accepted')
        else:
            raise NTTCCISAPIException('No response from the API')

    def expand_disk(self, server_id=None, disk_id=None, disk_size=None):
        params = {}
        if server_id is not None:
            params['id'] = server_id
        else:
            raise NTTCCISAPIException('No server ID supplied')
        if disk_id is not None:
            params['id'] = disk_id
        else:
            raise NTTCCISAPIException('No disk ID supplied')
        if disk_size is not None:
            params['newSizeGb'] = disk_size
        else:
            raise NTTCCISAPIException('No disk size supplied')

        url = self.base_url + 'server/expandDisk'

        response = self.api_post_call(url, params)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')


    def get_geo(self, params):
        if 'id' in params:
            if params['id'] is None:
                raise NTTCCISAPIException('An id or name is required')
        if 'name' in params:
            if params['name'] is None:
                raise NTTCCISAPIException('An id or name is required')

        url = ('https://%s/caas/%s/%s/infrastructure/geographicRegion' % 
               (self.home_geo, API_VERSION, self.org_id))

        response = self.api_get_call(url, params)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')


    def get_dc(self, params):
        url = self.base_url + 'infrastructure/datacenter'

        response = self.api_get_call(url, params)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')

    def get_os(self, params):
        url = self.base_url + 'infrastructure/operatingSystem'

        response = self.api_get_call(url, params)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')

    def get_image(self, params):
        url = self.base_url + 'image/osImage'

        response = self.api_get_call(url, params)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')


    # Args:
    #   image_id: The ID of the image
    # Return: the customer image object
    def get_customer_image(self, image_id):
        url = self.base_url + 'image/customerImage/%s' % image_id

        response = self.api_get_call(url)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')


    # Args:
    #   params: The search parameters - Check Cloud Control API doco
    # Return: the customer image object(s)
    def list_customer_image(self, params):
        url = self.base_url + 'image/customerImage'

        response = self.api_get_call(url, params)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')


    # Args:
    #   datacenter: The datacenter ID e.g. NA9
    #   ovf_package: The filename of the OVF manifest file on the FTPS server
    #   image_name: The name to be assigned to the imported image
    #   description: The image description in Cloud Control
    #   ngoc: Boolean to enable/disable Guest OS Customization
    # Return: the customer image object
    def import_customer_image(self, datacenter_id, ovf_package, image_name,
                              description, ngoc):
        url = self.base_url + 'image/importImage'
        params = {}

        if datacenter_id is None:
            raise NTTCCISAPIException('datacenter_id cannot be None')
        else:
            params['datacenterId'] = datacenter_id
        if ovf_package is None:
            raise NTTCCISAPIException('ovf_package cannot be None')
        else:
            params['ovfPackage'] = ovf_package
        if image_name is None:
            raise NTTCCISAPIException('image_name cannot be None')
        else:
            params['name'] = image_name
        if description is not None:
            params['description'] = description
        if ngoc is None:
            raise NTTCCISAPIException('ngoc cannot be None')
        else:
            params['guestOsCustomization'] = ngoc

        response = self.api_post_call(url, params)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')


    # Args: 
    #   network_domain_id: Cloud Network Domain UUID
    # Return: Array of UUIDs of found public IPv4 block or empty array
    def list_public_ipv4(self, network_domain_id):
        url = self.base_url + 'network/publicIpBlock'

        params = {'networkDomainId': network_domain_id}
        response = self.api_get_call(url, params)
        try:
            return response.json()['publicIpBlock']
        except KeyError:
            return []

    # Args: 
    #   public_ipv4_block_id: Public IPv4 block UUID
    # Return: UUID of the public IPv4 block
    def get_public_ipv4(self, public_ipv4_block_id):
        url = self.base_url + 'network/publicIpBlock/%s' % (
              public_ipv4_block_id)

        response = self.api_get_call(url)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')

    # Args: 
    #   network_domain_id: Cloud Network Domain UUID
    # Return: UUID of the new public IPv4 block
    def add_public_ipv4(self, network_domain_id):
        params = {'networkDomainId': network_domain_id}

        url = self.base_url + 'network/addPublicIpBlock'
        response = self.api_post_call(url, params)
        try:
            return response.json()['info'][0]['value']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the '
                                         'add public ipv4 block request was '
                                         'accepted')

    # Args: 
    #   public_ipv4_block_id: Public IPv4 block UUID
    # Return: string (API message)
    def remove_public_ipv4(self, public_ipv4_block_id):
        params = {'id': public_ipv4_block_id}

        url = self.base_url + 'network/removePublicIpBlock'
        response = self.api_post_call(url, params)
        try:
            if response.json()['responseCode'] == "OK":
                return response.json()['message']
            else:
                return response.json()['error']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the '
                                         'remove public ipv4 block request '
                                         'was accepted')

    # Args: 
    #   vlan_id: VLAN UUID
    #   datacenter_id: datacenter ID (e.g. NA9)
    #   version: IP version (deafult = 4)
    # Return: Array of private IPv4 reservations or empty array
    def list_reserved_ip(self, vlan_id=None, datacenter_id=None, version=4):
        params = {}
        if vlan_id is None and datacenter_id is None:
            raise NTTCCISAPIException('A vlan or datacenter must be provided')
        if version != 4 and version != 6:
            raise NTTCCISAPIException('Invalid IP version - %d' % version)
        # Prefer VLAN ID over datacenter ID
        if vlan_id is not None:
            params['vlanId'] = vlan_id
        elif datacenter_id is not None:
            params['datacenterId'] = datacenter_id

        url = self.base_url + 'network/reservedPrivateIpv4Address'
        if version == 6:
            url = self.base_url + 'network/reservedIpv6Address'

        response = self.api_get_call(url, params)
        try:
                return response.json()['ipv%d' % version]
        except KeyError:
            return []

    # Args: 
    #   vlan_id: VLAN UUID
    #   ip_address: The IP address to reserve
    #   description: The description of the reserve IPv4 address
    #   version: IP version (deafult = 4)
    # Return: the returned confirmed IPv4 address
    def reserve_ip(self, vlan_id=None, ip_address=None, 
                             description=None, version=4):
        params = {}
        if vlan_id is None or ip_address is None:
            raise NTTCCISAPIException('A vlan and IPv4 address must be '
                                      'provided')
        if version != 4 and version != 6:
            raise NTTCCISAPIException('Invalid IP version - %d' % version)
        params['vlanId'] = vlan_id
        params['ipAddress'] = ip_address
        if description is not None:
            params['description'] = description

        url = self.base_url + 'network/reservePrivateIpv4Address'
        if version == 6:
            url = self.base_url + 'network/reserveIpv6Address'

        response = self.api_post_call(url, params)
        try:
            return response.json()['info'][0]['value']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the reserve '
                                         'private ipv%d address request was '
                                         'accepted' % version)


    # Args: 
    #   vlan_id: VLAN UUID
    #   ipv_address: The IP address to reserve
    # Return: string (API message)
    def unreserve_ip(self, vlan_id=None, ip_address=None, version=4):
        params = {}
        if vlan_id is None or ip_address is None:
            raise NTTCCISAPIException('A vlan and IPv4 address must be '
                                      'provided')
        if version != 4 and version != 6:
            raise NTTCCISAPIException('Invalid IP version - %d' % version)
        params['vlanId'] = vlan_id
        params['ipAddress'] = ip_address

        url = self.base_url + 'network/unreservePrivateIpv4Address'
        if version == 6:
            url = self.base_url + 'network/unreserveIpv6Address'
        
        response = self.api_post_call(url, params)
        try:
            if response.json()['responseCode'] == "OK":
                return response.json()['message']
            else:
                return response.json()['error']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the '
                                         'unreserving of the private ipv%d '
                                         'address request was accepted'
                                         % version)


    # Args: 
    #   network_domain_id: Cloud Network Domain UUID
    # Return: Array of NATs
    def list_nat_rule(self, network_domain_id):
        url = self.base_url + 'network/natRule'

        params = {'networkDomainId': network_domain_id}
        response = self.api_get_call(url, params)
        try:
            return response.json()['natRule']
        except KeyError:
            return []


    # Args: 
    #   network_domain_id: Cloud Network Domain UUID
    #   ip_address: The IP address to reserve
    #   description: The description of the reserve IPv4 address
    #   version: IP version (deafult = 4)
    # Return: the returned confirmed IPv4 address
    def create_nat_rule(self, network_domain_id=None, internal_ip=None, 
                   external_ip=None):
        params = {}
        if internal_ip is None or external_ip is None:
            raise NTTCCISAPIException('A valid internal and external IP '
                                      'address must be provided')
        if network_domain_id is None:
            raise NTTCCISAPIException('A valid Network Domain is required')
        params['networkDomainId'] = network_domain_id
        params['internalIp'] = internal_ip
        params['externalIp'] = external_ip

        url = self.base_url + 'network/createNatRule'

        response = self.api_post_call(url, params)
        try:
            return response.json()['info'][0]['value']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the create NAT '
                                      'rule request was accepted')
        except IndexError:
            raise NTTCCISAPIException('Could not confirm that the create NAT '
                                      'rule request was accepted')


    # Args: 
    #   nat_rule_id: NAT rule UUID
    # Return: The NAT rule object
    def get_nat_rule(self, nat_rule_id):
        url = self.base_url + 'network/natRule/%s' % (nat_rule_id)

        response = self.api_get_call(url)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')


    # Args: 
    #   nat_rule_id: NAT rule UUID
    # Return: string (API message)
    def remove_nat_rule(self, nat_rule_id):
        params = {'id': nat_rule_id}

        url = self.base_url + 'network/deleteNatRule'
        response = self.api_post_call(url, params)
        try:
            if response.json()['responseCode'] == "OK":
                return response.json()['message']
            else:
                return response.json()['error']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the '
                                         'remove NAT rule request was '
                                         'accepted')


    # Args: 
    #   network_domain_id: Cloud Network Domain UUID
    # Return: Array of Port Lists
    def list_port_list(self, network_domain_id):
        url = self.base_url + 'network/portList'

        params = {'networkDomainId': network_domain_id}
        response = self.api_get_call(url, params)
        try:
            return response.json()['portList']
        except KeyError:
            return []


    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   port_list_id: The UUID of a Port List
    # Return: Port List
    def get_port_list(self, network_domain_id, port_list_id):

        url = self.base_url + 'network/portList/%s' % port_list_id

        response = self.api_get_call(url)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')

    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   name: The name of a Port List
    # Return: Port List
    def get_port_list_by_name(self, network_domain_id, name):
        url = self.base_url + 'network/portList'

        params = {'networkDomainId': network_domain_id}
        response = self.api_get_call(url, params)
        try:
            port_lists = response.json()['portList']
            port_list_exists = filter(lambda x: x['name'] ==  name, 
                                      port_lists)
            return port_list_exists[0]
        except KeyError:
            return None
        except IndexError:
            return None

    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   name: The name of a Port List
    #   description: The description of the port list
    #   ports: An array of beginning and end ports
    #   child_port_list: An array of port list UUIDs
    # Return: Port List UUID
    def create_port_list(self, network_domain_id, name, description, ports,
                         child_port_list):
        child_port_list_uuid = []
        params = {}
        params['port'] = []
        if network_domain_id is None or name is None or ports is None:
            raise NTTCCISAPIException('A valid Network Domain, Name and '
                                      'Beginning Port is required')
        if child_port_list is not None:
            for uuid in child_port_list:
                try:
                    result = self.get_port_list(network_domain_id, uuid)
                    child_port_list_uuid.append(result['id'])
                except NTTCCISAPIException as e:
                    raise NTTCCISAPIException(e)
                except KeyError:
                    raise NTTCCISAPIException('Could not find child port '
                                              'lists')

        for port in ports:
            new_port_group = {}
            try:
                new_port_group['begin'] = port['port_begin']
                if 'port_end' in port:
                    if port['port_end'] > port['port_begin']:
                        new_port_group['end'] = port['port_end']
                    else:
                        raise NTTCCISAPIException('End port must be greated '
                                      'than the beginning port')
                params['port'].append(new_port_group)
            except KeyError:
                raise NTTCCISAPIException('Port groups must have a '
                                          'beginning port')

        url = self.base_url + 'network/createPortList'

        params['networkDomainId'] = network_domain_id
        params['name'] = name
        if description is not None:
            params['description'] = description

        if len(child_port_list_uuid) > 0:
            params['childPortListId'] = child_port_list_uuid

        response = self.api_post_call(url, params)
        try:
            return response.json()['info'][0]['value']
        except KeyError, IndexError:
            raise NTTCCISAPIException('Could not confirm that the create Port'
                                      ' List request was accepted')


    # Args:
    #   network_domain_id: The UUID of the Cloud Network Domain
    #   port_list_id: The UUID of a Port List
    #   description: The description of the port list
    #   ports: An array of beginning and end ports
    #   ports_nil: Boolean to denote whether to delete all ports
    #   child_port_list: An array of port list UUIDs
    #   child_port_list_nil: Boolean to denote whether to delete all child
    #                        Port Lists
    # Return: Port List UUID
    def update_port_list(self, network_domain_id, port_list_id, description, 
                         ports,ports_nil, child_port_list, 
                         child_port_list_nil):
        child_port_list_uuid = []
        params = {}
        params['port'] = []
        if port_list_id is None or (ports is None and not ports_nil):
            raise NTTCCISAPIException('A valid Port List ID and list of ports'
                                      ' is required')
        if child_port_list_nil:
            child_port_list_uuid.append({'nil': True})
        elif child_port_list is not None:
            if network_domain_id is None:
                raise NTTCCISAPIException('A valid Network Domain is '
                                          'required')
            for uuid in child_port_list:
                try:
                    result = self.get_port_list(network_domain_id, uuid)
                    child_port_list_uuid.append(result['id'])
                except NTTCCISAPIException as e:
                    raise NTTCCISAPIException(e)
                except KeyError:
                    raise NTTCCISAPIException('Could not find child port '
                                              'lists')

        if ports_nil:
            params['port'].append({'nil': True})
        else:
            for port in ports:
                new_port_group = {}
                try:
                    new_port_group['begin'] = port['port_begin']
                    if 'port_end' in port:
                        if port['port_end'] > port['port_begin']:
                            new_port_group['end'] = port['port_end']
                        else:
                            raise NTTCCISAPIException('End port must be '
                                          'greater than the beginning port')
                    params['port'].append(new_port_group)
                except KeyError:
                    raise NTTCCISAPIException('Port groups must have a '
                                              'beginning port')

        url = self.base_url + 'network/editPortList'

        params['id'] = port_list_id
        if description is not None:
            params['description'] = description

        if len(child_port_list_uuid) > 0:
            params['childPortListId'] = child_port_list_uuid

        response = self.api_post_call(url, params)
        try:
            return response.json()['responseCode']
        except KeyError, IndexError:
            raise NTTCCISAPIException('Could not confirm that the update Port'
                                      ' List request was accepted')


    # Args: 
    #   port_list_id: Port List UUID
    # Return: string (API message)
    def remove_port_list(self, port_list_id):
        params = {'id': port_list_id}

        url = self.base_url + 'network/deletePortList'
        response = self.api_post_call(url, params)
        try:
            if response.json()['responseCode'] == "OK":
                return response.json()['message']
            else:
                return response.json()['error']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the '
                                         'remove Port List request was '
                                         'accepted')


    # Args: 
    #   network_domain_id: Cloud Network Domain UUID
    #   version: IP version
    # Return: Array of IP Address Lists
    def list_ip_list(self, network_domain_id, version):
        url = self.base_url + 'network/ipAddressList'

        params = {'networkDomainId': network_domain_id}
        if version is not None:
            params['ipVersion'] = version

        response = self.api_get_call(url, params)
        try:
            return response.json()['ipAddressList']
        except KeyError:
            return []


    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   port_list_id: The UUID of a IP Address List
    # Return: IP Address List
    def get_ip_list(self, network_domain_id, ip_address_list_id):

        url = self.base_url + 'network/ipAddressList/%s' % ip_address_list_id

        response = self.api_get_call(url)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')

    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   name: The name of a IP Address List
    # Return: IP Address List
    def get_ip_list_by_name(self, network_domain_id, name, version):
        url = self.base_url + 'network/ipAddressList'

        params = {'networkDomainId': network_domain_id}
        if version is not None:
            params['ipVersion'] = version
        response = self.api_get_call(url, params)
        try:
            ip_address_lists = response.json()['ipAddressList']
            ip_address_list_exists = filter(lambda x: x['name'] ==  name, 
                                      ip_address_lists)
            return ip_address_list_exists[0]
        except KeyError:
            return None
        except IndexError:
            return None

    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   name: The name of a IP Address List
    #   description: The description of the IP Address list
    #   ip_addresses: An array of beginning and end ports
    #   child_ip_list: An array of IP Address list UUIDs
    #   version: IP version
    # Return: IP Address List UUID
    def create_ip_list(self, network_domain_id, name, description, 
                       ip_addresses, child_ip_list, version):
        child_ip_list_uuid = []
        params = {}
        params['ipAddress'] = []
        if (network_domain_id is None or name is None or ip_addresses is None
            or version is None):
            raise NTTCCISAPIException('A valid Network Domain, Name and '
                                      'list of IP addresses and version '
                                      'is required')
        if child_ip_list is not None:
            for uuid in child_ip_list:
                try:
                    result = self.get_ip_list(network_domain_id, uuid)
                    child_ip_list_uuid.append(result['id'])
                except NTTCCISAPIException as e:
                    raise NTTCCISAPIException(e)
                except KeyError:
                    raise NTTCCISAPIException('Could not find child IP '
                                              'Address lists')

        for ip_address in ip_addresses:
            new_ip_group = {}
            try:
                new_ip_group['begin'] = ip_address['begin']
                if 'end' in ip_address:
                    new_ip_group['end'] = ip_address['end']
                elif 'prefix' in ip_address:
                    new_ip_group['prefixSize'] = ip_address['prefix']
                params['ipAddress'].append(new_ip_group)
            except KeyError:
                raise NTTCCISAPIException('IP Addresses must have a '
                                          'beginning IP Address')

        url = self.base_url + 'network/createIpAddressList'

        params['networkDomainId'] = network_domain_id
        params['name'] = name
        params['ipVersion'] = version
        if description is not None:
            params['description'] = description

        if len(child_ip_list_uuid) > 0:
            params['childIpAddressListId'] = child_ip_list_uuid

        response = self.api_post_call(url, params)
        try:
            return response.json()['info'][0]['value']
        except KeyError, IndexError:
            raise NTTCCISAPIException('Could not confirm that the create IP '
                                      'Address List request was accepted')


    # Args:
    #   network_domain_id: The UUID of the Cloud Network Domain
    #   ip_address_list_id: The UUID of a IP Address List
    #   description: The description of the IP Address list
    #   ip_addresses: An array of beginning and end ip addresses
    #   ip_addresses_nil: Boolean to denote whether to delete all ip addresses
    #   child_ip_list: An array of IP Address list UUIDs
    #   child_ip_list_nil: Boolean to denote whether to delete all child
    #                        IP Address Lists
    # Return: Port List UUID
    def update_ip_list(self, network_domain_id, ip_address_list_id, 
                       description, ip_addresses, ip_addresses_nil, 
                       child_ip_list, child_ip_list_nil):
        child_ip_list_uuid = []
        params = {}
        params['ipAddress'] = []
        if ip_address_list_id is None or (ip_addresses is None and not 
                                          ip_addresses_nil):
            raise NTTCCISAPIException('A valid IP Address List ID and list of'
                                      ' IP Addresses is required')
        if child_ip_list_nil:
            child_ip_list_uuid.append({'nil': True})
        elif child_ip_list is not None:
            if network_domain_id is None:
                raise NTTCCISAPIException('A valid Network Domain is '
                                          'required')
            for uuid in child_ip_list:
                try:
                    result = self.get_ip_list(network_domain_id, uuid)
                    child_ip_list_uuid.append(result['id'])
                except NTTCCISAPIException as e:
                    raise NTTCCISAPIException(e)
                except KeyError:
                    raise NTTCCISAPIException('Could not find child IP '
                                              'Address lists')

        if ip_addresses_nil:
            params['ipAddress'].append({'nil': True})
        else:
            for ip_address in ip_addresses:
                new_ip_group = {}
                try:
                    new_ip_group['begin'] = ip_address['begin']
                    if 'end' in ip_address:
                        new_ip_group['end'] = ip_address['end']
                    elif 'prefix' in ip_address:
                        new_ip_group['prefixSize'] = (
                            ip_address['prefix'])
                    params['ipAddress'].append(new_ip_group)
                except KeyError:
                    raise NTTCCISAPIException('IP Addresses must have a '
                                              'beginning IP Address')

        url = self.base_url + 'network/editIpAddressList'

        params['id'] = ip_address_list_id
        if description is not None:
            params['description'] = description

        if len(child_ip_list_uuid) > 0:
            params['childIpAddressListId'] = child_ip_list_uuid

        response = self.api_post_call(url, params)
        try:
            return response.json()['responseCode']
        except KeyError, IndexError:
            raise NTTCCISAPIException('Could not confirm that the update IP '
                                      'Address List request was accepted')


    # Args: 
    #   ip_address_list_id: IP Address List UUID
    # Return: string (API message)
    def remove_ip_list(self, ip_address_list_id):
        params = {'id': ip_address_list_id}

        url = self.base_url + 'network/deleteIpAddressList'
        response = self.api_post_call(url, params)
        try:
            if response.json()['responseCode'] == "OK":
                return response.json()['message']
            else:
                return response.json()['error']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the remove'
                                      ' IP Address List request was '
                                      'accepted')


    # Args: 
    #   network_domain_id: Cloud Network Domain UUID
    # Return: Array of firewall rules
    def list_fw_rules(self, network_domain_id,):
        url = self.base_url + 'network/firewallRule'

        params = {'networkDomainId': network_domain_id}

        response = self.api_get_call(url, params)
        try:
            return response.json()['firewallRule']
        except KeyError:
            return []


    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   port_list_id: The UUID of a IP Address List
    # Return: firewall rule
    def get_fw_rule(self, network_domain_id, ip_address_list_id):

        url = self.base_url + 'network/firewallRule/%s' % ip_address_list_id

        response = self.api_get_call(url)
        if response != None:
            return response.json()
        else:
            raise NTTCCISAPIException('No response from the API')

    # Args:
    #   network_domain_id: Cloud Network Domain UUID
    #   name: The name of a firewall rule
    #   version: the IP version ([IPV4, IPv6])
    # Return: firewall rule
    def get_fw_rule_by_name(self, network_domain_id, name):
        url = self.base_url + 'network/firewallRule'

        params = {'networkDomainId': network_domain_id}
        response = self.api_get_call(url, params)
        try:
            fw_rules = response.json()['firewallRule']
            fw_rule_exists = filter(lambda x: x['name'] ==  name, 
                                      fw_rules)
            return fw_rule_exists[0]
        except KeyError:
            return None
        except IndexError:
            return None


    # Args:
    #   network_domain_id: UUID of the Cloud Network Domain
    #   name: The name of a firewall rule
    #   action: [ACCEPT_DECISIVELY, DROP]
    #   version: [IPV4, IPV6]
    #   protocol: [IP, ICMP, TCP, UDP]
    #   src_ip: (string) IPv4 or IPv6 address - omit all src IP for "ANY"
    #   src_ip_prefix: (string) IP prefix
    #   src_ip_list_id: (string) UUID of an IP Address List
    #   dst_ip: (string) IPv4 or IPv6 address - omit all dst IP for "ANY"
    #   dst_ip_prefix: (string) IP prefix
    #   dst_ip_list_id: (string) UUID of an IP Address List
    #   src_port_begin: (string) beginning port number - omit all src ports 
    #                   for "ANY"
    #   src_port_end: (string) end port number for a port range
    #   src_port_list: (string) UUID of a port list
    #   dst_port_begin: (string) beginning port number - omit all dst ports 
    #                   for "ANY"
    #   dst_port_end: (string) end port number for a port range
    #   dst_port_list: (string) UUID of a port list
    #   enabled: (boolean) whether to enable the firewall rule
    #   position: [FIRST, LAST, BEFORE, AFTER]
    #   position_to: (string) name of an existing firewall rule
    # Return: message
    def create_fw_rule(self, network_domain_id, name, action, version, 
                       protocol, src_ip, src_ip_prefix, src_ip_list_id,
                       dst_ip, dst_ip_prefix, dst_ip_list_id, src_port_begin, 
                       src_port_end, src_port_list_id, dst_port_begin,
                       dst_port_end, dst_port_list_id, enabled, position,
                       position_to):
        url = self.base_url + 'network/createFirewallRule'
        params = {}
        params['placement'] = {}
        params['source'] = {}
        params['destination'] = {}
        if network_domain_id is None:
            raise NTTCCISAPIException('Network Domain UUID is required')
        if name is None:
            raise NTTCCISAPIException('Name is required')
        if src_ip is None and src_ip_list_id is None:
            raise NTTCCISAPIException('Source IP or IP Address list is '
                                      'required')
        if dst_ip is None and dst_ip_list_id is None:
            raise NTTCCISAPIException('Destination IP or IP address list is '
                                      'required')
        if src_port_begin is None and src_port_list_id is None:
            raise NTTCCISAPIException('Source Port or Port list is required')
        if dst_port_begin is None and dst_port_list_id is None:
            raise NTTCCISAPIException('Destination Port or Port list is '
                                      'required')

        params['networkDomainId'] = network_domain_id
        params['name'] = name
        if src_ip_list_id is not None:
            params['source']['ipAddressListId'] = src_ip_list_id
        else:
            params['source']['ip'] = {}
            params['source']['ip']['address'] = src_ip
            if src_ip_prefix is not None:
                params['source']['ip']['prefixSize'] = src_ip_prefix
        if dst_ip_list_id is not None:
            params['destination']['ipAddressListId'] = dst_ip_list_id
        else:
            params['destination']['ip'] = {}
            params['destination']['ip']['address'] = dst_ip
            if dst_ip_prefix is not None:
                params['destination']['ip']['prefixSize'] = dst_ip_prefix
        if src_port_list_id is not None:
            params['source']['portListId'] = src_port_list_id
        else:
            if src_port_begin != 'ANY':
                params['source']['port'] = {}
                params['source']['port']['begin'] = src_port_begin
                if src_port_end is not None:
                    params['source']['port']['end'] = src_port_end
        if dst_port_list_id is not None:
            params['destination']['portListId'] = dst_port_list_id
        else:
            if dst_port_begin != 'ANY':
                params['destination']['port'] = {}
                params['destination']['port']['begin'] = dst_port_begin
                if dst_port_end is not None:
                    params['destination']['port']['end'] = dst_port_end
        if action is None:
            action = 'ACCEPT_DECISIVELY'
        if version is None:
            version = 'IPV4'
        if protocol is None:
            protocol = 'TCP'
        if enabled is None:
            enabled = True
        if position is None:
            position = 'LAST'
        if position_to is not None:
            params['placement']['relativeToRule'] = position_to

        params['placement']['position'] = position
        params['enabled'] = enabled
        params['protocol'] = protocol
        params['ipVersion'] = version
        params['action'] = action

        response = self.api_post_call(url, params)
        try:
            return response.json()['info'][0]['value']
        except KeyError, IndexError:
            raise NTTCCISAPIException('Could not confirm that the create '
                                      'firewall rule request was accepted')


    # Args:
    #   id: UUID of the firewall rule
    #   action: [ACCEPT_DECISIVELY, DROP]
    #   protocol: [IP, ICMP, TCP, UDP]
    #   src_ip: (string) IPv4 or IPv6 address
    #   src_ip_prefix: (string) IP prefix
    #   src_ip_list_id: (string) UUID of an IP Address List
    #   dst_ip: (string) IPv4 or IPv6 address
    #   dst_ip_prefix: (string) IP prefix
    #   dst_ip_list_id: (string) UUID of an IP Address List
    #   src_port_begin: (string) beginning port number for
    #   src_port_end: (string) end port number for a port range
    #   src_port_list: (string) UUID of a port list
    #   dst_port_begin: (string) beginning port number
    #   dst_port_end: (string) end port number for a port range
    #   dst_port_list: (string) UUID of a port list
    #   enabled: (boolean) whether to enable the firewall rule
    #   position: [FIRST, LAST, BEFORE, AFTER]
    #   position_to: (string) name of an existing firewall rule
    # Return: message
    def update_fw_rule(self, fw_rule_id, action,protocol, src_ip, 
                       src_ip_prefix, src_ip_list_id, dst_ip, dst_ip_prefix,
                       dst_ip_list_id, src_port_begin, src_port_end,
                       src_port_list_id, dst_port_begin, dst_port_end,
                       dst_port_list_id, enabled, position, position_to):
        url = self.base_url + 'network/editFirewallRule'
        params = {}
        
        if fw_rule_id is None:
            raise NTTCCISAPIException('Id is required')
        if src_ip is None and src_ip_list_id is None:
            raise NTTCCISAPIException('Source IP or IP Address list is '
                                      'required')
        if dst_ip is None and dst_ip_list_id is None:
            raise NTTCCISAPIException('Destination IP or IP address list is '
                                      'required')
        if src_port_begin is None and src_port_list_id is None:
            raise NTTCCISAPIException('Source Port or Port list is required')
        if dst_port_begin is None and dst_port_list_id is None:
            raise NTTCCISAPIException('Destination Port or Port list is '
                                      'required')

        params['id'] = fw_rule_id
        if src_ip_list_id is not None:
            params['source'] = {}
            params['source']['ipAddressListId'] = src_ip_list_id
        elif src_ip is not None:
            params['source'] = {}
            params['source']['ip'] = {}
            params['source']['ip']['address'] = src_ip
            if src_ip_prefix is not None:
                params['source']['ip']['prefixSize'] = src_ip_prefix
        if dst_ip_list_id is not None:
            params['destination'] = {}
            params['destination']['ipAddressListId'] = dst_ip_list_id
        elif dst_ip is not None:
            params['destination'] = {}
            params['destination']['ip'] = {}
            params['destination']['ip']['address'] = dst_ip
            if dst_ip_prefix is not None:
                params['destination']['ip']['prefixSize'] = dst_ip_prefix
        if src_port_list_id is not None:
            params['source']['portListId'] = src_port_list_id
        elif src_port_begin is not None:
            if src_port_begin != 'ANY':
                params['source']['port'] = {}
                params['source']['port']['begin'] = src_port_begin
                if src_port_end is not None:
                    params['source']['port']['end'] = src_port_end
        if dst_port_list_id is not None:
            params['destination']['portListId'] = dst_port_list_id
        elif dst_port_begin is not None:
            if dst_port_begin != 'ANY':
                params['destination']['port'] = {}
                params['destination']['port']['begin'] = dst_port_begin
                if dst_port_end is not None:
                    params['destination']['port']['end'] = dst_port_end
        if action is not None:
            params['action'] = action
        if protocol is not None:
            params['protocol'] = protocol
        if enabled is not None:
            params['enabled'] = enabled
        if position is not None:
            params['placement'] = {}
            params['placement']['position'] = position
        if position_to is not None:
            if 'placement' not in params:
                params['placement'] = {}
            params['placement']['relativeToRule'] = position_to

        response = self.api_post_call(url, params)
        try:
            return response.json()['responseCode']
        except KeyError, IndexError:
            raise NTTCCISAPIException('Could not confirm that the update '
                                      'firewall rule request was accepted')


    # Args: 
    #   fw_rule_id: UUID of the firewall rule
    # Return: string (API message)
    def remove_fw_rule(self, firewall_rule_id):
        params = {'id': firewall_rule_id}

        url = self.base_url + 'network/deleteFirewallRule'
        response = self.api_post_call(url, params)
        try:
            if response.json()['responseCode'] == "OK":
                return response.json()['message']
            else:
                return response.json()['error']
        except KeyError:
            raise NTTCCISAPIException('Could not confirm that the remove'
                                      ' firewall rule request was '
                                      'accepted')

    def api_get_call(self, url, params=None):
        response = REQ.get(url, auth=self.credentials, headers=HTTP_HEADERS, 
                           params=params)
        try:
            if response != None:
                if (response.status_code == 200):
                    return response
                else:
                    raise NTTCCISAPIException(response.status_code)
            else:
                raise NTTCCISAPIException('No response from the API for url: '
                                         '%s') % (url)
        except Exception as e:
            try:
                raise NTTCCISAPIException('%s - %s' % (e, response.json()
                                                       ['message']))
            except Exception as e:
                raise NTTCCISAPIException('%s - %s' % (e, response))


    def api_post_call(self, url, params):
        response = REQ.post(url, auth=self.credentials, headers=HTTP_HEADERS, 
                           json=params)
        try:
            if response != None:
                if (response.status_code == 200):
                    return response
                else:
                    raise NTTCCISAPIException(response.status_code)
            else:
                raise NTTCCISAPIException('No response from the API for url: '
                                         '%s') % (url)
        except Exception as e:
            try:
                raise NTTCCISAPIException('%s - %s' % (e, response.json()
                                                        ['message']))
            except Exception as e:
                raise NTTCCISAPIException(response)

