#!/usr/bin/python
""" PN CLI admin-service-modify """

# Copyright 2018 Pluribus Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: pn_admin_service
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to modify admin-service.
description:
  - C(modify): modify services on the server-switch
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'present' to create admin-service and
        'absent' to delete admin-service 'update' to modify the admin-service.
    required: True
  pn_action:
    description:
      - admin-service configuration command.
    required: true
    choices: ['modify']
    type: str
  pn_web:
    description:
      - Web (HTTP) - enable or disable
    required: false
    type: bool
  pn_web_ssl:
    description:
      - Web SSL (HTTPS) - enable or disable
    required: false
    type: bool
  pn_snmp:
    description:
      - Simple Network Monitoring Protocol (SNMP) - enable or disable
    required: false
    type: bool
  pn_web_port:
    description:
      - Web (HTTP) port - enable or disable
    required: false
    type: str
  pn_web_ssl_port:
    description:
      - Web SSL (HTTPS) port - enable or disable
    required: false
    type: str
  pn_nfs:
    description:
      - Network File System (NFS) - enable or disable
    required: false
    type: bool
  pn_ssh:
    description:
      - Secure Shell - enable or disable
    required: false
    type: bool
  pn_web_log:
    description:
      - Web logging - enable or disable
    required: false
    type: bool
  pn__if:
    description:
      - administrative service interface
    required: false
    type: str
  pn_icmp:
    description:
      - Internet Message Control Protocol (ICMP) - enable or disable
    required: false
    type: bool
  pn_net_api:
    description:
      - Netvisor API - enable or disable APIs
    required: false
    type: bool
"""

EXAMPLES = """
- name: admin service functionality
  pn_admin_service:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn__if: "mgmt"
    pn_web: False
    pn_web_ssl: False
    pn_icmp: True

- name: admin service functionality
  pn_admin_service:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_web: False
    pn__if: "mgmt"
    pn_snmp: True
    pn_net_api: True
    pn_ssh: True
    pn_nfs: True  
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the admin-service command.
  returned: always
  type: list
stderr:
  description: set of error responses from the admin-service command.
  returned: on error
  type: list
changed:
  description: indicates whether the CLI caused changes on the target.
  returned: always
  type: bool
"""

import shlex

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pn_nvos import pn_cli


def run_cli(module, cli):
    """
    This method executes the cli command on the target node(s) and returns the
    output. The module then exits based on the output.
    :param cli: the complete cli string to be executed on the target node(s).
    :param module: The Ansible module to fetch command
    """
    cliswitch = module.params['pn_cliswitch']
    state = module.params['state']
    command = get_command_from_state(state)

    cmd = shlex.split(cli)
    result, out, err = module.run_command(cmd)

    print_cli = cli.split(cliswitch)[0]

    # Response in JSON format
    if err:
        module.fail_json(
            command=print_cli,
            stderr=err.strip(),
            msg="admin-service %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="admin-service %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="admin-service %s operation completed" % cmd,
            changed=True
        )


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'update':
        command = 'admin-service-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['update']),
            pn_web=dict(required=False, type='bool'),
            pn_web_ssl=dict(required=False, type='bool'),
            pn_snmp=dict(required=False, type='bool'),
            pn_web_port=dict(required=False, type='str'),
            pn_web_ssl_port=dict(required=False, type='str'),
            pn_nfs=dict(required=False, type='bool'),
            pn_ssh=dict(required=False, type='bool'),
            pn_web_log=dict(required=False, type='bool'),
            pn__if=dict(required=False, type='str'),
            pn_icmp=dict(required=False, type='bool'),
            pn_net_api=dict(required=False, type='bool'),
        ),
        required_if=[['state', 'update', ['pn__if']]],
        required_one_of=[['pn_web', 'pn_web_ssl', 'pn_snmp', 'pn_web_port',
                        'pn_web_ssl_port', 'pn_nfs', 'pn_ssh', 'pn_web_log',
                        'pn_icmp', 'pn_net_api']],
    )

    # Accessing the arguments
    state = module.params['state']
    web = module.params['pn_web']
    web_ssl = module.params['pn_web_ssl']
    snmp = module.params['pn_snmp']
    web_port = module.params['pn_web_port']
    web_ssl_port = module.params['pn_web_ssl_port']
    nfs = module.params['pn_nfs']
    ssh = module.params['pn_ssh']
    web_log = module.params['pn_web_log']
    _if = module.params['pn__if']
    icmp = module.params['pn_icmp']
    net_api = module.params['pn_net_api']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'admin-service-modify':
        cli += ' %s ' % command
        if web:
            if web is True:
                cli += ' web '
            else:
                cli += ' no-web '
        if web_ssl:
            if web_ssl is True:
                cli += ' web-ssl '
            else:
                cli += ' no-web-ssl '
        if snmp:
            if snmp is True:
                cli += ' snmp '
            else:
                cli += ' no-snmp '
        if web_port:
            cli += ' web-port ' + web_port
        if web_ssl_port:
            cli += ' web-ssl-port ' + web_ssl_port
        if nfs:
            if nfs is True:
                cli += ' nfs '
            else:
                cli += ' no-nfs '
        if ssh:
            if ssh is True:
                cli += ' ssh '
            else:
                cli += ' no-ssh '
        if web_log:
            if web_log is True:
                cli += ' web-log '
            else:
                cli += ' no-web-log '
        if _if:
            cli += ' if ' + _if
        if icmp:
            if icmp is True:
                cli += ' icmp '
            else:
                cli += ' no-icmp '
        if net_api:
            if net_api is True:
                cli += ' net-api '
            else:
                cli += ' no-net-api '

    run_cli(module, cli)


if __name__ == '__main__':
    main()
