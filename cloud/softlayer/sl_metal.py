#!/usr/bin/env python

# TODO: 
#
# Documentation
# TEST
# Deal with RAID and storage groups better
# Check for existing hostname.domain
# Add hourly pre-packaged selections
# Make OS and imageTemplateID mutually exclusive
#

DOCUMENTATION = '''
---
module: sl_metal
short_description: Order a bare-metal instance on SoftLayer
description:
  - Create a bare-metal server in SoftLayer.  This technique may be used to other SoftLayer hardware components such as storage, firewalls, and other 'packages'.  Options and values are highly dependant the choice of package that is used.  Because of this, there will be a set of standard options, and then for the choice of a package type there will be an additional setup of options specific to that package.

standard options:
  name:
    required: true
    aliases: ["hostname"]
    description: 
      - Name of the server to create
  domain:
    required: true
    description:
      - Domain name for the server to order
  datacenter:
    required: true
    description:
      - Datacenter that will host the server
  hourly:
    required: false
    default: True
    description:
      - Will the server be ordered hourly, or monthly
  os:
    required: true
    description:
      - The OS that will be installed on the server
  pkgid: 
    required: true
    description:
      - The server package that will be used.
  primaryVlan:
    required: false
    description:
      - VLAN ID to use for the primary/public network
  backendVlan:
    required: false
    description:
      - VLAN ID to use for the backend/private network
  sshKeys:
    required: false
    description:
      - List of SSH keys to install on system
  storageGroups:
    required: false
    description:
      - List of arrangement of disks into RAID groups

 
typical server options:  
'''

EXAMPLES = '''

- name: Build metal instance
  hosts: localhost
  gather_facts: False
  tasks:
  - name: Build instance request
    sl_metal:
      name: "myserver" 
      domain: "bestdomainevah.com" 
      datacenter: "fra02" 
      hourly: False 
      os: OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT 
      pkgid: 253 
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

''' 

# Wildcard import for compatibility
from ansible.module_utils.basic import *
import json
import pprint
import sys
import shlex

try:
    import SoftLayer
    client = SoftLayer.create_client_from_env()
    HAS_SL = True
except ImportError:
    HAS_SL = False

class SL_data(object):
    """ 
    SL_data

    Wrap SoftLayer baremetal ordering information
    """

    def __init__(self):

        self.dcenters = { 
            x.get('name'):x.get('id') for x in client["SoftLayer_Location_Datacenter"].getDatacenters(mask='name,id') 
        }

    def get_packages(self):
        return client['Product_Package'].getAllObjects(mask='id,name,keyName')

    def get_categories(self, package_id):
        categories = client['Product_Package'].getConfiguration(id=package_id, mask='isRequired, itemCategory.id, itemCategory.name, itemCategory.categoryCode')

        return categories

    def get_pricegroups(self, dcenter):
        if dcenter not in self.dcenters:
            return 1

        data = client["SoftLayer_Location_Datacenter"].getDatacenters(
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
            standard_items = client["SoftLayer_Product_Package"].getItems(
                id=package_id, filter={'items':{'prices':{'locationGroupId':{'operation':'is null'}}}}
            )
            setattr(self, "std_%s" % package_id, standard_items)
        return standard_items
        
    def get_location_items(self, package_id, dcenter):
        if hasattr(self, "loc_%s_%s" % (package_id, dcenter)):
            location_items = getattr(self, "loc_%s_%s" % (package_id, dcenter))
        else:
            price_groups = self.get_pricegroups(dcenter)
            location_items = client["SoftLayer_Product_Package"].getItems(
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
        item_dict = {s.get(key):s for s in standard_items}

        loc_dict = {
            s.get(key): l for l in location_items for s in standard_items if s.get(key) == l.get(key)
        }

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

        item_cats = { 
            c.get('itemCategory').get('categoryCode'):[ 
                i.get('keyName') for i in items.itervalues() \
                if i.get('itemCategory').get('id') == c.get('itemCategory').get('id') 
            ] for c in cats 
        }

        return item_cats


class Order(object):
    def __init__(self, module):
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
        ]

        # Get the list it itemkeys to get prices for
        self.item_values = [ module.params.get(x) for x in module.params if x not in self.stdparams ]

        for k in self.stdparams:
            setattr(self, k, module.params.get(k))

    def getLocationId(self, location):
        '''Return the id of the datacenter specified by its short name.'''
        filt = {'name': {'operation': location}}
        locations = client['Location'].getDataCenters(mask='id, name', filter=filt)
        if len(locations) != 1:
            return None     
        return locations[0].get('id')

    def getProductOrder(self):
        sld = SL_data()
       
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
  
    # We need to pre-parse the arguments to get pkgid and datacenter
    # Since available options are dependant on this
    args_file = sys.argv[1]
    args_json = file(args_file).read()
    args_data = json.loads(args_json)
    args = args_data.get('ANSIBLE_MODULE_ARGS',{})
    

    sld = SL_data()
    # will need to get package_id and datacenter before parsing the argument_spec
    item_cats = sld.get_item_categories(int(args.get('pkgid')), args.get('datacenter'))

    cats = sld.get_categories(int(args.get('pkgid')))
    
    arg_spec       = dict(
        hostname        = dict(required=True, aliases=['name']),
        domain          = dict(required=True),
        pkgid           = dict(required=True, type='int'),
        datacenter      = dict(required=True, choices=sld.dcenters.keys()),
        hourly          = dict(type='bool', default=True),
        imageTemplateId = dict(type='int'),
        sshKeys         = dict(type='list'),
        storageGroups   = dict(type='list'),
        backendVlan     = dict(),
        primaryVlan     = dict(), 
    )

    package_spec = { 
        c.get('itemCategory').get('categoryCode'): { 
            'required': c.get('isRequired'), 'choices': item_cats.get(c.get('itemCategory').get('categoryCode')) 
        } for c in cats 
    }

    arg_spec.update(package_spec)

    module = AnsibleModule(
        argument_spec = arg_spec,
        supports_check_mode=True
    )

    order = Order(module)

    if module.check_mode:
        o = client['Product_Order'].verifyOrder(order.getProductOrder())
        print o

    module.exit_json(changed=True)

if __name__ == "__main__":
    main()
