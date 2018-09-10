#!/usr/bin/python
""" PN CLI access-list-create/delete """

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
module: pn_access_list
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/delete access-list.
description:
  - C(create): create an access list
  - C(delete): delete an access list
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'present' to create access-list and
        'absent' to delete access-list.
    required: True
  pn_name:
    description:
      - Access List Name
    required: false
    type: str
  pn_scope:
    description:
      - scope - local or fabric
    required: false
    choices: ['local', 'fabric']
"""

EXAMPLES = """
- name: access list functionality
  pn_access_list:
    pn_cliswitch: "192.168.1.1"
    pn_name: "foo"
    pn_scope: "local"
    state: "present"

- name: access list functionality
  pn_access_list:
    pn_cliswitch: "192.168.1.1"
    pn_name: "foo"
    pn_scope: "local"
    state: "absent"

- name: access list functionality
  pn_access_list:
    pn_cliswitch: "192.168.1.1"
    pn_name: "foo"
    pn_scope: "fabric"
    state: "present"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the access-list command.
  returned: always
  type: list
stderr:
  description: set of error responses from the access-list command.
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
    list_name = module.params['pn_name']

    show = cli + \
        ' access-list-show format name no-show-headers'
    show = shlex.split(show)
    out = module.run_command(show)[1]

    out = out.split()
    # Global flags
    global ACC_LIST_EXISTS

    ACC_LIST_EXISTS = True if list_name in out else False


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'present':
        command = 'access-list-create'
    if state == 'absent':
        command = 'access-list-delete'
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
        required_together=[['pn_name', 'pn_scope']],
    )

    # Accessing the arguments
    state = module.params['state']
    list_name = module.params['pn_name']
    scope = module.params['pn_scope']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'access-list-delete':
        check_cli(module, cli)
        if ACC_LIST_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='access-list with name %s does not exist' % list_name
            )
        cli += ' %s name %s ' % (command, list_name)
    else:
        if command == 'access-list-create':
            check_cli(module, cli)
            if ACC_LIST_EXISTS is True:
                module.exit_json(
                     skipped=True,
                     msg='access list with name %s already exists' % list_name
                )
        cli += ' %s name %s ' % (command, list_name)
        cli += ' scope %s ' % scope

    run_cli(module, cli)


if __name__ == '__main__':
    main()
