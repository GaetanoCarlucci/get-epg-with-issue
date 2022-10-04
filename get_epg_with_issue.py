#!/usr/bin/env python
#
#   Author: Gaetano Carlucci, Cisco CX
#   Python Version: 3
#
#   This software is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied

import json
from Utils.Session import Session
import re

# Returns a dict with all EPG deployed in the fabric
def get_all_epg(my_fabric, api_name):
    output = []
    data_json = json.loads(my_fabric.apic_json_get(api_name))
    for vrf_ref in data_json['imdata']:
        for k, v in vrf_ref['fvAEPg'].items():
            for j, attribute in v.items():
                if j == 'dn':
                    if re.search('/tn-(.*?)/ap-(.*?)/epg-(.*)', attribute):
                        tenant_name = (re.search('/tn-(.*?)/ap-(.*?)/epg-(.*)', attribute)).group(1)
                        app_name = (re.search('/tn-(.*?)/ap-(.*?)/epg-(.*)', attribute)).group(2)
                        epg_name = (re.search('/tn-(.*?)/ap-(.*?)/epg-(.*)', attribute)).group(3)
                        output.append([tenant_name, app_name, epg_name])
    return output

def main():
    with open('Utils/credentials.json') as json_file:
        data = json.load(json_file)

    my_fabric = Session(data['apic_ip_address'], data["apic_port"],
                        data['apic_admin_user'], data['apic_admin_password'])

    cookie = my_fabric.get_cookie()
    my_fabric.set_cookie(cookie)

    epg_list = get_all_epg(my_fabric, 'fvAEPg')

    leaf_ip = ['10.47.142.53', '10.47.142.54']
    #epg_list = [['LDO', 'LSX_02_AP', 'SAP_PHY_EPG'], ['SYS', 'DC02 - AP', 'VEEAM - EPG'],
    #            ['SXC', 'POMEZIA_02_AP', 'SCGIT_EPG'], ['SDI', 'SDI - AP', 'Test_Wass - EPG'],
    #            ['LDO', 'BROWN_02_AP', 'SAP_HYPERION_EPG'], ['EDG', 'BROWN_02_AP', 'SRV_CLOUD_EPG'],
    #            ['EDG', 'BROWN_02_AP', 'EQUITRAC_EDG_EPG'], ['EDG', 'BROWN_02_AP', 'MCAFEE_SXE_EPG'],
    #            ['SYS', 'BACKUP_02_AP', 'SYS_EPG'], ['EDG', 'BROWN_02_AP', 'SAP_SELEXELSAG_EPG'],
    #            ['EDG', 'BROWN_02_AP', 'SRV_DIVISIONALI_EPG'], ['SXC', 'SAM_02_AP', 'GW_SXC_EPG'],
    #            ['SXC', 'BROWN_02_AP', 'SERV_V200_EPG'], ['EDG', 'FONIA_02_AP', 'SRV_EPG'],
    #            ['LDO', 'BROWN_02_AP', 'MCAFEE_EPO_EPG'], ['SGP', 'BROWN_02_AP', 'SRV_WIN_EPG'],
    #            ['LDO', 'BROWN_02_AP', 'SES_CSM_CERT_EPG'], ['common', 'LICENSE_SRV_02_AP', 'TRIADE_LS_3_EPG'],
    #            ['common', 'IDP_T_02_AP', 'LDAPEXT_EPG'], ['common', 'IDP_02_AP', 'STS_PROD_EPG']]

    for address in leaf_ip:
        my_fabric = Session(address, data["apic_port"],
                            data['apic_admin_user'], data['apic_admin_password'])
        cookie = my_fabric.get_cookie()
        my_fabric.set_cookie(cookie)

        url_base = 'https://' + address + '/api/node/class/ipCons.xml?query-target-filter=and(and(wcard(ipCons.dn,"dom-'
        i = 0

        with open('OUTPUT_' + address + '_.txt', 'w') as f:
            for row in epg_list:
                i = i + 1
                if i == 20:
                    cookie = my_fabric.get_cookie()
                    my_fabric.set_cookie(cookie)
                    i = 0
                url = url_base + row[0] + '.*epgDn-\[uni/tn-' + row[0] + '/ap-' \
                      + row[1] + '/epg-' + row[2] + '")),not(wcard(ipCons.dn,"epp")))'
                print(url)
                f.write(url)
                f.write('\n')
                output = my_fabric.leaf_json_get(url)
                f.write(output)
                f.write('\n')

if __name__ == "__main__":
    main()
