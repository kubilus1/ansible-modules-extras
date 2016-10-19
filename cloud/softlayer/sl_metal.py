#!/usr/bin/env python
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


# Improvement Items: 
#
# Deal with RAID and storage groups better
# Add hourly pre-packaged selections
# Make OS and imageTemplateID mutually exclusive
#

DOCUMENTATION = '''
---
module: sl_metal
short_description: Order a bare-metal instance on SoftLayer
description:
  - Create a bare-metal server in SoftLayer.  This technique may be used to order other SoftLayer hardware components such as storage, firewalls, and other 'packages', this module will focus BARE_METAL_CPU (servers), however.  
  - Options and values are highly dependant on the choice of package that is used.  Because of this, there will be a set of standard options, and then for the choice of a package type there will be an additional setup of options specific to that package.
  - The following is a list of standard options and options for a typical pkgid 253 (DUAL_E52600_4_DRIVES) system.
version_added: "0.0"
author: "Matt Kubilus, @kubilus1"
requirements:
    - "python >= 2.7"
    - "softlayer >= 5.2"
    - "pyyaml >= 3.12"
notes:
  - Using this module may incur charges to your SoftLayer account.  Use at your own risk.
  - It is highly recommended to first run this in check mode with verbose logging to double-check the product order.
  - Not all package/datacenter/options combinations may be available at all times.

options:
  name:
    required: true
    aliases: ["hostname"]
    description: 
      - Name of the server to create
      - Standard option
  domain:
    required: true
    description:
      - Domain name for the server to order
      - Standard option
  datacenter:
    required: true
    description:
      - Datacenter that will host the server
      - Standard option
  hourly:
    required: false
    default: False
    description:
      - Will the server be ordered hourly, or monthly.  Currently only works with monthly orders.
      - Standard option
  pkgid: 
    required: true
    description:
      - The server package that will be used.
      - Standard option
  primaryVlan:
    required: false
    description:
      - VLAN ID to use for the primary/public network
      - Standard option
  backendVlan:
    required: false
    description:
      - VLAN ID to use for the backend/private network
      - Standard option
  sshKeys:
    required: false
    description:
      - List of SSH keys to install on system
      - Standard option
  storageGroups:
    required: false
    description:
      - List of arrangement of disks into RAID groups
      - Standard option
  state:
    required: true
    description:
      - Requested state for the server
      - present - Check or order system
      - absent - Cancel system if it exists
      - reloaded - Reload the OS on the system
      - options - Return package specific options in verbose mode
      - Standard option
    choices: [ present, absent, reloaded, options ]
  av_spyware_protection:
    choices:
    - MCAFEE_VIRUSSCAN_ANTIVIRUS_WINDOWS
    description:
    - Anti-Virus & Spyware Protection
    - Package option for pkgid 253 at wdc01
    required: false
  bandwidth:
    choices:
    - BANDWIDTH_500_GB
    - BANDWIDTH_UNLIMITED_100_MBPS_UPLINK
    - BANDWIDTH_10000_GB
    - BANDWIDTH_5000_GB
    - BANDWIDTH_0_GB
    - BANDWIDTH_1000_GB
    - BANDWIDTH_20000_GB
    description:
    - Public Bandwidth
    - Package option for pkgid 253 at wdc01
    required: true
  bc_insurance:
    choices:
    - BUSINESS_CONTINUANCE_INSURANCE
    description:
    - Insurance
    - Package option for pkgid 253 at wdc01
    required: false
  cdp_backup:
    choices:
    - IDERA_BACKUP_AGENT_1_PACK
    - IDERA_BACKUP_AGENT_5_PACK
    - IDERA_BACKUP_AGENT_10_PACK
    - IDERA_BACKUP_AGENT_25_PACK
    description:
    - CDP Addon
    - Package option for pkgid 253 at wdc01
    required: false
  control_panel:
    choices:
    - PLESK_PANEL_12_5_WINDOWS_30_DOMAINS_BM
    - PLESK_PANEL_12_5_LINUX_30_DOMAINS_BM
    - CPANELWHM_WITH_FANTASTICO_AND_RVSKIN
    - PARALLELS_PLESK_PANEL_11_LINUX_100_DOMAIN_W_POWER_PACK
    - PARALLELS_PLESK_PANEL_11_LINUX_UNLIMITED_DOMAIN_W_POWER_PACK
    - PARALLELS_PLESK_PANEL_11_WINDOWS_UNLIMITED_DOMAIN_W_POWER_PACK
    - PLESK_PANEL_12_5_LINUX_UNLIMITED_BM
    - CPANELWHM_WITH_SOFTACULOUS_AND_RVSKIN
    - PARALLELS_PLESK_12_30_DOMAIN_W_POWER_PACK
    - PARALLELS_PLESK_12_UNLIMITED_DOMAIN_W_POWER_PACK
    description:
    - Control Panel Software
    - Package option for pkgid 253 at wdc01
    required: false
  database:
    choices:
    - MICROSOFT_SQL_SERVER_2014_ENTERPRISE_EDITION_2
    - MICROSOFT_SQL_SERVER_2014_EXPRESS_EDITION
    - MICROSOFT_SQL_SERVER_2014_STANDARD_EDITION
    - DATABASE_MYSQL_LINUX
    - DATABASE_MYSQL_5_0_WINDOWS
    - DATABASE_MICROSOFT_SQL_SERVER_2005_EXPRESS
    - DATABASE_MICROSOFT_SQL_SERVER_2005_STANDARD
    - DATABASE_MICROSOFT_SQL_SERVER_2005_WORKGROUP
    - DATABASE_MICROSOFT_SQL_SERVER_2005_ENTERPRISE
    - DATABASE_MICROSOFT_SQL_SERVER_2008_STANDARD_R2
    - DATABASE_MICROSOFT_SQL_SERVER_2008_EXPRESS_R2
    - DATABASE_MICROSOFT_SQL_SERVER_2008_WEB_R2
    - DATABASE_CLOUDERA_DISTRIBUTION_HADOOP_4
    - DATABASE_RIAK_1_X
    - DATABASE_MICROSOFT_SQL_SERVER_2008_STANDARD_3
    - DATABASE_MICROSOFT_SQL_SERVER_2008_STANDARD_R2_2
    - DATABASE_MICROSOFT_SQL_SERVER_2008_ENTERPRISE_3
    - DATABASE_MICROSOFT_SQL_SERVER_2008_ENTERPRISE_R2_2
    - DATABASE_MICROSOFT_SQL_SERVER_2008_WEB_3
    - DATABASE_MICROSOFT_SQL_SERVER_2008_WEB_R2_2
    - DATABASE_MICROSOFT_SQL_SERVER_2012_WEB
    - DATABASE_MYSQL_5_0_51_WINDOWS
    - DATABASE_MYSQL_5_7_WINDOWS
    - DATABASE_MICROSOFT_SQL_SERVER_2012_STANDARD
    - DATABASE_MICROSOFT_SQL_SERVER_2008_EXPRESS
    - DATABASE_MICROSOFT_SQL_SERVER_2008_ENTERPRISE
    - DATABASE_MICROSOFT_SQL_SERVER_2008_STANDARD
    - DATABASE_MICROSOFT_SQL_SERVER_2008_WEB
    - DATABASE_MICROSOFT_SQL_SERVER_2012_ENTERPRISE
    - DATABASE_MICROSOFT_SQL_SERVER_2008_ENTERPRISE_R2
    - DATABASE_MICROSOFT_SQL_SERVER_2014_WEB
    description:
    - Database Software
    - Package option for pkgid 253 at wdc01
    required: false
  disk0:
    choices:
    - HARD_DRIVE_2_00_TB_SATA_2
    - HARD_DRIVE_3_00_TB_SATA
    - HARD_DRIVE_4_00_TB_SATA
    - HARD_DRIVE_600_GB_SAS_15K_RPM
    - HARD_DRIVE_1_2_TB_SSD_10_DWPD
    - HARD_DRIVE_8_00_TB_SATA
    - HARD_DRIVE_960GB_SSD
    - HARD_DRIVE_400GB_SSD
    - HARD_DRIVE_800GB_SSD
    - HARD_DRIVE_1_00_TB_SATA_2
    - HARD_DRIVE_6_00_TB_SATA_3
    - HARD_DRIVE_8_00_TB_SATA_2
    - HARD_DRIVE_1_7_TB_SSD_3_DWPD
    description:
    - First Hard Drive
    - Package option for pkgid 253 at wdc01
    required: true
  disk1:
    choices:
    - HARD_DRIVE_2_00_TB_SATA_2
    - HARD_DRIVE_3_00_TB_SATA
    - HARD_DRIVE_4_00_TB_SATA
    - HARD_DRIVE_600_GB_SAS_15K_RPM
    - HARD_DRIVE_1_2_TB_SSD_10_DWPD
    - HARD_DRIVE_8_00_TB_SATA
    - HARD_DRIVE_960GB_SSD
    - HARD_DRIVE_400GB_SSD
    - HARD_DRIVE_800GB_SSD
    - HARD_DRIVE_1_00_TB_SATA_2
    - HARD_DRIVE_6_00_TB_SATA_3
    - HARD_DRIVE_8_00_TB_SATA_2
    - HARD_DRIVE_1_7_TB_SSD_3_DWPD
    description:
    - Second Hard Drive
    - Package option for pkgid 253 at wdc01
    required: false
  disk2:
    choices:
    - HARD_DRIVE_2_00_TB_SATA_2
    - HARD_DRIVE_3_00_TB_SATA
    - HARD_DRIVE_4_00_TB_SATA
    - HARD_DRIVE_600_GB_SAS_15K_RPM
    - HARD_DRIVE_1_2_TB_SSD_10_DWPD
    - HARD_DRIVE_8_00_TB_SATA
    - HARD_DRIVE_960GB_SSD
    - HARD_DRIVE_400GB_SSD
    - HARD_DRIVE_800GB_SSD
    - HARD_DRIVE_1_00_TB_SATA_2
    - HARD_DRIVE_6_00_TB_SATA_3
    - HARD_DRIVE_8_00_TB_SATA_2
    - HARD_DRIVE_1_7_TB_SSD_3_DWPD
    description:
    - Third Hard Drive
    - Package option for pkgid 253 at wdc01
    required: false
  disk3:
    choices:
    - HARD_DRIVE_2_00_TB_SATA_2
    - HARD_DRIVE_3_00_TB_SATA
    - HARD_DRIVE_4_00_TB_SATA
    - HARD_DRIVE_600_GB_SAS_15K_RPM
    - HARD_DRIVE_1_2_TB_SSD_10_DWPD
    - HARD_DRIVE_8_00_TB_SATA
    - HARD_DRIVE_960GB_SSD
    - HARD_DRIVE_400GB_SSD
    - HARD_DRIVE_800GB_SSD
    - HARD_DRIVE_1_00_TB_SATA_2
    - HARD_DRIVE_6_00_TB_SATA_3
    - HARD_DRIVE_8_00_TB_SATA_2
    - HARD_DRIVE_1_7_TB_SSD_3_DWPD
    description:
    - Fourth Hard Drive
    - Package option for pkgid 253 at wdc01
    required: false
  disk_controller:
    choices:
    - DISK_CONTROLLER_RAID
    - DISK_CONTROLLER_NONRAID
    - DISK_CONTROLLER_RAID_0
    - DISK_CONTROLLER_RAID_1
    - DISK_CONTROLLER_RAID_5
    - DISK_CONTROLLER_RAID_10
    description:
    - Disk Controller
    - Package option for pkgid 253 at wdc01
    required: true
  evault:
    choices:
    - EVAULT_175_GB
    - EVAULT_350_GB
    - EVAULT_750_GB
    - EVAULT_1500_GB
    - EVAULT_60_GB
    - EVAULT_20_GB
    - EVAULT_40_GB
    - EVAULT_100_GB
    - EVAULT_250_GB
    - EVAULT_1000_GB
    - EVAULT_30_GB
    - EVAULT_2000_GB
    description:
    - EVault
    - Package option for pkgid 253 at wdc01
    required: false
  evault_plugin:
    choices:
    - EVAULT_PLUGIN_BMR_BARE_METAL_RESTORE
    description:
    - EVault Plugin
    - Package option for pkgid 253 at wdc01
    required: false
  firewall:
    choices:
    - 2000MBPS_HARDWARE_FIREWALL
    - 1000MBPS_HARDWARE_FIREWALL
    - 100MBPS_HARDWARE_FIREWALL
    - 10MBPS_HARDWARE_FIREWALL
    - APF_SOFTWARE_FIREWALL_FOR_LINUX
    - 20MBPS_HARDWARE_FIREWALL
    - 200MBPS_HARDWARE_FIREWALL
    - MICROSOFT_WINDOWS_FIREWALL
    description:
    - Hardware & Software Firewalls
    - Package option for pkgid 253 at wdc01
    required: false
  intrusion_protection:
    choices:
    - MCAFEE_HOST_INTRUSION_PROTECTION_WREPORTING
    description:
    - Intrusion Detection & Protection
    - Package option for pkgid 253 at wdc01
    required: false
  managed_resource:
    choices: []
    description:
    - Managed Resource
    - Package option for pkgid 253 at wdc01
    required: false
  monitoring:
    choices:
    - MONITORING_HOST_PING
    - MONITORING_HOST_PING_AND_TCP_SERVICE
    description:
    - Monitoring
    - Package option for pkgid 253 at wdc01
    required: true
  monitoring_package:
    choices:
    - MONITORING_PACKAGE_BASIC
    - MONITORING_PACKAGE_PREMIUM_APPLICATION
    - MONITORING_PACKAGE_ADVANCED
    description:
    - Advanced Monitoring
    - Package option for pkgid 253 at wdc01
    required: false
  notification:
    choices:
    - NOTIFICATION_EMAIL_AND_TICKET
    description:
    - Notification
    - Package option for pkgid 253 at wdc01
    required: true
  os:
    choices:
    - OS_COREOS
    - OS_FREEBSD_9_X_64_BIT
    - OS_DEBIAN_8_X_JESSIE_MINIMAL_64_BIT_2
    - OS_UBUNTU_12_04_LTS_PRECISE_PANGOLIN_64_BIT
    - OS_VSPHERE_ENTERPRISE_PLUS_6_0
    - OS_WINDOWS_2012_FULL_DC_64_BIT
    - OS_WINDOWS_2012_FULL_DC_64_BIT_2
    - OS_CITRIX_XENSERVER_6_1
    - OS_RHEL_6_64_BIT_PER_PROCESSOR_LICENSING
    - OS_CENTOS_7_0
    - OS_QUANTASTOR_3_X_128_TB
    - OS_QUANTASTOR_3_X_48_TB
    - OS_DEBIAN_7_X_WHEEZY_MINIMAL_64_BIT
    - OS_VYATTA_6_X_SUBSCRIPTION_EDITION_64_BIT
    - OS_WINDOWS_2012_R2_FULL_DC_64_BIT
    - OS_WINDOWS_2012_R2_FULL_DC_64_BIT_2
    - OS_WINDOWS_2012_R2_FULL_STD_64_BIT
    - OS_VMWARE_ESXI_5_5
    - OS_CITRIX_XENSERVER_6_2_1
    - OS_FREEBSD_10_X_64_BIT
    - OS_NO_OPERATING_SYSTEM
    - OS_CITRIX_XENSERVER_6_5_1
    - OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT
    - OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_MINIMAL_64_BIT_2
    - OS_QUANTASTOR_3_X_16_TB
    - OS_QUANTASTOR_3_X_4_TB
    - OS_DEBIAN_8_X_JESSIE_64_BIT
    - OS_CENTOS_7_X_64_BIT
    - OS_WINDOWS_2012_FULL_STD_64_BIT
    - OS_DEBIAN_7_X_WHEEZY_64_BIT
    - OS_CENTOS_6_X_64_BIT
    - OS_QUANTASTOR_3_X_4_TB_QUANTASTOR_EXTRA_SMALL_TIER
    - OS_QUANTASTOR_4_X_16_TB_QUANTASTOR_SMALL_TIER
    - OS_QUANTASTOR_4_X_48_TB_QUANTASTOR_MEDIUM_TIER
    - OS_QUANTASTOR_4_X_128_TB
    - OS_CITRIX_XENSERVER_7_0_0
    - OS_WINDOWS_2008_FULL_STD_64_BIT_R2
    - OS_CITRIX_XENSERVER_6_5
    - OS_RHEL_7_1_64_BIT
    description:
    - Operating System
    - Package option for pkgid 253 at wdc01
    required: true
  os_addon:
    choices:
    - XENSERVER_ADVANCED_FOR_XENSERVER_6_X
    - XENSERVER_ENTERPRISE_FOR_XENSERVER_6_X
    - R1SOFT_SERVER_BACKUP_5_0_LINUX
    - VCENTER_6_0
    - VMWARE_VCENTER_5_1_STANDARD
    - IDERA_SERVER_BACKUP_5_0_ENTERPRISE_LINUX
    - IDERA_SERVER_BACKUP_5_0_ENTERPRISE_WINDOWS
    - XENSERVER_ADVANCED_FOR_XENSERVER_5_6
    - XENSERVER_ENTERPRISE_FOR_XENSERVER_5_6
    - CITRIX_ESSENTIALS_XENSERVER_5_5
    - VMWARE_VCENTER_5_5_STANDARD
    description:
    - OS-Specific Addon
    - Package option for pkgid 253 at wdc01
    required: false
  plesk_billing:
    choices: []
    description:
    - Parallels Plesk Billing
    - Package option for pkgid 253 at wdc01
    required: false
  port_speed:
    choices:
    - 100_MBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS
    - 1_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS
    - 100_MBPS_REDUNDANT_PRIVATE_NETWORK_UPLINKS
    - 100_MBPS_REDUNDANT_PUBLIC_PRIVATE_NETWORK_UPLINKS
    - 10_GBPS_REDUNDANT_PRIVATE_NETWORK_UPLINKS
    - 10_GBPS_REDUNDANT_PUBLIC_PRIVATE_NETWORK_UPLINKS
    - 10_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS
    - 1_GBPS_REDUNDANT_PUBLIC_PRIVATE_NETWORK_UPLINKS
    - 10_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS_NON_DATACENTER_RESTRICTED
    - 100_MBPS_PRIVATE_NETWORK_UPLINK
    - 1_GBPS_PRIVATE_NETWORK_UPLINK
    - 1_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS_UNBONDED
    - 1_GBPS_REDUNDANT_PRIVATE_NETWORK_UPLINKS
    - 10_GBPS_PRIVATE_NETWORK_UPLINK
    - 10_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS_NON_DATACENTER_RESTRICTED_2
    - 10_GBPS_DUAL_PRIVATE_NETWORK_UPLINKS_UNBONDED
    - 10_GBPS_DUAL_PUBLIC_PRIVATE_NETWORK_UPLINKS_UNBONDED
    - 100_MBPS_DUAL_PUBLIC_PRIVATE_NETWORK_UPLINKS_UNBONDED
    description:
    - Uplink Port Speeds
    - Package option for pkgid 253 at wdc01
    required: true
  power_supply:
    choices:
    - REDUNDANT_POWER_SUPPLY
    description:
    - Power Supply
    - Package option for pkgid 253 at wdc01
    required: false
  premium:
    choices: []
    description:
    - Surcharges
    - Package option for pkgid 253 at wdc01
    required: false
  pri_ip_addresses:
    choices:
    - 1_IP_ADDRESS
    description:
    - Primary IP Addresses
    - Package option for pkgid 253 at wdc01
    required: true
  pri_ipv6_addresses:
    choices:
    - 1_IPV6_ADDRESS
    description:
    - Primary IPv6 Addresses
    - Package option for pkgid 253 at wdc01
    required: false
  ram:
    choices:
    - RAM_64_GB_DDR3_1333_REG_2
    - RAM_256_GB_DDR3_1333_REG_2
    - RAM_512_GB_DDR4_2133_ECC_REG
    - RAM_128_GB_DDR3_1333_REG_2
    description:
    - RAM
    - Package option for pkgid 253 at wdc01
    required: true
  remote_management:
    choices:
    - REBOOT_KVM_OVER_IP
    description:
    - Remote Management
    - Package option for pkgid 253 at wdc01
    required: true
  response:
    choices:
    - AUTOMATED_NOTIFICATION
    - AUTOMATED_REBOOT_FROM_MONITORING
    description:
    - Response
    - Package option for pkgid 253 at wdc01
    required: true
  sec_ip_addresses:
    choices:
    - 4_PUBLIC_IP_ADDRESSES
    - 32_PUBLIC_IP_ADDRESSES
    description:
    - Public Secondary IP Addresses
    - Package option for pkgid 253 at wdc01
    required: false
  server:
    choices:
    - INTEL_XEON_2620_2_40
    - INTEL_XEON_2650_2_30
    - INTEL_XEON_2690_2_60
    description:
    - Server
    - Package option for pkgid 253 at wdc01
    required: true
  static_ipv6_addresses:
    choices:
    - 64_BLOCK_STATIC_PUBLIC_IPV6_ADDRESSES
    description:
    - Public Static IPv6 Addresses
    - Package option for pkgid 253 at wdc01
    required: false
  trusted_platform_module:
    choices:
    - INTEL_TXT_TRUSTED_EXECUTION_TECHNOLOGY
    description:
    - Server Security
    - Package option for pkgid 253 at wdc01
    required: false
  vpn_management:
    choices:
    - UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT
    description:
    - VPN Management - Private Network
    - Package option for pkgid 253 at wdc01
    required: true
  vulnerability_scanner:
    choices:
    - NESSUS_VULNERABILITY_ASSESSMENT_REPORTING
    description:
    - Vulnerability Assessments & Management
    - Package option for pkgid 253 at wdc01
    required: true
  web_analytics:
    choices: []
    description:
    - Web Analytics Software
    - Package option for pkgid 253 at wdc01
    required: false
'''

EXAMPLES = '''

  - name: Request server
    sl_metal:
      # Standard Options:
      name: "myserver" 
      domain: "bestdomainevah.com" 
      datacenter: "fra02" 
      hourly: False 
      os: OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT 
      pkgid: 253
      state: present
      # Package specific options
      ram: RAM_64_GB_DDR3_1333_REG_2 
      pri_ip_addresses: 1_IP_ADDRESS 
      bandwidth: BANDWIDTH_500_GB
      monitoring: MONITORING_HOST_PING 
      remote_management: REBOOT_KVM_OVER_IP 
      disk0: HARD_DRIVE_1_00_TB_SATA_2 
      notification: NOTIFICATION_EMAIL_AND_TICKET
      port_speed: 100_MBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS
      disk_controller: DISK_CONTROLLER_NONRAID
      vulnerability_scanner: NESSUS_VULNERABILITY_ASSESSMENT_REPORTING
      response: AUTOMATED_NOTIFICATION
      server: INTEL_XEON_2620_2_40
      vpn_management: UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT
    delegate_to: localhost

''' 

from ansible.module_utils.basic import AnsibleModule, _load_params

import re
import sys
import json

try:
    import SoftLayer
    HAS_SL = True
except ImportError:
    HAS_SL = False


class SL_data(object):
    """ 
    SL_data

    Wrap SoftLayer baremetal ordering information
    """

    def __init__(self, client):

        self.client = client
        self.dcenters = dict( 
            (x.get('name'),x.get('id')) for x in self.client["SoftLayer_Location_Datacenter"].getDatacenters(mask='name,id') 
        )

    def gen_option_docs(self, pkgid, datacenter):
        import yaml
        cats = self.get_categories(pkgid)
        item_cats = self.get_item_categories(pkgid, datacenter)
        doc = {'options':{ 
            c.get('itemCategory').get('categoryCode'):{
                'description':[
                    c.get('itemCategory').get('name'), 
                    "Package option for pkgid %s at %s" % (pkgid, datacenter) 
                ],
                'required':c.get('isRequired'),
                'choices':item_cats.get(c.get('itemCategory').get('categoryCode')) 
            } for c in cats 
        }}
        doc_json = json.dumps(doc)
        return yaml.dump(yaml.load(doc_json), default_flow_style=False)

    def get_server_pkgs(self):
        hws = self.client['Product_Package'].getAllObjects(mask='id,name,keyName,type')
        return dict( (x.get('keyName'),x.get('id')) for x in hws if 'BARE_METAL_CPU' in x.get('type').get('keyName') )

    def get_categories(self, package_id):
        categories = self.client['Product_Package'].getConfiguration(
            id=package_id, 
            mask='isRequired, itemCategory.id, itemCategory.name, itemCategory.categoryCode'
        )

        return categories

    def get_pricegroups(self, dcenter):
        if dcenter not in self.dcenters:
            return 1

        data = self.client["SoftLayer_Location_Datacenter"].getDatacenters(
            filter={'name':{'operation': dcenter} }, mask="priceGroups"
        )
        
        priceGroups = []
        if len(data) > 0:
            groups = data[0].get('priceGroups')
            priceGroups = [ x.get('id') for x in groups ]

        return priceGroups

    def get_standard_items(self, package_id):
        if hasattr(self, "std_%s" % package_id):
            standard_items = getattr(self, "std_%s" % package_id)
        else:
            standard_items = self.client["SoftLayer_Product_Package"].getItems(
                id=package_id, filter={'items':{'prices':{'locationGroupId':{'operation':'is null'}}}}
            )
            setattr(self, "std_%s" % package_id, standard_items)
        return standard_items
        
    def get_location_items(self, package_id, dcenter):
        if hasattr(self, "loc_%s_%s" % (package_id, dcenter)):
            location_items = getattr(self, "loc_%s_%s" % (package_id, dcenter))
        else:
            price_groups = self.get_pricegroups(dcenter)
            location_items = self.client["SoftLayer_Product_Package"].getItems(
                id=package_id, 
                filter={'items':{'prices':{'locationGroupId':{
                    'operation':'in',
                    'options':[{
                        'name':'data',
                        'value':price_groups
                    }]
                }}}}
            )
            setattr(self, "loc_%s_%s" % (package_id, dcenter), location_items)
        return location_items

    def get_items(self, key, package_id, dcenter):
        standard_items = self.get_standard_items(package_id)
        location_items = self.get_location_items(package_id, dcenter)

        #std_dict = {s.get('id'):s for s in standard_items if s.get('id') not in dict1}
        item_dict = dict( (s.get(key), s) for s in standard_items )

        loc_dict = dict( 
            (s.get(key), l) for l in location_items for s in standard_items if s.get(key) == l.get(key)
        )

        # Update the standard items with location specific pricing
        item_dict.update(loc_dict)
        return item_dict

    def get_item(self, name, package_id, dcenter):
        items = self.get_items('keyName', package_id, dcenter)
        return items.get(name)

    def get_item_priceid(self, name, package_id, dcenter):
        item = self.get_item(name, package_id, dcenter)
        if not item:
            return None
        if len(item.get('prices')) > 0:
            return item.get('prices')[0].get('id')

    def get_item_categories(self, package_id, dcenter):
        cats = self.get_categories(package_id)
        items = self.get_items('id', package_id, dcenter)

        item_cats = dict( 
            (c.get('itemCategory').get('categoryCode'), [ 
                i.get('keyName') for i in items.itervalues() \
                if i.get('itemCategory').get('id') == c.get('itemCategory').get('id') 
            ]) for c in cats
        )

        # Massage the disk options since the SoftLayer API is inconsistent and broken
        disk_opts = item_cats.get('disk0')
        for k in item_cats:
            if re.match('disk[0-9]+', k):
                item_cats[k] = disk_opts

        return item_cats


class Order(object):
    """
    Order - SoftLayer product order class
    """
    def __init__(self, client, module):
        self.client = client
        self.module = module

        self.stdparams = [
            'name',
            'hostname',
            'domain',
            'hourly',
            'pkgid',
            'datacenter',
            'primaryVlan',
            'backendVlan',
            'imageTemplateId',
            'sshKeys',
            'storageGroups',
            'state',
        ]

        # Get the list it itemkeys to get prices for
        self.item_values = [ module.params.get(x) for x in module.params if x not in self.stdparams ]

        for k in self.stdparams:
            setattr(self, k, module.params.get(k))

    def getLocationId(self, location):
        """Return the id of the datacenter specified by its short name."""
        filt = {'name': {'operation': location}}
        locations = self.client['Location'].getDataCenters(mask='id, name', filter=filt)
        if len(locations) != 1:
            return None     
        return locations[0].get('id')

    def getProductOrder(self):
        """Return the product order in a structure consumable by the SL API"""
        sld = SL_data(self.client)
       
        # For each item key get the price id, unless it is not specified
        prices = [ 
            {'id': sld.get_item_priceid(x,self.pkgid, self.datacenter), 'name':x} for x in self.item_values if x is not None 
        ]
        
        productOrder = {
            "quantity": 1,
            "hardware": [{
                            "hostname": self.hostname,
                            "domain": self.domain,
                            "primaryBackendNetworkComponent": self.backendVlan,
                            "primaryNetworkComponent": self.primaryVlan
                        }],
            "imageTemplateId": self.imageTemplateId,
            "location": self.getLocationId(self.datacenter),
            "useHourlyPricing": self.hourly,
            "packageId": self.pkgid,
            "prices": prices,
            "sshKeys": [self.sshKeys],
            "storageGroups": [self.storageGroups]
        }
        return productOrder


def main():
    client = SoftLayer.create_client_from_env()
  
    # We need to pre-parse the arguments to get pkgid and datacenter
    # Since available options are dependant on this
    args = _load_params()

    sld = SL_data(client)
    
    arg_spec       = dict(
        hostname        = dict(required=True, aliases=['name']),
        domain          = dict(required=True),
        pkgid           = dict(required=True, type='int'),
        datacenter      = dict(required=True, choices=sld.dcenters.keys()),
        hourly          = dict(type='bool', default=False),
        imageTemplateId = dict(type='int'),
        sshKeys         = dict(type='list'),
        storageGroups   = dict(type='list'),
        backendVlan     = dict(),
        primaryVlan     = dict(), 
        state           = dict(required=True, choices=['present','absent','reloaded', 'options'])
    )

    # Determine the action we wish to take
    state = args.get('state')
    
    # Create required arg_spec dictionary for packageid/datacenter combination
    item_cats = sld.get_item_categories(int(args.get('pkgid')), args.get('datacenter'))
    cats = sld.get_categories(int(args.get('pkgid')))
    if state == 'present' or state == 'options':
        # Grab options unique to the chosen package id
        package_spec = dict(
            (c.get('itemCategory').get('categoryCode'), { 
                'required': c.get('isRequired'), 'choices': item_cats.get(c.get('itemCategory').get('categoryCode')) 
            }) for c in cats if item_cats.get(c.get('itemCategory').get('categoryCode'))
        )
    else:
        # If not creating/verifying mark all package options as not required
        package_spec = dict(
            (c.get('itemCategory').get('categoryCode'), { 
                'required': 0, 'choices': item_cats.get(c.get('itemCategory').get('categoryCode')) 
            }) for c in cats if item_cats.get(c.get('itemCategory').get('categoryCode'))
        )

    # Extend the arguments with the available package_specs
    arg_spec.update(package_spec)

    if state == 'options':
        # If we are only checking the options, immediately exit
        sys.stdout.write(json.dumps(arg_spec))
        sys.exit(0)

    module = AnsibleModule(
        argument_spec = arg_spec,
        supports_check_mode=True
    )

    order = Order(client, module)

    # Let's take a look at the existing hardware systems...
    mgr = SoftLayer.HardwareManager(client)
    hws =  mgr.list_hardware(
        hostname = module.params.get('hostname'),
        domain = module.params.get('domain'),
        datacenter = module.params.get('datacenter')
    )

    if state == "present":
        # Check fqdn for a datacenter.  NOTE, this may allow duplicates if users do not have permissions to 
        # view the same set of servers
        if hws:
            module.exit_json(changed=False)
                   
        if module.check_mode:
            o = client['Product_Order'].verifyOrder(order.getProductOrder())
        else:
            # Place order
            o = client['Product_Order'].placeOrder(order.getProductOrder(), False)
        module.exit_json(changed=True, order=o)

    elif state == "absent":
        if hws:
            #mgr.cancel_hardware(hws[0].get('id'))
            module.exit_json(changed=True, instance=json.loads(hws0))
        else:
            module.exit_json(changed=False)

    elif state == "reloaded":
        if hws:
            mgr.reload(hws[0].get('id'), ssh_keys=module.params.get('sshKeys'))
            module.exit_json(changed=True)
        else:
            module.fail_json(msg="%s.%s in %s not found" % (
                module.params.get('hostname'),
                module.params.get('domain'),
                module.params.get('datacenter')
            ))

if __name__ == "__main__":
    main()

