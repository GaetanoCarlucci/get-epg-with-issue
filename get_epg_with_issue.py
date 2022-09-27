#!/usr/bin/env python
#
#   Author: Gaetano Carlucci, Cisco CX
#   Python Version: 3
#
#   This software is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied

import json
from Utils.Session import Session
from Utils import excel_lib
import re


# parsed the column in order to get a more user friendly output
def parse_column(column_for_excel_raw, node_names, node_addr, bd_names, vrf, subnet_ip):
    output = []
    column = ['VLAN', 'node_id', 'oob_addr', 'host_name', 'tenant_name', 'ap_name', 'epg_name', 'bd_name', 'vrf', 'subnet_ip']
    for row in column_for_excel_raw:
        new_row = {}
        ap_name = ''
        new_row['vrf'] = ''
        for k, v in row.items():
            if k == 'epgDn':
                if re.search('/epg-(.*)', v):
                    tenant_name = (re.search('/tn-(.*?)/', v)).group(1)
                    app_name = (re.search('/ap-(.*?)/epg-(.*)', v)).group(1)
                    epg_name = (re.search('/ap-(.*?)/epg-(.*)', v)).group(2)
                    new_row['epg_name'] = epg_name
                    key_in_bd_names = tenant_name + '/' + app_name + '/' + epg_name
                    if key_in_bd_names in bd_names:
                        scope_vrf = bd_names[key_in_bd_names][1]
                        new_row['vrf'] = vrf[scope_vrf]
                        bd_name = bd_names[key_in_bd_names][0]
                        new_row['bd_name'] = bd_name
                        if bd_name in subnet_ip:
                            new_row['subnet_ip'] = subnet_ip[bd_name]
                        else:
                            new_row['subnet_ip'] = ''
                    else:
                        new_row['bd_name'] = ''
                        new_row['subnet_ip'] = ''
                if re.search('/tn-(.*?)/', v):
                    tenant_name = (re.search('/tn-(.*?)/', v)).group(1)
                    new_row['tenant_name'] = tenant_name
                if re.search('/ap-(.*?)/', v):
                    ap_name = (re.search('/ap-(.*?)/', v)).group(1)
                    new_row['ap_name'] = ap_name
            if k == 'dn':
                if re.search('/node-(.*?)/', v):
                    node_id = (re.search('/node-(.*?)/', v)).group(1)
                    new_row['node_id'] = node_id
                    new_row['host_name'] = node_names[node_id]
                    new_row['oob_addr'] = node_addr[node_id]
            if k == 'encap':
                new_row['VLAN'] = v
        if ap_name == '':
            new_row['ap_name'] = row['epgDn']
            new_row['epg_name'] = row['epgDn']
            new_row['bd_name'] = ''
            new_row['subnet_ip'] = ''
        output.append(new_row)
    return [output, column]


# Return a list of dict with correspond to each row of the excel sheet not parsed
def get_vlan_encap(my_fabric, api_name, column):
    output = []
    data_json = json.loads(my_fabric.apic_json_get(api_name))
    for vlan in data_json['imdata']:
        for k, v in vlan.items():
            row = {}
            for j, attribute in v.items():
                for i in column:
                    row[i] = attribute[i]
                output.append(row)
    return output


# Returns a dict with Node id as key and host name as value
def get_node_name(my_fabric, api_name):
    output = {}
    data_json = json.loads(my_fabric.apic_json_get(api_name))
    for fabric_node in data_json['imdata']:
        for k, v in fabric_node['fabricNode'].items():
            for j, attribute in v.items():
                if j == 'dn':
                    if re.search('/node-(.*)', attribute):
                        node_id = (re.search('/node-(.*)', attribute)).group(1)
                if j == 'name':
                    name = attribute
            output[node_id] = name
    return output


# Returns a dict with Node oob addresses as value and node id as key
def get_node_oob_addresses(my_fabric, api_name):
    output = {}
    data_json = json.loads(my_fabric.apic_json_get(api_name))
    for fabric_node in data_json['imdata']:
        for k, v in fabric_node['mgmtRsOoBStNode'].items():
            for j, attribute in v.items():
                if j == 'dn':
                    if re.search('/node-(.*)', attribute):
                        node_id = (re.search('/node-(.*)]', attribute)).group(1)
                if j == 'addr':
                    addr = attribute
            output[node_id] = addr
    return output


# Returns a dict with bd name as key and ip as value
def get_ip(my_fabric, api_name):
    output = {}
    data_json = json.loads(my_fabric.apic_json_get(api_name))
    for subnet in data_json['imdata']:
        for k, v in subnet['fvSubnet'].items():
            for j, attribute in v.items():
                if j == 'dn':
                    if re.search('/BD-(.*?)/', attribute):
                        bd_name = (re.search('/BD-(.*?)/', attribute)).group(1)
                if j == 'ip':
                    ip = attribute
            output[bd_name] = ip
    return output


# Returns a dict with EPG as key and BD name as value
def get_bd(my_fabric, api_name):
    output = {}
    tenants = {}

    bd_scope_json = json.loads(my_fabric.apic_json_get('fvBD'))
    for bd_ref in bd_scope_json['imdata']:
        for k, v in bd_ref['fvBD'].items():
            for j, attribute in v.items():
                if j == 'dn':
                    if re.search('/tn-(.*?)/', attribute):
                        tenant_name = (re.search('/tn-(.*?)/', attribute)).group(1)
                        bd_name = (re.search('/tn-(.*?)/BD-(.*)', attribute)).group(2)
                if j == 'scope':
                    scope = attribute
            tenants[tenant_name + '/' + bd_name] = scope

    data_json = json.loads(my_fabric.apic_json_get(api_name))
    for bd_ref in data_json['imdata']:
        for k, v in bd_ref['fvRsBd'].items():
            for j, attribute in v.items():
                if j == 'dn':
                    if re.search('/epg-(.*?)/', attribute):
                        app_name = (re.search('/ap-(.*?)/epg-(.*?)/', attribute)).group(1)
                        epg_name = (re.search('/ap-(.*?)/epg-(.*?)/', attribute)).group(2)
                        tenant_name = (re.search('/tn-(.*?)/', attribute)).group(1)
                if j == 'tDn':
                    if re.search('/BD-(.*)', attribute):
                        bd_name = (re.search('/BD-(.*)', attribute)).group(1)
            scope = tenants[tenant_name + '/' + bd_name]
            output[tenant_name + '/' + app_name + '/' + epg_name] = [bd_name, scope]
    return output


# Returns a dict with VRF scope as key and VRF name as value
def get_vrf(my_fabric, api_name):
    output = {}
    data_json = json.loads(my_fabric.apic_json_get(api_name))
    for vrf_ref in data_json['imdata']:
        for k, v in vrf_ref['fvCtx'].items():
            for j, attribute in v.items():
                if j == 'dn':
                    if re.search('/tn-(.*?)/ctx-(.*)', attribute):
                        vrf_name = (re.search('/tn-(.*?)/ctx-(.*)', attribute)).group(2)
                if j == 'scope':
                    scope = attribute
            output[scope] = vrf_name
    return output


def main():
    with open('Utils/credentials.json') as json_file:
        data = json.load(json_file)
    my_fabric = Session(data['apic_ip_address'], data["apic_port"],
                        data['apic_admin_user'], data['apic_admin_password'])
    cookie = my_fabric.get_cookie()
    my_fabric.set_cookie(cookie)

    excel = excel_lib.Excel('./', "Vlan_Encap")

    column_raw = ["encap", "epgDn", "dn"]
    column_for_excel_raw = get_vlan_encap(my_fabric, 'vlanCktEp', column_raw)
    node_names = get_node_name(my_fabric, 'fabricNode')
    node_oob_addresses = get_node_oob_addresses(my_fabric, 'mgmtRsOoBStNode')
    bd_names = get_bd(my_fabric, 'fvRsBd')
    subnet_ip = get_ip(my_fabric, 'fvSubnet')
    vrf = get_vrf(my_fabric, 'fvCtx')

    column_for_excel = parse_column(column_for_excel_raw, node_names, node_oob_addresses, bd_names, vrf, subnet_ip)
    excel.create_sheet("Vlan_Encap", column_for_excel[1])
    excel.fill_sheet(column_for_excel[0], "Vlan_Encap")

    print("Vlan_Encap.xlsx successfully created")

    excel.convert_to_csv("Vlan_Encap", "Vlan_Encap.csv")

    for id, address in node_oob_addresses.items():
        address = address.split('/')[0]
        url_base = 'https://' + address + '/api/node/class/ipCons.xml?query-target-filter=and(and(wcard(ipCons.dn,"dom-'

        for row in column_for_excel[0]:
            url = url_base + row['tenant_name'] + ':' + row['vrf'] + '.*epgDn-\[uni/tn-' + row['tenant_name'] + '/ap-' \
                  + row['ap_name'] + '/epg-' + row['epg_name'] + '")),not(wcard(ipCons.dn,"epp")))'
            output = my_fabric.leaf_json_get(url)
            print(output)

            break

if __name__ == "__main__":
    main()
