#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2015, Dan Radez <dradez@redhat.com>
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

import subprocess
import requests
import sys
import json

DOCUMENTATION = '''
---
module: foreman
version_added: "0.1"
short_description: Provision servers via foreman
description:
   - Provision servers via foreman
options:
        foreman_username                = dict(default='admin'),
        foreman_password                = dict(required=True),
        foreman_url                     = dict(default='https://127.0.0.1/api/v2/'),
        node                            = dict(required=True),
        ipmi_username                   = dict(default='root'),
        ipmi_password                   = dict(required=True),
        ipmi_host                       = dict(required=True),
        key_name                        = dict(default=None),
   foreman_username:
     description:
        - login username to authenticate to foreman
     required: true
     default: admin
   foreman_password:
     description:
        - Password of login user
     required: true
   foreman_url:
     description:
        - The foreman api url
     required: false
     default: 'https://127.0.0.1/v2.0/'
   node:
     description:
        - Name that has to be given to the instance
     required: true
     default: None
   ipmi_username:
     description:
        - login username to authenticate to node's ipmi interface
     required: true
     default: root
   ipmi_password:
     description:
        - Password of ipmi user
     required: true
   ipmi_host:
     description:
        - address to connect to ipmi
     required: true
   key_name:
     description:
        - The key pair name to be used when creating a VM
     required: false
     default: None
   wait:
     description:
        - If the module should wait for the VM to be created.
     required: false
     default: 'yes'
   wait_for:
     description:
        - The amount of time the module should wait for the VM to get into active state
     required: false
     default: 240
requirements: ["ipmi-tools"]
'''

EXAMPLES = '''
# Creates a new VM and attaches to a network and passes metadata to the instance
'''

def main():
    module = AnsibleModule(
        argument_spec                   = dict(
        foreman_username                = dict(default='admin'),
        foreman_password                = dict(required=True),
        foreman_url                     = dict(default='https://127.0.0.1/api/v2/'),
        node                            = dict(required=True),
        ipmi_username                   = dict(default='root'),
        ipmi_password                   = dict(required=True),
        ipmi_host                       = dict(required=True),
        key_name                        = dict(default=None),
        wait                            = dict(default='yes', choices=['yes', 'no']),
        wait_for                        = dict(default=240),
        state                           = dict(default='present', choices=['absent', 'present']),
        ),
    )

    # Read in the yaml groups file
    #f = open('groups.yml')
    #groups = yaml.safe_load(f)
    #f.close()

    # pull out the module params
    username = module.params['foreman_username']
    password = module.params['foreman_password']
    url = module.params['foreman_url']
    node = module.params['node']
    ipmi_username = module.params['ipmi_username']
    ipmi_password = module.params['ipmi_password']
    ipmi_host = module.params['ipmi_host']

    # Create a new http session with the following auth details and disabling ssl verification.
    s = requests.Session()
    s.auth = (username, password)
    s.verify = False

    hosts_url = url + 'hosts/'

    headers = {'Content-Type': 'application/json', }
    data=json.dumps({'host': {'build': 'true'}})
    r = s.put(url + 'hosts/%s' % node, data=data, headers=headers)

    if r.status_code != 200:
        module.fail_json(msg=r.json()['message'])
    else:
        ipmi = subprocess.Popen(["ipmitool","-I","lanplus",
                                           "-U",ipmi_username,
                                           "-P",ipmi_password,
                                           "-H",ipmi_host,"power","cycle"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        ipmi_msg=ipmi.communicate()[0]
        if ipmi.returncode:
            module.fail_json(msg=ipmi_msg)
        else:
            module.exit_json(changed=True, msg=ipmi_msg)

    module.exit_json(changed=True)

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
main()

