#!/usr/bin/python
""" PN CLI dhcp-filter-create/modify/delete """

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
module: pn_dhcp_filter
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/modify/delete dhcp-filter.
description:
  - C(create): creates a new DHCP filter config
  - C(modify): modify a DHCP filter config
  - C(delete): deletes a DHCP filter config
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'present' to create dhcp-filter and
        'absent' to delete dhcp-filter 'update' to modify the dhcp-filter.
    required: True
  pn_trusted_ports:
    description:
      - trusted ports
    required: false
    type: str
  pn_name:
    description:
      - name of the DHCP filter
    required: false
    type: str
"""

EXAMPLES = """
- name: dhcp filter create
  pn_dhcp_filter:
    pn_cliswitch: "192.168.1.1"
    pn_name: "foo"
    state: "present"
    pn_trusted_ports: "1"

- name: dhcp filter delete
  pn_dhcp_filter:
    pn_cliswitch: "192.168.1.1"
    pn_name: "foo"
    state: "absent"
    pn_trusted_ports: "1"

- name: dhcp filter modify
  pn_dhcp_filter:
    pn_cliswitch: "192.168.1.1"
    pn_name: "foo"
    state: "update"
    pn_trusted_ports: "1,2"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the dhcp-filter command.
  returned: always
  type: list
stderr:
  description: set of error responses from the dhcp-filter command.
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
            msg="dhcp-filter %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="dhcp-filter %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="dhcp-filter %s operation completed" % cmd,
            changed=True
        )


def check_cli(module, cli):
    """
    This method checks for idempotency using the dhcp-filter-show command.
    If a user with given name exists, return USER_EXISTS as True else False.
    :param module: The Ansible module to fetch input parameters
    :param cli: The CLI string
    :return Global Booleans: USER_EXISTS
    """
    user_name = module.params['pn_name']

    show = cli + \
        ' dhcp-filter-show format name no-show-headers'
    show = shlex.split(show)
    out = module.run_command(show)[1]

    out = out.split()
    # Global flags
    global USER_EXISTS

    USER_EXISTS = True if user_name in out else False


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'present':
        command = 'dhcp-filter-create'
    if state == 'absent':
        command = 'dhcp-filter-delete'
    if state == 'update':
        command = 'dhcp-filter-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent', 'update']),
            pn_trusted_ports=dict(required=False, type='str'),
            pn_name=dict(required=False, type='str'),
        ),
        required_if=[
            ["state", "present", ["pn_name", "pn_trusted_ports"]],
            ["state", "absent", ["pn_name"]],
            ["state", "update", ["pn_name", "pn_trusted_ports"]]
        ]
    )

    # Accessing the arguments
    state = module.params['state']
    trusted_ports = module.params['pn_trusted_ports']
    name = module.params['pn_name']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'dhcp-filter-delete':
        check_cli(module, cli)
        if USER_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='dhcp-filter with name %s does not exist' % name
            )
        cli += ' %s name %s ' % (command, name)
    else:
        if command == 'dhcp-filter-create':
            check_cli(module, cli)
            if USER_EXISTS is True:
                module.exit_json(
                     skipped=True,
                     msg='dhcp-filterwith name %s already exists' % name
                )
        cli += ' %s name %s ' % (command, name)
        if trusted_ports:
            cli += ' trusted-ports ' + trusted_ports

    run_cli(module, cli)


if __name__ == '__main__':
    main()
