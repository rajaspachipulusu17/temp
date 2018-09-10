#!/usr/bin/python
""" PN CLI stp-modify """
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
module: pn_stp
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to modify stp.
description:
  - C(modify): modify Spanning Tree Protocol parameters
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
  state:
    description:
      - State the action to perform. Use 'update' to stp.
    required: True
  pn_hello_time:
    description:
      - STP hello time between 1 and 10 secs - default 2
    type: str
  pn_enable:
    description:
      - enable or disable STP
  pn_root_guard_wait_time:
    description:
      - root guard wait time between 0 and 300 secs.
        Default 20, 0 to disable wait
    type: str
  pn_bpdus_bridge_ports:
    description:
      - BPDU packets to bridge specific port
  pn_mst_max_hops:
    description:
      - maximum hop count for mstp bpdu - default 20
    type: str
  pn_bridge_id:
    description:
      - STP bridge id
    type: str
  pn_max_age:
    description:
      - maximum age time between 6 and 40 secs - default 20
    type: str
  pn_stp_mode:
    description:
      - STP mode
    choices: ['rstp', 'mstp']
  pn_mst_config_name:
    description:
      - Name for MST Configuration Instance
    type: str
  pn_forwarding_delay:
    description:
      - STP forwarding delay between 4 and 30 secs - default 15
    type: str
  pn_bridge_priority:
    description:
      - STP bridge priority - default value of 32768
    type: str
"""

EXAMPLES = """
- name: Modify stp
  pn_stp:
    state: "update"
    pn_hello_time: "3"
    pn_stp_mode: "rstp"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the stp command.
  returned: always
  type: list
stderr:
  description: set of error responses from the stp command.
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
            msg="stp %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="stp %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="stp %s operation completed" % cmd,
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
        command = 'stp-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['update']),
            pn_hello_time=dict(required=False, type='str'),
            pn_enable=dict(required=False, type='bool'),
            pn_root_guard_wait_time=dict(required=False, type='str'),
            pn_bpdus_bridge_ports=dict(required=False, type='bool'),
            pn_mst_max_hops=dict(required=False, type='str'),
            pn_bridge_id=dict(required=False, type='str'),
            pn_max_age=dict(required=False, type='str'),
            pn_stp_mode=dict(required=False, type='str',
                             choices=['rstp', 'mstp']),
            pn_mst_config_name=dict(required=False, type='str'),
            pn_forwarding_delay=dict(required=False, type='str'),
            pn_bridge_priority=dict(required=False, type='str'),
        ),
        required_one_of=[['pn_enable', 'pn_hello_time',
                          'pn_root_guard_wait_time',
                          'pn_bpdus_bridge_ports',
                          'pn_mst_max_hops',
                          'pn_bridge_id',
                          'pn_max_age',
                          'pn_stp_mode',
                          'pn_mst_config_name',
                          'pn_forwarding_delay',
                          'pn_bridge_priority']]
    )

    # Accessing the arguments
    state = module.params['state']
    hello_time = module.params['pn_hello_time']
    enable = module.params['pn_enable']
    root_guard_wait_time = module.params['pn_root_guard_wait_time']
    bpdus_bridge_ports = module.params['pn_bpdus_bridge_ports']
    mst_max_hops = module.params['pn_mst_max_hops']
    bridge_id = module.params['pn_bridge_id']
    max_age = module.params['pn_max_age']
    stp_mode = module.params['pn_stp_mode']
    mst_config_name = module.params['pn_mst_config_name']
    forwarding_delay = module.params['pn_forwarding_delay']
    bridge_priority = module.params['pn_bridge_priority']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'stp-modify':
        cli += ' %s ' % command
        if hello_time:
            cli += ' hello-time ' + hello_time
        if enable:
            if enable is True:
                cli += ' enable '
            else:
                cli += ' disable '
        if root_guard_wait_time:
            cli += ' root-guard-wait-time ' + root_guard_wait_time
        if bpdus_bridge_ports:
            if bpdus_bridge_ports is True:
                cli += ' bpdus-bridge-ports '
            else:
                cli += ' bpdus-all-ports '
        if mst_max_hops:
            cli += ' mst-max-hops ' + mst_max_hops
        if bridge_id:
            cli += ' bridge-id ' + bridge_id
        if max_age:
            cli += ' max-age ' + max_age
        if stp_mode:
            cli += ' stp-mode ' + stp_mode
        if mst_config_name:
            cli += ' mst-config-name ' + mst_config_name
        if forwarding_delay:
            cli += ' forwarding-delay ' + forwarding_delay
        if bridge_priority:
            cli += ' bridge-priority ' + bridge_priority

    run_cli(module, cli)


if __name__ == '__main__':
    main()
