#!/usr/bin/python
""" PN CLI snmp-trap-sink-create/delete """
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
module: pn_snmp_trap_sink
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to create/delete snmp-trap-sink.
description:
  - C(create): create a SNMP trap sink
  - C(delete): delete a SNMP trap sink
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
  state:
    description:
      - State the action to perform. Use 'present' to create snmp-trap-sink and
        'absent' to delete snmp-trap-sink.
    required: True
  pn_dest_host:
    description:
      - destination host
    type: str
  pn_community:
    description:
      - community type
    type: str
  pn_dest_port:
    description:
      - destination port - default 162
    type: str
  pn_type:
    description:
      - trap type - default TRAP_TYPE_V2C_TRAP
    choices: ['TRAP_TYPE_V1_TRAP', 'TRAP_TYPE_V2C_TRAP', 'TRAP_TYPE_V2_INFORM']
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
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the snmp-trap-sink command.
  returned: always
  type: list
stderr:
  description: set of error responses from the snmp-trap-sink command.
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
            msg="snmp-trap-sink %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="snmp-trap-sink %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="snmp-trap-sink %s operation completed" % cmd,
            changed=True
        )


def check_cli(module, cli):
    """
    This method checks for idempotency using the snmp-trap-sink-show command.
    If a user with given name exists, return TYPE_EXISTS as True else False.
    :param module: The Ansible module to fetch input parameters
    :param cli: The CLI string
    :return Global Booleans: USER_EXISTS
    """
    pn_type = module.params['pn_type']

    show = cli + \
        ' snmp-trap-sink-show format type no-show-headers'
    show = shlex.split(show)
    out = module.run_command(show)[1]

    out = out.split()
    # Global flags
    global TYPE_EXISTS

    TYPE_EXISTS = True if pn_type in out else False


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'present':
        command = 'snmp-trap-sink-create'
    if state == 'absent':
        command = 'snmp-trap-sink-delete'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['present', 'absent']),
            pn_dest_host=dict(required=False, type='str'),
            pn_community=dict(required=False, type='str'),
            pn_dest_port=dict(required=False, type='str', default='162'),
            pn_type=dict(required=True, type='str',
                         choices=['TRAP_TYPE_V1_TRAP',
                                  'TRAP_TYPE_V2C_TRAP',
                                  'TRAP_TYPE_V2_INFORM']),
        )
    )

    # Accessing the arguments
    state = module.params['state']
    dest_host = module.params['pn_dest_host']
    community = module.params['pn_community']
    dest_port = module.params['pn_dest_port']
    pn_type = module.params['pn_type']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'snmp-trap-sink-create':
        check_cli(module, cli)
        if TYPE_EXISTS is True:
            module.exit_json(
                skipped=True,
                msg='snmp trap sink with type %s already exists' % pn_type
            )

        cli += ' %s type %s ' % (command, pn_type)
        if dest_host:
            cli += ' dest-host ' + dest_host
        if community:
            cli += ' community ' + community
        if dest_port:
            cli += ' dest-port ' + dest_port

    if command == 'snmp-trap-sink-delete':
        check_cli(module, cli)
        if TYPE_EXISTS is False:
            module.exit_json(
                skipped=True,
                msg='snmp-trap-sink with type %s does not exist' % pn_type
            )

        cli += ' %s community %s ' % (command, community)
        cli += ' dest-host %s dest-port %s ' % (dest_host, dest_port)

    run_cli(module, cli)


if __name__ == '__main__':
    main()
