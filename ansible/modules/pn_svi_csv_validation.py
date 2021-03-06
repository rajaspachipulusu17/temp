#!/usr/bin/python
""" PN SVI CSV Validation """

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

import socket

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: pn_svi_csv_validation
author: 'Pluribus Networks (devops@pluribusnetworks.com)'
description: Module to validate svi configuration csv file.
    Csv file format: interface_ip(with subnet), vlan id
    Csv file should not be empty. This module validates the given csv file.
options:
    pn_svi_data:
      description: String containing svi config data parsed from csv file.
      required: True
      type: str
"""

EXAMPLES = """
- name: Validate svi csv file
  pn_svi_csv_validation:
    pn_svi_data: "{{ lookup('file', '{{ csv_file }}') }}"
"""

RETURN = """
msg:
  description: It contains output of each validation.
  returned: always
  type: str
changed:
  description: Indicates whether the validation caused changes on the target.
  returned: always
  type: bool
unreachable:
  description: Empty string.
  returned: always
  type: bool
failed:
  description: Indicates if csv validation failed or not.
  returned: always
  type: bool
exception:
  description: Empty string.
  returned: always
  type: str
task:
  description: Name of the task getting executed.
  returned: always
  type: str
summary:
  description: Indicates whether csv file is valid or invalid.
  returned: always
  type: str
"""


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_svi_data=dict(required=True, type='str'),
        )
    )

    output = ''
    line_count = 0
    valid_vlans = []
    existing_interface_ip = []

    svi_data = module.params['pn_svi_data'].replace(' ', '')
    if svi_data:
        svi_data_list = svi_data.split('\n')
        for row in svi_data_list:
            row = row.strip()
            line_count += 1

            if not row.strip() or row.startswith('#'):
                # Skip blank lines and comments which starts with '#'
                continue
            else:
                elements = row.split(',')
                if len(elements) == 2:
                    interface_ip = elements[0]
                    vlan_id = elements[1]

                    if not vlan_id or not interface_ip:
                        output += 'Invalid entry at line number {}\n'.format(
                            line_count
                        )
                    else:
                        # INTERFACE IP address validation
                        try:
                            if '/' not in interface_ip:
                                raise socket.error
                            else:
                                address_with_subnet = interface_ip.split('/')
                                address = address_with_subnet[0]
                                subnet = address_with_subnet[1]
                                dot_count = address.count('.')
                                if dot_count != 3 or address in existing_interface_ip:
                                    raise socket.error

                                socket.inet_aton(address)
                                if (not subnet.isdigit() or
                                        int(subnet) not in range(1, 33)):
                                    raise socket.error

                                existing_interface_ip.append(address)
                        except socket.error:
                            output += 'Invalid interface ip {} '.format(interface_ip)
                            output += 'at line number {}. '.format(line_count)
                            output += 'Note: Format of interface_ip -> x.x.x.x/subnet\n'

                        # Vlan ID validation
                        if vlan_id in valid_vlans:
                            output += 'Duplicate vlan {} '.format(vlan_id)
                            output += 'at line number {}\n'.format(line_count)

                        if (not vlan_id.isdigit() or
                                int(vlan_id) not in range(2, 4093)):
                            output += 'Invalid vlan {} '.format(vlan_id)
                            output += 'at line number {}\n'.format(line_count)
                        else:
                            valid_vlans.append(vlan_id)
                else:
                    output += 'Invalid entry at line number {}\n'.format(
                        line_count)
    else:
        output += 'Csv file should not be empty\n'

    if not output:
        msg = 'Valid csv file'
        failed_flag = False
    else:
        msg = 'Invalid csv file'
        failed_flag = True

    module.exit_json(
        unreachable=False,
        msg=output,
        summary=msg,
        exception='',
        failed=failed_flag,
        changed=False,
        task='Validate svi csv file'
    )

if __name__ == '__main__':
    main()
