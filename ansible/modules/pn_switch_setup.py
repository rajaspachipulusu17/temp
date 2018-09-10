#!/usr/bin/python
""" PN CLI switch-setup-modify """

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
module: pn_switch_setup
author: "Pluribus Networks (devops@pluribusnetworks.com)"
version_added: "2.7"
short_description: CLI command to modify switch-setup.
description:
  - C(modify): modify switch setup
options:
  pn_cliswitch:
    description:
      - Target switch to run the CLI on.
    required: False
    type: str
  state:
    description:
      - State the action to perform. Use 'update' to modify the switch-setup.
    required: True
  pn_force:
    description:
      - force analytics-store change even if it involves removing data
    required: false
    type: bool
  pn_dns_ip:
    description:
      - DNS IP address
    required: false
    type: str
  pn_mgmt_netmask:
    description:
      - netmask
    required: false
    type: str
  pn_gateway_ip6:
    description:
      - gateway IPv6 address
    required: false
    type: str
  pn_in_band_ip6_assign:
    description:
      - data IPv6 address assignment
    required: false
    choices: ['none', 'autoconf']
  pn_domain_name:
    description:
      - domain name
    required: false
    type: str
  pn_timezone:
    description:
      - timezone
    required: false
    type: str
  pn_in_band_netmask:
    description:
      - data in-band netmask
    required: false
    type: str
  pn_in_band_ip6:
    description:
      - data in-band IPv6 address
    required: false
    type: str
  pn_in_band_netmask_ip6:
    description:
      - data in-band IPv6 netmask
    required: false
    type: str
  pn_motd:
    description:
      - Message of the Day
    required: false
    type: str
  pn_loopback_ip6:
    description:
      - loopback IPv6 address
    required: false
    type: str
  pn_mgmt_ip6_assignment:
    description:
      - IPv6 address assignment
    required: false
    choices: ['none', 'autoconf']
  pn_ntp_secondary_server:
    description:
      - Secondary NTP server
    required: false
    type: str
  pn_in_band_ip:
    description:
      - data in-band IP address
    required: false
    type: str
  pn_eula_accepted:
    description:
      - accept EULA
    required: false
    choices: ['true', 'false']
  pn_mgmt_ip:
    description:
      - management IP address
    required: false
    type: str
  pn_ntp_server:
    description:
      - NTP server
    required: false
    type: str
  pn_mgmt_ip_assignment:
    description:
      - IP address assignment
    required: false
    choices: ['none', 'dhcp']
  pn_date:
    description:
      - date
    required: false
    type: str
  pn_password:
    description:
      - plain text password
    required: false
    type: str
  pn_banner:
    description:
      - Banner to display on server-switch
    required: false
    type: str
  pn_loopback_ip:
    description:
      - loopback IPv4 address
    required: false
    type: str
  pn_dns_secondary_ip:
    description:
      - secondary DNS IP address
    required: false
    type: str
  pn_switch_name:
    description:
      - switch name
    required: false
    type: str
  pn_eula_timestamp:
    description:
      - EULA timestamp
    required: false
    type: str
  pn_mgmt_netmask_ip6:
    description:
      - IPv6 netmask
    required: false
    type: str
  pn_enable_host_ports:
    description:
      - Enable host ports by default
    required: false
    type: bool
  pn_mgmt_ip6:
    description:
      - IPv6 address
    required: false
    type: str
  pn_analytics_store:
    description:
      - type of disk storage for analytics
    required: false
    choices: ['default', 'optimized']
  pn_gateway_ip:
    description:
      - gateway IPv4 address
    required: false
    type: str
"""

EXAMPLES = """
- name: Modify switch banner
  pn_switch_setup:
    state: "update"
    pn_timezone: "America/New_York"
    pn_in_band_ip: "20.20.1.1"
    pn_in_band_netmask: "24"

- name: Modify switch banner
  pn_switch_setup:
    state: "update"
    pn_timezone: "America/New_York"
    pn_in_band_ip6: "2001:0db8:85a3::8a2e:0370:7334"
    pn_in_band_netmask_ip6: "127"
"""

RETURN = """
command:
  description: the CLI command run on the target node.
stdout:
  description: set of responses from the switch-setup command.
  returned: always
  type: list
stderr:
  description: set of error responses from the switch-setup command.
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
            msg="switch-setup %s operation failed" % cmd,
            changed=False
        )

    if out:
        module.exit_json(
            command=print_cli,
            stdout=out.strip(),
            msg="switch-setup %s operation completed" % cmd,
            changed=True
        )

    else:
        module.exit_json(
            command=print_cli,
            msg="switch-setup %s operation completed" % cmd,
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
        command = 'switch-setup-modify'
    return command


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliswitch=dict(required=False, type='str'),
            state=dict(required=True, type='str',
                       choices=['update']),
            pn_force=dict(required=False, type='bool'),
            pn_dns_ip=dict(required=False, type='str'),
            pn_mgmt_netmask=dict(required=False, type='str'),
            pn_gateway_ip6=dict(required=False, type='str'),
            pn_in_band_ip6_assign=dict(required=False, type='str',
                                       choices=['none', 'autoconf']),
            pn_domain_name=dict(required=False, type='str'),
            pn_timezone=dict(required=False, type='str'),
            pn_in_band_netmask=dict(required=False, type='str'),
            pn_in_band_ip6=dict(required=False, type='str'),
            pn_in_band_netmask_ip6=dict(required=False, type='str'),
            pn_motd=dict(required=False, type='str'),
            pn_loopback_ip6=dict(required=False, type='str'),
            pn_mgmt_ip6_assignment=dict(required=False, type='str',
                                        choices=['none', 'autoconf']),
            pn_ntp_secondary_server=dict(required=False, type='str'),
            pn_in_band_ip=dict(required=False, type='str'),
            pn_eula_accepted=dict(required=False, type='str',
                                  choices=['true', 'false']),
            pn_mgmt_ip=dict(required=False, type='str'),
            pn_ntp_server=dict(required=False, type='str'),
            pn_mgmt_ip_assignment=dict(required=False, type='str',
                                       choices=['none', 'dhcp']),
            pn_date=dict(required=False, type='str'),
            pn_password=dict(required=False, type='str', no_log=True),
            pn_banner=dict(required=False, type='str'),
            pn_loopback_ip=dict(required=False, type='str'),
            pn_dns_secondary_ip=dict(required=False, type='str'),
            pn_switch_name=dict(required=False, type='str'),
            pn_eula_timestamp=dict(required=False, type='str'),
            pn_mgmt_netmask_ip6=dict(required=False, type='str'),
            pn_enable_host_ports=dict(required=False, type='bool'),
            pn_mgmt_ip6=dict(required=False, type='str'),
            pn_analytics_store=dict(required=False, type='str',
                                    choices=['default', 'optimized']),
            pn_gateway_ip=dict(required=False, type='str'),
        ),
        required_one_of=[['pn_force', 'pn_dns_ip', 'pn_mgmt_netmask',
                          'pn_gateway_ip6', 'pn_in_band_ip6_assign',
                          'pn_domain_name', 'pn_timezone',
                          'pn_in_band_netmask', 'pn_in_band_ip6',
                          'pn_in_band_netmask_ip6', 'pn_motd',
                          'pn_loopback_ip6', 'pn_mgmt_ip6_assignment',
                          'pn_ntp_secondary_server', 'pn_in_band_ip',
                          'pn_eula_accepted', 'pn_mgmt_ip',
                          'pn_ntp_server', 'pn_mgmt_ip_assignment',
                          'pn_date', 'pn_password',
                          'pn_banner', 'pn_loopback_ip',
                          'pn_dns_secondary_ip', 'pn_switch_name',
                          'pn_eula_timestamp', 'pn_mgmt_netmask_ip6',
                          'pn_enable_host_ports', 'pn_mgmt_ip6',
                          'pn_analytics_store', 'pn_gateway_ip']]
    )

    # Accessing the arguments
    state = module.params['state']
    force = module.params['pn_force']
    dns_ip = module.params['pn_dns_ip']
    mgmt_netmask = module.params['pn_mgmt_netmask']
    gateway_ip6 = module.params['pn_gateway_ip6']
    in_band_ip6_assign = module.params['pn_in_band_ip6_assign']
    domain_name = module.params['pn_domain_name']
    timezone = module.params['pn_timezone']
    in_band_netmask = module.params['pn_in_band_netmask']
    in_band_ip6 = module.params['pn_in_band_ip6']
    in_band_netmask_ip6 = module.params['pn_in_band_netmask_ip6']
    motd = module.params['pn_motd']
    loopback_ip6 = module.params['pn_loopback_ip6']
    mgmt_ip6_assignment = module.params['pn_mgmt_ip6_assignment']
    ntp_secondary_server = module.params['pn_ntp_secondary_server']
    in_band_ip = module.params['pn_in_band_ip']
    eula_accepted = module.params['pn_eula_accepted']
    mgmt_ip = module.params['pn_mgmt_ip']
    ntp_server = module.params['pn_ntp_server']
    mgmt_ip_assignment = module.params['pn_mgmt_ip_assignment']
    date = module.params['pn_date']
    password = module.params['pn_password']
    banner = module.params['pn_banner']
    loopback_ip = module.params['pn_loopback_ip']
    dns_secondary_ip = module.params['pn_dns_secondary_ip']
    switch_name = module.params['pn_switch_name']
    eula_timestamp = module.params['pn_eula_timestamp']
    mgmt_netmask_ip6 = module.params['pn_mgmt_netmask_ip6']
    enable_host_ports = module.params['pn_enable_host_ports']
    mgmt_ip6 = module.params['pn_mgmt_ip6']
    analytics_store = module.params['pn_analytics_store']
    gateway_ip = module.params['pn_gateway_ip']

    command = get_command_from_state(state)

    # Building the CLI command string
    cli = pn_cli(module)

    if command == 'switch-setup-modify':
        cli += ' %s ' % command
        if force:
            if force is True:
                cli += ' force '
            else:
                cli += ' no-force '
        if dns_ip:
            cli += ' dns-ip ' + dns_ip
        if mgmt_netmask:
            cli += ' mgmt-netmask ' + mgmt_netmask
        if gateway_ip6:
            cli += ' gateway-ip6 ' + gateway_ip6
        if in_band_ip6_assign:
            cli += ' in-band-ip6-assign ' + in_band_ip6_assign
        if domain_name:
            cli += ' domain-name ' + domain_name
        if timezone:
            cli += ' timezone ' + timezone
        if in_band_netmask:
            cli += ' in-band-netmask ' + in_band_netmask
        if in_band_ip6:
            cli += ' in-band-ip6 ' + in_band_ip6
        if in_band_netmask_ip6:
            cli += ' in-band-netmask-ip6 ' + in_band_netmask_ip6
        if motd:
            cli += ' motd ' + motd
        if loopback_ip6:
            cli += ' loopback-ip6 ' + loopback_ip6
        if mgmt_ip6_assignment:
            cli += ' mgmt-ip6-assignment ' + mgmt_ip6_assignment
        if ntp_secondary_server:
            cli += ' ntp-secondary-server ' + ntp_secondary_server
        if in_band_ip:
            cli += ' in-band-ip ' + in_band_ip
        if eula_accepted:
            cli += ' eula-accepted ' + eula_accepted
        if mgmt_ip:
            cli += ' mgmt-ip ' + mgmt_ip
        if ntp_server:
            cli += ' ntp-server ' + ntp_server
        if mgmt_ip_assignment:
            cli += ' mgmt-ip-assignment ' + mgmt_ip_assignment
        if date:
            cli += ' date ' + date
        if password:
            cli += ' password ' + password
        if banner:
            cli += ' banner ' + banner
        if loopback_ip:
            cli += ' loopback-ip ' + loopback_ip
        if dns_secondary_ip:
            cli += ' dns-secondary-ip ' + dns_secondary_ip
        if switch_name:
            cli += ' switch-name ' + switch_name
        if eula_timestamp:
            cli += ' eula_timestamp ' + eula_timestamp
        if mgmt_netmask_ip6:
            cli += ' mgmt-netmask-ip6 ' + mgmt_netmask_ip6
        if enable_host_ports:
            if enable_host_ports is True:
                cli += ' enable-host-ports '
            else:
                cli += ' disable-host-ports '
        if mgmt_ip6:
            cli += ' mgmt-ip6 ' + mgmt_ip6
        if analytics_store:
            cli += ' analytics-store ' + analytics_store
        if gateway_ip:
            cli += ' gateway-ip ' + gateway_ip

    run_cli(module, cli)


if __name__ == '__main__':
    main()
