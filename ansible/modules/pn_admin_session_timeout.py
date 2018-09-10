#!/usr/bin/python
""" PN CLI admin-session-timeout-modify """

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
module: pn_admin_session_timeout
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to modify admin-session-timeout.
description:
  - C(modify): Modify login session timeout
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform.
        'update' to modify the admin-session-timeout.
    required: True
  pn_action:
    description:
      - admin-session-timeout configuration command.
    required: true
    choices: ['modify']
    type: str
  pn_timeout:
    description:
      - Maximum time to wait for user activity before
        terminating login session. Minimum should be 60s.
    required: false
    type: str
"""

EXAMPLES = """
- name: admin session timeout functionality
  pn_admin_session_timeout.py:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_timeout: "61s"

- name: admin session timeout functionality
  pn_admin_session_timeout.py:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_timeout: "1d"

- name: admin session timeout functionality
  pn_admin_session_timeout.py:
    pn_cliswitch: "192.168.1.1"
    state: "update"
    pn_timeout: "10d20m3h15s"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the admin-session-timeout command.
  returned: always
  type: list
stderr:
  description: set of error responses from the admin-session-timeout command.
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


def get_command_from_state(state):
    """
    This method gets appropriate command name for the state specified. It
    returns the command name for the specified state.
    :param state: The state for which the respective command name is required.
    """
    command = None
    if state == 'update':
        command = 'admin-session-timeout-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['update']),
            pn_timeout=dict(required=False, type='str'),
        ),
        required_together=[['state', 'pn_timeout']],
    )

    # Accessing the arguments
    state = module.params['state']
    timeout = module.params['pn_timeout']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)
    if command == 'admin-session-timeout-modify':
        cli += '%s ' % command
        if timeout:
            cli += ' timeout ' + timeout

    run_cli(module, cli)


if __name__ == '__main__':
    main()
