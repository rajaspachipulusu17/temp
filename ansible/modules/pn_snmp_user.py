#!/usr/bin/python
""" PN CLI snmp-user-create/modify/delete """
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
module: pn_snmp_user
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/modify/delete snmp-user.
description:
  - C(create): create SNMPv3 users
  - C(modify): modify SNMPv3 users
  - C(delete): delete SNMPv3 users
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
  state:
    description:
      - State the action to perform. Use 'present' to create snmp-user and
        'absent' to delete snmp-user 'update' to modify the user.
    required: True
  pn_auth_password:
    description:
      - authentication password
    type: str
  pn_priv_password:
    description:
      - privilege password
    type: str
  pn_auth_hash:
    description:
      - Hashing algorithm for authentication
    choices: ['md5', 'sha']
  pn_auth:
    description:
      - authentication required
  pn_priv:
    description:
      - privileges
  pn_user_name:
    description:
      - SNMP user name
    type: str
"""

EXAMPLES = """
- name: snmp-user functionality
  pn_snmp_user:
    pn_cliswitch: "192.168.1.1"
    state: 'absent'
    pn_user_name: "VINETro"
    pn_auth: True
    pn_priv: True
    pn_auth_password: "baseball"
    pn_priv_password: "baseball"

- name: snmp-user functionality
  pn_snmp_user:
    pn_cliswitch: "192.168.1.1"
    state: 'absent'
    pn_user_name: "VINETro"

- name: snmp-user functionality
  pn_snmp_user:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_user_name: "VINETro"
    pn_auth: True
    pn_priv: True
    pn_auth_password: "baseball"
    pn_priv_password: "bassball"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the snmp-user command.
  returned: always
  type: list
stderr:
  description: set of error responses from the snmp-user command.
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

    print_cli = cli.split(cliswitch)[0]

    # Response in JSON format
    if result != 0:
        module.exit_json(
            command=print_cli,
            stderr=err.strip(),
            msg="snmp-user %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="snmp-user %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="snmp-user %s operation completed" % cmd,
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
    user_name = module.params['pn_user_name']

    show = cli + \
        ' snmp-user-show format user-name no-show-headers'
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
        command = 'snmp-user-create'
    if state == 'absent':
        command = 'snmp-user-delete'
    if state == 'update':
        command = 'snmp-user-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent', 'update']),
            pn_auth_password=dict(required=False, type='str', no_log=True),
            pn_priv_password=dict(required=False, type='str', no_log=True),
            pn_auth_hash=dict(required=False, type='str',
                              choices=['md5', 'sha']),
            pn_auth=dict(required=False, type='bool', no_log=True),
            pn_priv=dict(required=False, type='bool', no_log=True),
            pn_user_name=dict(required=False, type='str'),
        ),
        required_if=(
            ["state", "present", ["pn_user_name"]],
            ["state", "absent", ["pn_user_name"]],
            ["state", "update", ["pn_user_name"]]
        )
    )

    # Accessing the arguments
    state = module.params['state']
    auth_password = module.params['pn_auth_password']
    priv_password = module.params['pn_priv_password']
    auth_hash = module.params['pn_auth_hash']
    auth = module.params['pn_auth']
    priv = module.params['pn_priv']
    user_name = module.params['pn_user_name']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'snmp-user-delete':
        check_cli(module, cli)
        if USER_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='snmp-user with name %s does not exist' % user_name
            )
        cli += ' %s user-name %s ' % (command, user_name)
    else:
        if command == 'snmp-user-create':
            check_cli(module, cli)
            if USER_EXISTS is True:
                module.exit_json(
                     skipped=True,
                     msg='snmp user with name %s already exists' % user_name
                )
        cli += ' %s user-name %s ' % (command, user_name)
        if auth_password:
            cli += ' auth-password ' + auth_password
        if priv_password:
            cli += ' priv-password ' + priv_password
        if auth_hash:
            cli += ' auth-hash ' + auth_hash
        if auth:
            if auth is True:
                cli += ' auth '
            else:
                cli += ' no-auth '
        if priv:
            if priv is True:
                cli += ' priv '
            else:
                cli += ' no-priv '

    run_cli(module, cli)


if __name__ == '__main__':
    main()
