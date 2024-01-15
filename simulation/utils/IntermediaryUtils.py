from django.shortcuts import render
import requests
from requests.auth import HTTPBasicAuth
from ciscoconfparse import CiscoConfParse
from ciscoconfparse import CiscoPassword
from django.conf import settings
from ciscoconfparse.ccp_util import IPv4Obj
from .. import views


def getConfigDeviceType(projectID, node):
    response = requests.get(settings.SIMULATION_SITE_DOMAIN + "v2/projects/" + projectID + "/nodes/" + node["id"],
            auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))
    data = response.json()
    deviceType = data.get("node_type")

    if deviceType == "dynamips":
        deviceType = "router"
    elif deviceType == "iou":
        deviceType = "switch"

    return deviceType

def getConfigServicePasswordEncryption(parse):
    servPassLine = parse.find_objects(r'^service password-encryption')
    if servPassLine:
        return "true"
    else:
        return "false"

def getConfigPrivilegeExecHash(parse):
    hashLine = parse.find_objects(r'^enable secret')
    if hashLine:
        hash = hashLine[0].text.split()
        return hash[3]
    else:
        return {}

def getConfigHostname(parse):
    hostnameLine = parse.find_objects(r'^hostname')
    if hostnameLine:
        hostname = hostnameLine[0].text.split()
        return hostname[1]
    else:
        return {"hh":"hh"}

def getConfigInterfaces(parse):
    interface_data = {}

    # Find all interfaces with IP addresses configured
    interfaces_with_ip = parse.find_objects(r'^interface')

    # Store interface data in the dictionary
    for intf in interfaces_with_ip:
        interface_name = intf.text.strip()  # Extract the interface name
        int_name = interface_name.split()
        ip_addresses = intf.re_search_children(r'^\s')

        # Extract the IP address information as a dictionary
        if ip_addresses:
            ip_info = {}
            switchport = {}
            for ip_addr in ip_addresses:
                
                if ip_addr.text.startswith(" ip address"):
                    parts = ip_addr.text.strip().split()  # Split into ["ip", "address", "192.168.1.1", "255.255.255.0"]
                    ip_info[parts[0] + " "+parts[1]] = parts[2]  # Use "ip" as the key and the IP address as the value
                    ip_info["subnet mask"] = parts[3]

                    net = str(IPv4Obj(parts[2] + '/' + parts[3]).prefixlength)
                    ip_info['subnet mask in cidr'] = net
                elif ip_addr.text.startswith(" clock rate"): 
                    parts = ip_addr.text.strip().split()
                    ip_info["clock rate"] = parts[2]
                elif ip_addr.text.startswith(" description"):
                    parts = ip_addr.text.strip().split(' ', 1)[1]
                    ip_info["description"] = parts
                elif(ip_addr.text.startswith(" switchport mode")):
                    switchport["mode"] = ip_addr.text.strip().split()[2]
                elif(ip_addr.text.startswith(" switchport access vlan")):
                    switchport["vlan"] = ip_addr.text.strip().split()[3]
                elif(ip_addr.text.startswith(" switchport port-security violation")):
                    switchport["violation"] = ip_addr.text.strip().split()[3]
                elif(ip_addr.text.startswith(" switchport port-security mac-address sticky")):
                    macAddress = ip_addr.text.strip()
                    macAddress = macAddress.replace("switchport port-security mac-address sticky", "")
                    switchport["mac-address sticky"] = macAddress.strip()
                elif(ip_addr.text.startswith(" switchport port-security mac-address")):
                    switchport["mac-address"] = ip_addr.text.strip().split()[3]
                elif(ip_addr.text.startswith(" switchport port-security")):
                    switchport["port security"] = "true"
                else:
                    if ip_addr.text.startswith(" shutdown"): 
                        parts = ip_addr.text.strip()
                        if parts:
                            ip_info["shutdown"] = "true"
                    else:
                        ip_info["shutdown"] = "false"
                        continue
            
            if len(switchport) != 0:
                ip_info["switchport"] = switchport
            interface_data[int_name[1]] = ip_info

    return interface_data

def getConfigRoutingProtocol(parse):
    routingData = {}
    routingLine = parse.find_objects_w_child(r'^router', r'^\s+network')

    if routingLine:
        routingData["protocol"] = routingLine[0].text.split()[1]
        if routingData.get("protocol") == "ospf":
            routingData["process id"] = routingLine[0].text.split()[2]

            networks = routingLine[0].re_search_children(r'^\s+network')

            networkArray = []
            for network in networks:
                networkData = network.text.strip().split()
                networkDataObject = {}
                networkDataObject["ip address"] = networkData[1]
                networkDataObject["wildcard mask"] = networkData[2]
                networkDataObject["area"] = networkData[4]

                networkArray.append(networkDataObject)
        elif routingData.get("protocol") == "rip":
            networks = routingLine[0].re_search_children(r'^\s+network')
            networkArray = []

            for network in networks:
                networkData = network.text.strip().split()
                networkArray.append(networkData[1])
        
        routingData["networks"] = networkArray

        return routingData
    else:
        return {}

def getConfigBannerMOTD(parse):
    bannerLine = parse.find_objects(r'^banner')
    if bannerLine:
        banner = bannerLine[0].text.split()
        banner = banner[2].replace("\u0003", "")
        return banner
    else:
        return {}

def getConfigConsolePassword(parse):
    consoleData = {}
    consoleLine = parse.find_objects(r'^line con 0')

    if consoleLine:
        consoleLinePassword = consoleLine[0].re_search_children(r'^\s')
        if consoleLinePassword:
            dp = CiscoPassword()
            decrypted_passwd = dp.decrypt(consoleLinePassword[0].text.split()[2])
            if decrypted_passwd != "":
                consoleData["password"] = decrypted_passwd

            consoleLineExecTimeout = consoleLine[0].re_search_children(r'^\sexec-timeout')
            consoleLineExecTimeoutArray = consoleLineExecTimeout[0].text.split()
            consoleData["exec timeout"] = consoleLineExecTimeoutArray[1] + " " +  consoleLineExecTimeoutArray[2]

            consoleLineLogin = consoleLine[0].re_search_children(r'^\slogin')
            if consoleLineLogin:
                consoleData["login"] = "true"
            else:
                consoleData["login"] = "false"

            return consoleData
        else:
            return {}
    else:
        return {}

def getConfigLineVTY(parse):
    vtyData = {}
    vtyLine = parse.find_objects(r'^line vty')

    
    if vtyLine:

        vty0to4 = {}
        vty0to4PasswordLine = vtyLine[0].re_search_children(r'^\spassword')
        if vty0to4PasswordLine:
            if len(vty0to4PasswordLine[0].text.split()) > 2:
                dp = CiscoPassword()
                decrypted_passwd = dp.decrypt(vty0to4PasswordLine[0].text.split()[2])
                vty0to4["password"] = decrypted_passwd
            else:
                 vty0to4["password"] = vty0to4PasswordLine[0].text.split()[1]
        

        vty0to4LoginLine = vtyLine[0].re_search_children(r'^\slogin')
        if vty0to4LoginLine:
            vty0to4["login"] = "true"
        else:
            vty0to4["login"] = "false"

        vty0to4TransportLine = vtyLine[0].re_search_children(r'^\stransport input')
        if vty0to4TransportLine:
            vty0to4Transport = vty0to4TransportLine[0].text.split()
            vty0to4["transport input"] = vty0to4Transport[2]

        vtyData["0 4"] = vty0to4

        vty5to15 = {}
        if len(vtyLine) > 1:
            vty5to15PasswordLine = vtyLine[1].re_search_children(r'^\spassword')
            if len(vty5to15PasswordLine[0].text.split()) > 2:
                dp = CiscoPassword()
                decrypted_passwd = dp.decrypt(vty5to15PasswordLine[0].text.split()[2])
                vty5to15["password"] = decrypted_passwd
            else:
                vty5to15["password"] = vty5to15PasswordLine[0].text.split()[1]

            vty5to15LoginLine = vtyLine[1].re_search_children(r'^\slogin')
            if vty5to15LoginLine:
                vty5to15["login"] = "true"
            else:
                vty5to15["login"] = "false"

            vty5to15TransportLine = vtyLine[1].re_search_children(r'^\stransport input')
            if vty5to15TransportLine:
                vty5to15Transport = vty5to15TransportLine[0].text.split()
                vty5to15["transport input"] = vty5to15Transport[2]

            vtyData["5 15"] = vty5to15

        return vtyData
    else:
        return {}
    
def getConfigIPDefaultGateway(parse):
    hostnameLine = parse.find_objects(r'^ip default-gateway')
    if hostnameLine:
        hostname = hostnameLine[0].text.split()
        return hostname[2]
    else:
        return {}
    
def getLocalUserAccount(parse):
    userAccountLine = parse.find_objects(r'^username')
    if userAccountLine:
        userAccount = userAccountLine[0].text.split()
        userAccountData = {}
        userAccountData["username"] = userAccount[1]
        userAccountData[userAccount[2]] = userAccount[4]

        return userAccountData
    else:
        return {}
    
def getIPDomainLookup(parse):
    ipDomainLookupLine = parse.find_objects(r'^no ip domain lookup')
    if ipDomainLookupLine:
        return "false"
    else:
        return "true"
    
def getIPDomainName(parse):
    ipDomainNameLineForRouter = parse.find_objects(r'^ip domain name')
    ipDomainNameLineForSwitch = parse.find_objects(r'^ip domain-name')
    if ipDomainNameLineForRouter:
        ipDomainName = ipDomainNameLineForRouter[0].text.split()
        return ipDomainName[3]
    elif ipDomainNameLineForSwitch:
        ipDomainName = ipDomainNameLineForSwitch[0].text.split()
        return ipDomainName[2]
    else:
        return {}
    
def getDHCP(parse):
    DHCPData = {}

    DHCPExcludeLines = parse.find_objects(r'^ip dhcp excluded-address')
    excludedIPData = []
    if DHCPExcludeLines:
        for excludedLine in DHCPExcludeLines:
            excludedIP = excludedLine.text.split()
            if len(excludedIP) > 4:
                excludedIPData.append(excludedIP[3] + " " + excludedIP[4])
            else:
                excludedIPData.append(excludedIP[3])
        DHCPData["excluded"] = excludedIPData

    DHCPPoolLines = parse.find_objects(r'^ip dhcp pool')
    if DHCPPoolLines:
        poolArray = []
        for poolLine in DHCPPoolLines:
            poolData = {}

            poolName = poolLine.text.split()[3]
            poolData["name"] = poolName

            poolNetworkLine = poolLine.re_search_children(r'^\s+network')
            if poolNetworkLine:
                poolNetwork = poolNetworkLine[0].text.split()
                poolData["network"] = poolNetwork[1] + " " + poolNetwork[2]

            poolDefaultRouterLine = poolLine.re_search_children(r'^\s+default-router')
            if poolDefaultRouterLine:
                poolDefaultRouter = poolDefaultRouterLine[0].text.split()
                poolData["default router"] = poolNetwork[1]

            poolDNSLine = poolLine.re_search_children(r'^\s+dns-server')
            if poolDNSLine:
                poolDNS = poolDNSLine[0].text.split()
                poolData["dns"] = poolNetwork[1]

            poolArray.append(poolData)
        DHCPData["pools"] = poolArray
    
    return DHCPData

def getConfigACL(parse):
    acl_data = {}

    # Find standard named ACLs
    standard_named_acls = parse.find_objects(r'^ip access-list standard (\S+)')
    for acl in standard_named_acls:
        acl_name = acl.re_match(r'^ip access-list standard (\S+)$')
        acl_entries = acl.re_search_children(r'^\s+(permit|deny) .+')
        acl_data[acl_name] = []

        for entry in acl_entries:
            parts = entry.text.strip().split()
            action = parts[0]
            rule = ' '.join(parts[1:])
            acl_data[acl_name].append({'action': action, 'rule': rule})

    # Find extended named ACLs
    extended_named_acls = parse.find_objects(r'^ip access-list extended (\S+)')
    for acl in extended_named_acls:
        acl_name = acl.re_match(r'^ip access-list extended (\S+)$')
        acl_entries = acl.re_search_children(r'^\s+(permit|deny) .+')
        acl_data[acl_name] = []

        for entry in acl_entries:
            parts = entry.text.strip().split()
            action = parts[0]
            rule = ' '.join(parts[1:])
            acl_data[acl_name].append({'action': action, 'rule': rule})

    # Find numbered ACLs
    numbered_acls = parse.find_objects(r'^access-list \d+')
    
    numberedACL = []
    for acl in numbered_acls:
        numberedACL.append(acl.text)
    
    acl_data["numbered acl"] = numberedACL
        

    return acl_data

def getConfigNAT(parse):
    nat_data = {}

    # Find NAT configurations
    nat_lines = parse.find_objects(r'^ip nat (\S+)$')

    for nat_line in nat_lines:
        nat_type = nat_line.re_match(r'^ip nat (\S+)$')

        if nat_type == 'inside source static':
            # Static NAT (1:1 mapping)
            inside_source_static_lines = nat_line.re_search_children(r'^\sinside source static')
            static_nat_data = []

            for line in inside_source_static_lines:
                parts = line.text.strip().split()
                static_nat_data.append({
                    'inside_local': parts[3],
                    'outside_global': parts[5],
                })

            nat_data['static_nat'] = static_nat_data

        elif nat_type == 'inside source list':
            # PAT (Port Address Translation)
            inside_source_list_lines = nat_line.re_search_children(r'^\sinside source list')

            pat_data = {}

            for line in inside_source_list_lines:
                parts = line.text.strip().split()
                pat_data['access_list'] = parts[4]

                if 'interface' in parts:
                    pat_data['interface'] = True
                    pat_data['interface_name'] = parts[-1]
                else:
                    pat_data['pool'] = parts[6]

            nat_data['pat'] = pat_data

    # Find interfaces marked as inside or outside
    interface_lines = parse.find_objects(r'^interface (\S+)$')
    interface_data = {}

    for intf_line in interface_lines:
        interface_name = intf_line.re_match(r'^interface (\S+)$')
        ip_nat_lines = intf_line.re_search_children(r'^\s+ip nat (\S+)$')

        if ip_nat_lines:
            nat_type = ip_nat_lines[0].text.strip().split()[-1]
            interface_data[interface_name] = nat_type

    nat_data['interfaces'] = interface_data

    return nat_data

def getStaticRoutes(parse):
    static_routes_data = []

    # Find lines that start with 'ip route'
    static_routes_lines = parse.find_objects(r'^\s*ip route')

    for route_line in static_routes_lines:
        parts = route_line.text.strip().split()
        
        # Extract relevant information for each static route
        static_route_info = {
            'destination': parts[2],
            'mask': parts[3],
            'next_hop': parts[4],
        }

        if len(parts) > 5:
            # Additional parameters such as 'via' or 'null0'
            static_route_info['additional_params'] = ' '.join(parts[5:])

        static_routes_data.append(static_route_info)

    return static_routes_data

def getConfigVlan(parse):
    vlan_data = {}

    # Find lines that start with 'vlan'
    vlan_lines = parse.find_objects(r'^\s*vlan \d+')

    for vlan_line in vlan_lines:
        parts = vlan_line.text.strip().split()
        vlan_id = int(parts[1])

        # Extract relevant information for each VLAN
        vlan_info = {
            'vlan_id': vlan_id,
        }

        # Check if the VLAN has a name associated with it
        vlan_name_line = vlan_line.re_search_children(r'^\s+name')
        if vlan_name_line:
            vlan_name = vlan_name_line[0].text.strip().split()[-1]
            vlan_info['vlan_name'] = vlan_name

        vlan_data[vlan_id] = vlan_info

    return vlan_data





def getAllLinks(projectID, nodes):
    response = requests.get(settings.SIMULATION_SITE_DOMAIN + "v2/projects/" + projectID + "/links",
        auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))
    
    data = response.json()

    linksData = []
    for link in data:
        linkData = []

        node1ID = link["nodes"][0].get("node_id")
        for listedNode in nodes:
            if listedNode["id"] == node1ID:
                if listedNode["type"] == "router":
                    parse = views.getRouterParse(projectID, listedNode, listedNode["router counter"])
                    hostname = getConfigHostname(parse)
                    linkData.append(hostname)
                elif listedNode["type"] == "switch":
                    parse = views.getSwitchParse(projectID, listedNode)
                    hostname = getConfigHostname(parse)
                    linkData.append(hostname)
                elif listedNode["type"] == "pc":
                    pcConfig = views.getPCConfigToJSONObject(projectID, listedNode)
                    hostname = pcConfig.get('name')
                    linkData.append(hostname)
        
        node1Port =  link["nodes"][0].get("label").get("text")
        linkData.append(node1Port)

        node2ID = link["nodes"][1].get("node_id")
        for listedNode in nodes:
            if listedNode["id"] == node2ID:
                if listedNode["type"] == "router":
                    parse = views.getRouterParse(projectID, listedNode, listedNode["router counter"])
                    hostname = getConfigHostname(parse)
                    linkData.append(hostname)
                elif listedNode["type"] == "switch":
                    parse = views.getSwitchParse(projectID, listedNode)
                    hostname = getConfigHostname(parse)
                    linkData.append(hostname)
                elif listedNode["type"] == "pc":
                    pcConfig = views.getPCConfigToJSONObject(projectID, listedNode)
                    hostname = pcConfig["ip"].get('name')
                    linkData.append(hostname)
        
        node2Port =  link["nodes"][1].get("label").get("text")
        linkData.append(node2Port)

            
        linksData.append(linkData)

    return linksData
    # return data