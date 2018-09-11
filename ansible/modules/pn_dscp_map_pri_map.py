#!/usr/bin/python
""" PN CLI dscp-map-pri-map-modify """

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
module: pn_dscp_map_pri_map
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to modify dscp-map-pri-map.
description:
  - C(modify): Update priority mappings in tables
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'update' to modify
        the dscp-map-pri-map.
    required: True
  pn_pri:
    description:
      - CoS priority
    required: false
    type: str
  pn_name:
    description:
      - Name for the DSCP map
    required: false
    type: str
  pn_dsmap:
    description:
      - DSCP value(s)
    required: false
    type: str
"""

EXAMPLES = """
- name: dscp map pri map modify
  pn_dscp_map_pri_map:
    pn_cliswitch: '192.168.1.1'
    state: 'update'
    pn_name: 'foo' 
    pn_pri: '0'
    pn_dsmap: '40'

- name: dscp map pri map modify
  pn_dscp_map_pri_map:
    pn_cliswitch: '192.168.1.1'
    state: 'update'
    pn_name: 'foo' 
    pn_pri: '1'
    pn_dsmap: '8,10,12,14'
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the dscp-map-pri-map command.
  returned: always
  type: list
stderr:
  description: set of error responses from the dscp-map-pri-map command.
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
            msg="dscp-map-pri-map %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="dscp-map-pri-map %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="dscp-map-pri-map %s operation completed" % cmd,
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
        command = 'dscp-map-pri-map-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['update']),
            pn_pri=dict(required=False, type='str'),
            pn_name=dict(required=False, type='str'),
            pn_dsmap=dict(required=False, type='str'),
        ),
        required_if=(
            ['state', 'update', ['pn_name', 'pn_pri', 'pn_dsmap']],
        )
    )

    # Accessing the arguments
    state = module.params['state']
    pri = module.params['pn_pri']
    name = module.params['pn_name']
    dsmap = module.params['pn_dsmap']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'dscp-map-pri-map-modify':
        cli += ' %s ' % command
        if pri:
            cli += ' pri ' + pri
        if name:
            cli += ' name ' + name
        if dsmap:
            cli += ' dsmap ' + dsmap

    run_cli(module, cli)


if __name__ == '__main__':
    main()
