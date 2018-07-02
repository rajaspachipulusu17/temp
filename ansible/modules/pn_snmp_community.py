#!/usr/bin/python
""" PN CLI snmp-community-create/snmp-community-delete/snmp-community-modify """
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

import shlex
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pn_nvos import pn_cli

DOCUMENTATION = """
---
module: pn_snmp_communtiy
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version: 2
short_description: CLI command to create snmp community.
description:
  - SNMP community configuration.
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  pn_action:
    description:
      - snmp-community command.
    required: true
    type: str
  pn_community_string:
    description:
      - snmp-communtiy string name
    required: false
    type: str
  pn_communtiy_type:
    description:
      - snmp-communtiy string type
    required: false
    type: str
    choices=['read-only', 'read-write']
"""

EXAMPLES = """
- name: snmp-community functionality
  pn_snmp_community:
    pn_action: "create"
    pn_community_string: "football"      
    pn_community_type: "read-write"
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


def run_cli(module, cli):
    """
    This method executes the cli command on the target node(s) and returns the
    output. The module then exits based on the output.
    :param cli: the complete cli string to be executed on the target node(s).
    :param module: The Ansible module to fetch command
    """
    action = module.params['pn_action']
    cli = shlex.split(cli)
    rc, out, err = module.run_command(cli)

    # Response in JSON format
    if err:
        module.fail_json(
            command=' '.join(cli),
            stderr=err.strip(),
            msg="snmp-community %s operation failed" % action,
            changed=False
        )

    if out:
        module.exit_json(
            command=' '.join(cli),
            stdout=out.strip(),
            msg="snmp-community %s operation completed" % action,
            changed=True
        )

    else:
        module.exit_json(
            command=' '.join(cli),
            msg="snmp-community %s operation completed" % action,
            changed=True
        )


def check_community(module, community_string):
    """
    This method cchecks for snmp community.
    :param module: The Ansible module to fetch command
    :param community_string: the str name of communtiy string.
    """
    cli = pn_cli(module, module.params['pn_cliswitch'])
    cli += ' snmp-community-show community-string ' + community_string
    cli = shlex.split(cli)
    return module.run_command(cli)[1]


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            pn_action=dict(required=True, type='str',
                           choices=['create', 'delete', 'modify']),
            pn_community_string=dict(required=True, type='str'),
            pn_community_type=dict(required=False, type='str',
                                   choices=['read-only', 'read-write']),
        )
    )

    community_string = module.params['pn_community_string']
    action = module.params['pn_action']
    community_type = module.params['pn_community_type']

    if action == 'create':
        if check_community(module, community_string):
            module.exit_json(
                msg='snmp-community with name %s \
                     already present in the switch' % community_string
            )
    elif action == 'modify' or action == 'delete':
        if not check_community(module, community_string):
            module.fail_json(
                msg='snmp-community with name %s \
                      not present in the switch' % community_string
            )
    else:
        module.fail_json(
            msg='snmp-community action %s not supported \
                 Use create/delete/modify' % action
        )
    cli = pn_cli(module, module.params['pn_cliswitch'])
    cli += ' snmp-community-'+ action + ' community-string ' + community_string
    if community_type and action != 'delete':
        cli += ' community-type ' + community_type

    run_cli(module, cli)

if __name__ == '__main__':
    main()

