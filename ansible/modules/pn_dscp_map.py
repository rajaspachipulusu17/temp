#!/usr/bin/python
""" PN CLI dscp-map-create/delete """

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
module: pn_dscp_map
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/delete dscp-map.
description:
  - C(create): Create a DSCP priority mapping table
  - C(delete): Delete a DSCP priority mapping table
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'present' to create dscp-map and
        'absent' to delete.
    required: True
  pn_name:
    description:
      - Name for the DSCP map
    required: false
    type: str
  pn_scope:
    description:
      - scope for dscp map
    required: false
    choices: ['local', 'fabric']
"""

EXAMPLES = """
- name: dscp map create
  pn_dscp_map:
    pn_cliswitch: "192.168.1.1"
    state: "present"
    pn_name: "verizon_qos"
    pn_scope: "local"

- name: dscp map delete
  pn_dscp_map:
    pn_cliswitch: "192.168.1.1"
    state: "absent"
    pn_name: "verizon_qos"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the dscp-map command.
  returned: always
  type: list
stderr:
  description: set of error responses from the dscp-map command.
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
            msg="dscp-map %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="dscp-map %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="dscp-map %s operation completed" % cmd,
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
    # Global flags
    global NAME_EXISTS
    name = module.params['pn_name']

    show = cli + \
        ' dscp-map-show name %s format name no-show-headers' % name
    show = shlex.split(show)
    out = module.run_command(show)[1]

    out = out.split()

    NAME_EXISTS = True if name in out else False


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'present':
        command = 'dscp-map-create'
    if state == 'absent':
        command = 'dscp-map-delete'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent']),
            pn_name=dict(required=False, type='str'),
            pn_scope=dict(required=False, type='str',
                          choices=['local', 'fabric']),
        ),
        required_if=(
            ["state", "present", ["pn_name", "pn_scope"]],
            ["state", "absent", ["pn_name"]],
        )
    )

    # Accessing the arguments
    state = module.params['state']
    name = module.params['pn_name']
    scope = module.params['pn_scope']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'dscp-map-delete':
        check_cli(module, cli)
        if NAME_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='dscp map with name %s does not exist' % name
            )
        cli += ' %s name %s ' % (command, name)
    else:
        if command == 'dscp-map-create':
            check_cli(module, cli)
            if NAME_EXISTS is True:
                module.exit_json(
                     skipped=True,
                     msg='dscp map with name %s already exists' % name
                )
        cli += ' %s name %s ' % (command, name)

        if scope:
            cli += ' scope ' + scope

    run_cli(module, cli)


if __name__ == '__main__':
    main()
