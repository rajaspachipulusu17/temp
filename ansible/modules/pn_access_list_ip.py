#!/usr/bin/python
""" PN CLI access-list-ip-add/remove """

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
module: pn_access_list_ip
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to add/remove access-list-ip.
description:
  - C(add): Add IPs associated with access list
  - C(remove): Remove IPs associated with access list
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'present' to add access-list-ip and
      'absent' to remove access-list-ip.
    required: True
  pn_ip:
    description:
      - IP associated with the access list
    required: false
    type: str
  pn_name:
    description:
      - Access List Name
    required: false
    type: str
"""

EXAMPLES = """
- name: add ip to access list
  pn_access_list_ip:
    pn_cliswitch: "192.168.1.1".
    pn_name: "foo"
    pn_ip: "172.16.3.1"
    state: "present"

- name: remove ip to access list
  pn_access_list_ip:
    pn_cliswitch: "192.168.1.1".
    pn_name: "foo"
    pn_ip: "172.16.3.1"
    state: "absent"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the access-list-ip command.
  returned: always
  type: list
stderr:
  description: set of error responses from the access-list-ip command.
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

    # 'out' contains the output
    # 'err' contains the error messages
    result, out, err = module.run_command(cmd)

    print_cli = cli.split(cliswitch)[0]

    # Response in JSON format
    if result != 0:
        module.exit_json(
            command=print_cli,
            stderr=err.strip(),
            msg="%s operation failed" % command,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="%s operation completed" % command,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="%s operation completed" % command,
            changed=True
        )


def check_cli(module, cli):
    """
    This method checks for idempotency using the snmp-user-show command.
    If a user with given name exists, return USER_EXISTS as True else False.
    :param module: The Ansible module to fetch input parameters
    :param cli: The CLI string
    :return Global Booleans: USER_EXISTS
    """
    name = module.params['pn_name']
    ip = module.params['pn_ip']

    show = cli + \
        ' access-list-ip-show name %s format ip no-show-headers' % name
    show = shlex.split(show)
    out = module.run_command(show)[1]

    out = out.split()
    # Global flags
    global IP_EXISTS

    IP_EXISTS = True if ip in out else False


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'present':
        command = 'access-list-ip-add'
    if state == 'absent':
        command = 'access-list-ip-remove'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent']),
            pn_ip=dict(required=False, type='str'),
            pn_name=dict(required=False, type='str'),
        ),
        required_together=[['pn_name', 'pn_ip']],
    )

    # Accessing the arguments
    state = module.params['state']
    ip = module.params['pn_ip']
    name = module.params['pn_name']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'access-list-ip-remove':
        check_cli(module, cli)
        if IP_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='access-list with ip %s does not exist' % ip
            )
        cli += ' %s name %s ip %s ' % (command, name, ip)
    else:
        if command == 'access-list-ip-add':
            check_cli(module, cli)
            if IP_EXISTS is True:
                module.exit_json(
                     skipped=True,
                     msg='access list with ip %s already exists' % ip
                )
        cli += ' %s name %s ip %s ' % (command, name, ip)

    run_cli(module, cli)


if __name__ == '__main__':
    main()
