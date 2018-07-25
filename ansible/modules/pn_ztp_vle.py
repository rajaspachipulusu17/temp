#!/usr/bin/python
""" PN ZTP VLE """

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
from ansible.module_utils.pn_nvos import *


DOCUMENTATION = """
---
module: pn_ztp_vle
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version: 2
options:
    pn_spine_list:
      description:
        - Specify list of Spine hosts
      required: False
      type: list
    pn_leaf_list:
      description:
        - Specify list of leaf hosts
      required: False
      type: list
    pn_csv_data:
      description:
        - String containing vrrp data parsed from csv file.
      required: True
      type: str
    pn_tracking:
      description:
        - enable/disable tracking between vle ports
      required: false
      type: bool
      default: True
"""

EXAMPLES = """
- name: Configure VLE
  pn_ztp_vle:
    pn_spine_list: "{{ groups['spine'] }}"
    pn_leaf_list: "{{ groups['leaf'] }}"
    pn_csv_data: "{{ lookup('file', '{{ csv_file }}') }}"
"""


RETURN = """
summary:
  description: It contains output of each configuration along with switch name.
  returned: always
  type: str
changed:
  description: Indicates whether the CLI caused changes on the target.
  returned: always
  type: bool
unreachable:
  description: Indicates whether switch was unreachable to connect.
  returned: always
  type: bool
failed:
  description: Indicates whether or not the execution failed on the target.
  returned: always
  type: bool
exception:
  description: Describes error/exception occurred while executing CLI command.
  returned: always
  type: str
task:
  description: Name of the task getting executed on switch.
  returned: always
  type: str
msg:
  description: Indicates whether configuration made was successful or failed.
  returned: always
  type: str
"""

CHANGED_FLAG = []


def run_cli(module, cli):
    """
    Method to execute the cli command on the target node(s) and returns the
    output.
    :param module: The Ansible module to fetch input parameters.
    :param cli: The complete cli string to be executed on the target node(s).
    :return: Output/Error or Success msg depending upon the response from cli.
    """
    cli = shlex.split(cli)
    rc, out, err = module.run_command(cli)
    results = []
    if out:
        return out

    if err:
        json_msg = {
            'switch': '',
            'output': u'Operation Failed: {}'.format(' '.join(cli))
        }
        results.append(json_msg)
        module.exit_json(
            unreachable=False,
            failed=True,
            exception=err.strip(),
            summary=results,
            task='Configure VLE',
            msg='VLE configuration failed',
            changed=False
        )
    else:
        return 'Success'


def vle_create(module, vle_switch1_name, vle_switch1_ports,
               vle_switch2_name, vle_switch2_ports):
    """
    Method to configure vle for switches.
    :param module: The Ansible module to fetch input parameters.
    :param vle_switch1_name: The vle switch name.
    :param vle_switch1_ports: List of switch1 ports.
    :param vle_switch2_name: The vle switch name.
    :param vle_switch2_ports: List of switch1 ports.
    :return: The output of the configuration.
    """

    output = ''
    cli = pn_cli(module)
    clicopy = cli
    vle_name = vle_switch1_name + '-' + vle_switch1_ports + '-' + \
               vle_switch2_name + '-' + vle_switch2_ports
#    _vle_switch1 = vle_switch1_ports.strip().split()
#    node1_ports = ','.join(str(port) for port in _vle_switch1)
#    _vle_switch2 = vle_switch2_ports.strip().split()
#    node2_ports = ','.join(str(port) for port in _vle_switch2)

    cli += 'vle-show format name parsable-delim ,'
    current_vle = run_cli(module, cli).strip().split('\n')
    if 'Success' in current_vle or vle_name not in current_vle:
        cli = clicopy
        cli += 'vle-create name %s ' % vle_name
        cli += 'node-1 %s node-1-port %s ' % (vle_switch1_name, str(vle_switch1_ports))
        cli += 'node-2 %s node-2-port %s ' % (vle_switch2_name, str(vle_switch2_ports))
        if module.params['pn_tracking']:
            cli += 'tracking '
        run_cli(module, cli)
        CHANGED_FLAG.append(True)
        output += '%s: Created vle with ' % vle_switch1_name
        output += '%s switch \n' % vle_switch2_name

    return output


def configure_vle(module, csv_data):
    """
    Method to configure VLE.
    :param module: The Ansible module to fetch input parameters.
    :param csv_data: String containing vle data passed from csv file.
    :return: Output string of configuration.
    """
    output = ''

    csv_data = csv_data.strip()
    csv_data_list = csv_data.split('\n')
    # Parse csv file data and configure VRRP.
    for row in csv_data_list:
        row = row.strip()
        if row.startswith('#'):
            continue
        else:
            elements = row.split(',')
            elements = filter(None, elements)
            switch_list = []
            if len(elements) == 4:
                #vle_name = elements.pop(0).strip()
                vle_switch1_name = elements.pop(0).strip()
                vle_switch1_ports = elements.pop(0).strip()
                if not vle_switch1_ports:
                    output += '%s: Cant have empty ports ' % vle_switch1_name
                    continue
                vle_switch2_name = elements.pop(0).strip()
                vle_switch2_ports = elements.pop(0).strip()
                if not vle_switch2_ports:
                    output += '%s: Cant have empty ports ' % vle_switch2_name
                    continue
                output += vle_create(module, vle_switch1_name,
                                     vle_switch1_ports, vle_switch2_name,
                                     vle_switch2_ports)
            else:
                output += 'Insufficient data in csv file'

    return output


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_spine_list=dict(required=False, type='list', default=[]),
            pn_leaf_list=dict(required=False, type='list', default=[]),
            pn_csv_data=dict(required=True, type='str'),
            pn_tracking=dict(required=False, type='bool',
                             choices=[True, False], default=True)
        )
    )

    global CHANGED_FLAG
    message = ''

    message += configure_vle(module, module.params['pn_csv_data'])


    # Exit the module and return the required JSON.
    message_string = message
    results = []
    switch_list = module.params['pn_spine_list'] + module.params['pn_leaf_list']
    for switch in switch_list:
        replace_string = switch + ': '

        for line in message_string.splitlines():
            if replace_string in line:
                json_msg = {
                    'switch': switch,
                    'output': (line.replace(replace_string, '')).strip()
                }
                results.append(json_msg)

    # Exit the module and return the required JSON.
    module.exit_json(
        unreachable=False,
        task='Configure VLE',
        msg='VLE configuration succeeded',
        summary=results,
        exception='',
        failed=False,
        changed=True if True in CHANGED_FLAG else False
    )

if __name__ == '__main__':
    main()
