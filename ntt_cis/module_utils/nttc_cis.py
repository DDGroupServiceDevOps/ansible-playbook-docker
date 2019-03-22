#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 NTT Communictions Cloud Infrastructure Services
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
#   - Aimon Bustardo <aimon.bustardo@dimensiondata.com>
#
# Common methods to be used by versious module components
import os
import ConfigParser
import string
import random
from os.path import expanduser

def get_credentials():
    user_id = None
    key = None

    # Attempt to grab from environment
    if 'NTTCIS_USER' in os.environ and 'NTTCIS_PASSWORD' in os.environ:
        user_id = os.environ['NTTCIS_USER']
        key = os.environ['NTTCIS_PASSWORD']

    # Environment failed try dot file
    if user_id is None or key is None:
        home = expanduser('~')
        config = ConfigParser.RawConfigParser()
        config.read("%s/.nttcis" % home)
        try:
            user_id = config.get("nttcis", "NTTCIS_USER")
            key = config.get("nttcis", "NTTCIS_PASSWORD")
        except:
            pass

    # Return False if either are not found
    if user_id is None or key is None:
        return False

    # Both found, return data
    return (user_id, key)

def generate_password():
    length = random.randint(12,19)
    special_characters = str(string.punctuation).translate(None,'<>\'\\')
    pwd = []
    count = 0
    while count != length:
        select = random.randint(0,4)
        if select == 0:
            pwd.append(random.choice(string.ascii_lowercase))
        elif select == 1:
            pwd.append(random.choice(string.ascii_uppercase))
        elif select == 2:
            pwd.append(str(random.randint(0,9)))
        else:
            pwd.append(random.choice(special_characters))
        count = count + 1

    random.shuffle(pwd)
    pwdStr = ''.join(pwd)
    
    return pwdStr