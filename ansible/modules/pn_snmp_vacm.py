#!/usr/bin/python
""" PN CLI snmp-vacm-create/modify/delete """
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
module: pn_snmp_vacm
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/modify/delete snmp-vacm.
description:
  - C(create): create View Access Control Models (VACM)
  - C(modify): modify View Access Control Models (VACM)
  - C(delete): delete View Access Control Models (VACM)
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
  state:
    description:
      - State the action to perform. Use 'present' to create snmp-vacm and
        'absent' to delete snmp-vacm and 'update' to modify snmp-vacm.
    required: True
  pn_oid_restrict:
    description:
      - restrict OID
    type: str
  pn_priv:
    description:
      - privileges
  pn_auth:
    description:
      - authentication required
  pn_user_type:
    description:
      - SNMP user type
    choices: ['rouser', 'rwuser']
  pn_user_name:
    description:
      - SNMP administrator name
    type: str
"""

EXAMPLES = """
- name: snmp vacm functionality
  pn_snmp_vacm:
    pn_cliswitch: "192.168.1.1"
    state: "present"
    pn_user_name: "VINETro"
    pn_auth: True
    pn_priv: True
    pn_user_type: "rouser"

- name: snmp vacm functionality
  pn_snmp_vacm:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_user_name: "VINETro"
    pn_auth: True
    pn_priv: True
    pn_user_type: "rwuser"

- name: snmp vacm functionality
  pn_snmp_vacm:
    pn_cliswitch: "192.168.1.1"
    state: "absent"
    pn_user_name: "VINETro"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the snmp-vacm command.
  returned: always
  type: list
stderr:
  description: set of error responses from the snmp-vacm command.
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
            msg="snmp-vacm %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="snmp-vacm %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="snmp-vacm %s operation completed" % cmd,
            changed=True
        )


def check_cli(module, cli):
    """
    This method checks for idempotency using the snmp-vacm-show command.
    If a user with given name exists, return USER_EXISTS as True else False.
    :param module: The Ansible module to fetch input parameters
    :param cli: The CLI string
    :return Global Booleans: USER_EXISTS
    """
    user_name = module.params['pn_user_name']

    show = cli + \
        ' snmp-vacm-show format user-name no-show-headers'
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
        command = 'snmp-vacm-create'
    if state == 'absent':
        command = 'snmp-vacm-delete'
    if state == 'update':
        command = 'snmp-vacm-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent', 'update']),
            pn_oid_restrict=dict(required=False, type='str'),
            pn_priv=dict(required=False, type='bool'),
            pn_auth=dict(required=False, type='bool'),
            pn_user_type=dict(required=False, type='str',
                              choices=['rouser', 'rwuser']),
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
    oid_restrict = module.params['pn_oid_restrict']
    priv = module.params['pn_priv']
    auth = module.params['pn_auth']
    user_type = module.params['pn_user_type']
    user_name = module.params['pn_user_name']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'snmp-vacm-delete':
        check_cli(module, cli)
        if USER_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='snmp-vacm with name %s does not exist' % user_name
            )

        cli += ' %s user-name %s ' % (command, user_name)

    else:
        if command == 'snmp-vacm-create':
            check_cli(module, cli)
            if USER_EXISTS is True:
                module.exit_json(
                    skipped=True,
                    msg='snmp vacm with name %s already exists' % user_name
                )

        cli += ' %s user-name %s ' % (command, user_name)

        if oid_restrict:
            cli += ' oid-restrict ' + oid_restrict
        if priv:
            if priv is True:
                cli += ' priv '
            else:
                cli += ' no-priv '
        if auth:
            if auth is True:
                cli += ' auth '
            else:
                cli += ' no-auth '
        if user_type:
            cli += ' user-type ' + user_type

    run_cli(module, cli)


if __name__ == '__main__':
    main()
