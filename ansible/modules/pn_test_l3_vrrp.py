#!/usr/bin/python
""" Tests for L3 VRRP """

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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pn_nvos import pn_cli

import shlex

DOCUMENTATION = """
---
module: pn_test_l3_vrrp
author: "Pluribus Networks (devops@pluribusnetworks.com)"
short_description: Tests for L3 VRRP.
options:
    pn_spine_count:
      description:
        - Number of spine switches.
      required: False
      type: int
    pn_leaf_count:
      description:
        - Number of leaf switches.
      required: False
      type: int
"""

EXAMPLES = """
- name: Test Layer3 VRRP
  pn_test_l3_vrrp:
  pn_spine_count: "{{ spine_count }}"
  pn_leaf_count: "{{ leaf_count }}"
"""

RETURN = """
stdout:
  description: The set of responses for each command.
  returned: always
  type: str
changed:
  description: Indicates whether the CLI caused changes on the target.
  returned: always
  type: bool
failed:
  description: Indicates whether or not the execution failed on the target.
  returned: always
  type: bool
"""


def run_cli(module, cli, find_str, out_msg):
    """
    Method to execute the cli command on the target node(s) and returns the
    output.
    :param module: The Ansible module to fetch input parameters.
    :param cli: the complete cli string to be executed on the target node(s).
    :param find_str: String to search/find in output string.
    :param out_msg: Output string describing command output.
    :return: Success/Fail message depending upon the response from cli.
    """
    cli = shlex.split(cli)
    rc, out, err = module.run_command(cli)

    if out:
        if out.find(find_str) > -1:
            return '%s: Successful\n' % out_msg

    return '%s: Failed\n' % out_msg


def test_vrouter_creation(module):
    """
    Test vrouters creation.
    :param module: The Ansible module to fetch input parameters.
    :return: Output of run_cli() method.
    """
    switch_count = module.params['pn_spine_count'] + module.params[
        'pn_leaf_count']
    find_str = 'Count: ' + str(switch_count)
    cli = pn_cli(module)
    cli += ' vrouter-show count-output '
    return run_cli(module, cli, find_str, 'Vrouters creation')


def test_vrouter_interface_creation(module):
    """
    Test vrouters interface creation.
    :param module: The Ansible module to fetch input parameters.
    :return: Output of run_cli() method.
    """
    cli = pn_cli(module)
    cli += ' vrouter-interface-show count-output '
    return run_cli(module, cli, 'Count:', 'Vrouter interfaces creation')


def test_loopback_interface_addition(module):
    """
    Test loopback interface addition to vrouters.
    :param module: The Ansible module to fetch input parameters.
    :return: Output of run_cli() method.
    """
    switch_count = module.params['pn_spine_count'] + module.params[
        'pn_leaf_count']
    find_str = 'Count: ' + str(switch_count)
    cli = pn_cli(module)
    cli += ' vrouter-loopback-interface-show count-output '
    return run_cli(module, cli, find_str, 'Loopback interface addition')


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_spine_count=dict(required=False, type='int'),
            pn_leaf_count=dict(required=False, type='int'),
        )
    )

    msg = test_vrouter_creation(module)
    msg += test_vrouter_interface_creation(module)
    msg += test_loopback_interface_addition(module)

    module.exit_json(
        stdout=msg,
        changed=False,
    )

if __name__ == '__main__':
    main()
