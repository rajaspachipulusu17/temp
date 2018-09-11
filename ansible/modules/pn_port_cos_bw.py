#!/usr/bin/python
""" PN CLI port-cos-bw-modify """

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
module: pn_port_cos_bw
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to modify port-cos-bw.
description:
  - C(modify): Update b/w settings for CoS queues
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'update' to modify the port-cos-bw.
    required: True
  pn_max_bw_limit:
    description:
      - Maximum b/w in %
    required: false
    type: str
  pn_cos:
    description:
      - CoS priority
    required: false
    type: str
  pn_port:
    description:
      - physical port
    required: false
    type: str
  pn_weight:
    description:
      - Scheduling weight (1 to 127) after b/w guarantee met
    required: false
    choices: ['priority', 'no-priority']
  pn_min_bw_guarantee:
    description:
      - Minimum b/w in %
    required: false
    type: str
"""

EXAMPLES = """
- name: port cos bw modify
  pn_port_cos_bw:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_port: "1"
    pn_cos: "0"
    pn_min_bw_guarantee: "60"

- name: port cos bw modify
  pn_port_cos_bw:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_port: "all"
    pn_cos: "0"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the port-cos-bw command.
  returned: always
  type: list
stderr:
  description: set of error responses from the port-cos-bw command.
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
            msg="port-cos-bw %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="port-cos-bw %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="port-cos-bw %s operation completed" % cmd,
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
        command = 'port-cos-bw-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['update']),
            pn_max_bw_limit=dict(required=False, type='str'),
            pn_cos=dict(required=False, type='str'),
            pn_port=dict(required=False, type='str'),
            pn_weight=dict(required=False, type='str',
                           choices=['priority', 'no-priority']),
            pn_min_bw_guarantee=dict(required=False, type='str'),
        ),
        required_if=(
            ['state', 'update', ['pn_cos', 'pn_port']],
        )
    )

    # Accessing the arguments
    state = module.params['state']
    max_bw_limit = module.params['pn_max_bw_limit']
    cos = module.params['pn_cos']
    port = module.params['pn_port']
    weight = module.params['pn_weight']
    min_bw_guarantee = module.params['pn_min_bw_guarantee']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'port-cos-bw-modify':
        cli += ' %s ' % command
        if max_bw_limit:
            cli += ' max-bw-limit ' + max_bw_limit
        if cos:
            cli += ' cos ' + cos
        if port:
            cli += ' port ' + port
        if weight:
            cli += ' weight ' + weight
        if min_bw_guarantee:
            cli += ' min-bw-guarantee ' + min_bw_guarantee

    run_cli(module, cli)


if __name__ == '__main__':
    main()
