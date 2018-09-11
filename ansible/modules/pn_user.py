#!/usr/bin/python
""" PN CLI user-create/modify/delete """
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: pn_user
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/modify/delete user.
description:
  - C(create): create a user and apply a role
  - C(modify): update a user
  - C(delete): delete a user
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
  state:
    description:
      - State the action to perform. Use 'present' to create user and
        'absent' to delete user 'update' to update user.
    required: True
  pn_scope:
    description:
      - local or fabric
    choices: ['local', 'fabric']
  pn_initial_role:
    description:
      - initial role for user
    type: str
  pn_password:
    description:
      - plain text password
    type: str
  pn_name:
    description:
      - username
    type: str
"""

EXAMPLES = """
- name: "Configure user"
  pn_user:
    state: "present"
    pn_scope: "fabric"
    pn_initial_role: "network-admin"
    pn_password: "test123"
    pn_name: "enss"

- name: "Configure user"
  pn_user:
    state: "absent"
    pn_name: "enss"

- name: "Configure user"
  pn_user:
    state: "update"
    pn_password: "test1234"
    pn_name: "enss"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the user command.
  returned: always
  type: list
stderr:
  description: set of error responses from the user command.
  returned: on error
  type: list
changed:
  description: indicates whether the CLI caused changes on the target.
  returned: always
  type: bool
"""


import shlex

# AnsibleModule boilerplate
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

    print_cli = cli.split(cliswitch)[1]

    # Response in JSON format
    if result != 0:
        module.exit_json(
            command=print_cli,
            stderr=err.strip(),
            msg="user %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="user %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="user %s operation completed" % cmd,
            changed=True
        )


def check_cli(module, cli):
    """
    This method checks for idempotency using the user-show command.
    If a user already exists on the given switch, return USER_EXISTS as
    True else False.
    :param module: The Ansible module to fetch input parameters
    :param cli: The CLI string
    :return Global Booleans: USER_EXISTS.
    """
    name = module.params['pn_name']
    # Global flags
    global USER_EXISTS

    show = cli + \
        ' user-show format name no-show-headers'
    show = shlex.split(show)
    out = module.run_command(show)[1]

    out = out.split()
    # Global flags
    global USER_EXISTS

    USER_EXISTS = True if name in out else False


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'present':
        command = 'user-create'
    if state == 'absent':
        command = 'user-delete'
    if state == 'update':
        command = 'user-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent', 'update']),
            pn_scope=dict(required=False, type='str',
                          choices=['local', 'fabric']),
            pn_initial_role=dict(required=False, type='str'),
            pn_password=dict(required=False, type='str', no_log=True),
            pn_name=dict(required=False, type='str'),
        ),
        required_if=(
            ["state", "present", ["pn_name"]],
            ["state", "absent", ["pn_name"]],
            ["state", "update", ["pn_name", "pn_password"]]
            )
        )

    # Accessing the arguments
    state = module.params['state']
    scope = module.params['pn_scope']
    initial_role = module.params['pn_initial_role']
    password = module.params['pn_password']
    name = module.params['pn_name']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'user-delete':
        check_cli(module, cli)
        if USER_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='user with name %s does not exist' % name
            )
        cli += ' %s name %s ' % (command, name)
    else:
        if command == 'user-create':
            check_cli(module, cli)
            if USER_EXISTS is True:
                module.exit_json(
                     skipped=True,
                     msg='User with name %s already exists' % name
                )
        cli += ' %s name %s ' % (command, name)

        if scope:
            cli += ' scope ' + scope
        if initial_role:
            cli += ' initial-role ' + initial_role
        if password:
            cli += ' password ' + password
    run_cli(module, cli)


if __name__ == '__main__':
    main()
