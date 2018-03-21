import variables as settings
import db
import requests
import json
import networkx as nx
import ui as ui
hosts = []
switches = []
links = []
global graph
switchPorts = dict()

localSwitches = dict()
localHosts = dict()

def init():
    for address in settings.topologyAddresses:
        getTopologyFromController(address)
    








def isHostMyRoutingTable(targetSwitch, hostAddress):
    routes = targetSwitch['routes']
    for route in routes:
        #print(route['destinationNode'])
        if route['destinationNode'] == hostAddress:
            return True
    return False 






def isHostInMyDomain(targetDomain, hostAddress):
    for switch in targetDomain:        
        if isHostMyRoutingTable(targetDomain[switch], hostAddress):
            return True
    return False












def macToIp(macAddress):        
    for host in hosts:        
        if host["host-tracker-service:addresses"][0]["mac"] == macAddress:            
            return host["host-tracker-service:addresses"][0]["ip"]





def getLocalSwitchesByController(ip):
    
    
    _switches = dict()
    path = settings.topologyPath
    print(settings.getTopologyPath(ip))
    result = requests.get(settings.getTopologyPath(ip), headers=settings.header, auth=settings.auth)
    topologies = result.json()['network-topology']['topology']
    for topology in topologies:        
        if 'node' in topology:
            for node in topology['node']:
                #if node['node-id'].split(':')[0] == 'host':
                #    hosts.append(node)
                if node['node-id'].split(':')[0] == 'openflow':
                    n = dict()
                    n["switch"] = node['node-id']
                    n["isBorderGateway"] = False
                    n["routes"] = []
                    node_id = node['node-id']
                    _switches[node_id] = n
                    #_switches.append(dict (["switch": node['node-id'], "isBorderGateway": False, "routes": []])        
    localSwitches[ip] = _switches



def getLocalHostsByController(ip):
    
    
    _hosts = []
    path = settings.topologyPath
    print(settings.getTopologyPath(ip))
    result = requests.get(settings.getTopologyPath(ip), headers=settings.header, auth=settings.auth)
    topologies = result.json()['network-topology']['topology']
    for topology in topologies:        
        if 'node' in topology:
            for node in topology['node']:
                if node['node-id'].split(':')[0] == 'host':
                    _hosts.append({ "mac" : node['node-id'], "ip": macToIp(node['node-id'].split('host:')[1])})
                
    localHosts[ip] = _hosts

#LE => local and External
def setSwitchsLEConnections(ip):
    global localSwitches
    result = requests.get(settings.getTopologyPath(ip), headers=settings.header, auth=settings.auth)
    topologies = result.json()['network-topology']['topology']
    for topology in topologies:
        if 'link' in topology:
            for link in topology['link']:
                if link['link-id'].split(":")[0] == 'openflow':
                    linkId = link['link-id']
                    destinationNode = link['destination']['dest-node']
                    if len(destinationNode.split("host:")) > 1:                        
                        destinationNode = macToIp(destinationNode.split("host:")[1])
                    destinationTp = link['destination']['dest-tp']
                    sourceNode = link['source']['source-node']
                    sourceTp = link['source']['source-tp']
                    openflowId = link['link-id'].split(":")[0] + ":" + link['link-id'].split(":")[1]
                    #print(link)
                    if openflowId in localSwitches[ip]:
                        localSwitches[ip][openflowId]['routes'].append(dict ({
                            "linkid": linkId,
                            "destinationNode": destinationNode,
                            "destinationTp": destinationTp,
                            "sourceNode": sourceNode,
                            "sourceTp": sourceTp
                        }))
                    else:
                      openflowId = link['destination']['dest-node'].split(":")[0] + ":" + link['destination']['dest-node'].split(":")[1]
                      sourceNode = link['destination']['dest-node']
                      destinationNode = link['source']['source-node']
                      if len(destinationNode.split("host:")) > 1:                        
                        destinationNode = macToIp(destinationNode.split("host:")[1])
                      localSwitches[ip][openflowId]['routes'].append(dict ({
                            "linkid": link['destination']['dest-tp'],
                            "destinationNode": destinationNode,
                            "destinationTp": link['source']['source-tp'],
                            "sourceNode": sourceNode,
                            "sourceTp": link['destination']['dest-tp']
                        }))
                    #print(destinationNode)
                    #print(str(destinationNode).split(":")[0])
                    if str(destinationNode).split(":")[0] == "openflow":                        
                        if destinationNode not in localSwitches[ip]:                            
                            localSwitches[ip][openflowId]["isBorderGateway"]  = True
                    



   # print(localSwitches[ip].keys())
    #print(localSwitches[ip]['openflow:3']["isBorderGateway"])
    # for dest in localSwitches[ip]['openflow:3']["routes"]:
    #     print(dest['destinationNode'])
    



#for dest in localSwitches[ip]['openflow:3']["routes"]:
    #     print(dest['destinationNode'])

def getTopologyFromController(ip):    
    path = settings.topologyPath
    #print(settings.getTopologyPath(ip))
    result = requests.get(settings.getTopologyPath(ip), headers=settings.header, auth=settings.auth)
    topologies = result.json()['network-topology']['topology']
    for topology in topologies:        
        if 'node' in topology:
            for node in topology['node']:
                if node['node-id'].split(':')[0] == 'host':
                    hosts.append(node)
                if node['node-id'].split(':')[0] == 'openflow':
                    switches.append(node)
        if 'link' in topology:
            for link in topology['link']:
                links.append(link)



def main():
    global localSwitches
    global localHosts
    init()
    ui.drawTableForHosts(hosts)
    localSwitches = dict()    
    localHosts = dict()
    for address in settings.topologyAddresses:
        getLocalSwitchesByController(address)    
        getLocalHostsByController(address)    
        
    #print(localHosts["10.2.2.131"])
    for switch in localSwitches:
        setSwitchsLEConnections(switch)
        break
    

    #print(localSwitches["10.2.2.128"])
    #print(isHostMyRoutingTable(localSwitches["10.2.2.128"]["openflow:2"], "192.168.2.2"))
    print(isHostInMyDomain(localSwitches["10.2.2.128"], "192.168.2.2"))
main()