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
# List, Create and Destory an Ansible Bastion Host

import json
from ansible.module_utils.basic import *
from ansible.module_utils.nttc_cis import *
try:
    from ansible.module_utils.v2 import NTTCISClient, NTTCISAPIException
    from ansible.module_utils.config import API_ENDPOINTS
    NTTCIS_IMPORTED = True
except:
    NTTCIS_IMPORTED = False


DOCUMENTATION = '''
'''
EXAMPLES = '''
'''
RETURN = '''
'''


def get_nttc_cis_regions():
    regions = []
    for region in API_ENDPOINTS:
        regions.append(region)
    return regions


def main():
    nttc_cis_regions = get_nttc_cis_regions()
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', choices=nttc_cis_regions),
            location=dict(required=True, type='str'),
            network=dict(required=True, type='str'),
            password=dict(default=None, required=False, type='str'),
            ipv4=dict(default=None, required=False, type='str'),
            state=dict(default='present', choices=['present', 'absent',
                       'query']),
            wait=dict(required=False, default=False, type='bool'),
            wait_time=dict(required=False, default=600, type='int'),
            wait_poll_interval=dict(required=False, default=2, type='int'),
            verify_ssl_cert=dict(required=False, default=True, type='bool')
        )
    )

if __name__ == '__main__':
    main()