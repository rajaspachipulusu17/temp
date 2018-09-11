#!/usr/bin/python
""" PN CLI snmp-community-create/modify/delete """
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
module: pn_snmp_community
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/modify/delete snmp-community.
description:
  - C(create): create SNMP communities for SNMPv1
  - C(modify): modify SNMP communities for SNMPv1
  - C(delete): delete SNMP communities for SNMPv1
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
  state:
    description:
      - State the action to perform. Use 'present' to create snmp-community and
        'absent' to delete snmp-community 'update' to update snmp-community.
    required: True
  pn_community_type:
    description:
      - community type
    choices: ['read-only', 'read-write']
  pn_community_string:
    description:
      - community name
    type: str
"""

EXAMPLES = """
- name: snmp-community functionality
  pn_snmp_community:
    pn_cliswitch: "192.168.1.1"
    state: "present"
    pn_community_string: "F4u1tMgmt"
    pn_community_type: "read-write"

- name: snmp-community functionality
  pn_snmp_community:
    pn_cliswitch: "192.168.1.1"
    state: "absent"
    pn_community_string: "F4u1tMgmt"
    pn_community_type: "read-write"

- name: snmp-community functionality
  pn_snmp_community:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_community_string: "F4u1tMgmt"
    pn_community_type: "read-only"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the snmp-community command.
  returned: always
  type: list
stderr:
  description: set of error responses from the snmp-community command.
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
            msg="snmp-community %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="snmp-community %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="snmp-community %s operation completed" % cmd,
            changed=True
        )


def check_cli(module, cli):
    """
    This method checks for idempotency using the snmp-community-show command.
    If a user with given name exists, return COMMUNITY_EXISTS
    as True else False.
    :param module: The Ansible module to fetch input parameters
    :param cli: The CLI string
    :return Global Booleans: COMMUNITY_EXISTS
    """
    comm_str = module.params['pn_community_string']

    show = cli + \
        ' snmp-community-show format community-string no-show-headers'
    show = shlex.split(show)
    out = module.run_command(show)[1]

    out = out.split()
    # Global flags
    global COMMUNITY_EXISTS

    COMMUNITY_EXISTS = True if comm_str in out else False


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'present':
        command = 'snmp-community-create'
    if state == 'absent':
        command = 'snmp-community-delete'
    if state == 'update':
        command = 'snmp-community-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent', 'update']),
            pn_community_type=dict(required=False, type='str',
                                   choices=['read-only', 'read-write']),
            pn_community_string=dict(required=False, type='str'),
        )
    )

    # Accessing the arguments
    state = module.params['state']
    community_type = module.params['pn_community_type']
    comm_str = module.params['pn_community_string']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'snmp-community-delete':
        check_cli(module, cli)
        if COMMUNITY_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='snmp community name %s does not exist' % comm_str
            )
        cli += ' %s community-string %s ' % (command, comm_str)
    else:
        if command == 'snmp-community-create':
            check_cli(module, cli)
            if COMMUNITY_EXISTS is True:
                module.exit_json(
                    skipped=True,
                    msg='snmp community with name %s already exists' % comm_str
                )
        cli += ' %s community-string %s ' % (command, comm_str)
        if community_type:
            cli += ' community-type ' + community_type

    run_cli(module, cli)


if __name__ == '__main__':
    main()
