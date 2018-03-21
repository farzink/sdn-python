import variables as settings
import db
import requests
import json
import networkx as nx
import ui as ui
import matplotlib
import matplotlib.pyplot as plt

hosts = []
switches = []
links = []
graph = nx.dodecahedral_graph()
switchPorts = dict()


def getTopologyFromController(ip):    
    path = settings.topologyPath
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
               
               
            
                #print topology['node'][1]
    #print(len(topologies))
    #print(topologies[1])
    #print(hosts[0]['host-tracker-service:addresses'][0]['ip'])
    #print(links[0])
def drawNetwork():
    global graph    
    plt.figure()    
    nx.draw_networkx(graph)
    plt.draw()
    plt.show()

def getIpByMac(macAddress):
    for host in hosts:
        if host["host-tracker-service:addresses"][0]["mac"] == macAddress:            
            return host["host-tracker-service:addresses"][0]["ip"]

def buildGraphByTable():    
    
    global graph
    graph = nx.Graph()
    tables = db.getTableNames()
    for i in range(4):        
        data = db.getTableRows(tables[i][0])
        #print(data)
        #print("-------------------------------------------------------\n")
        #print(data)
        for link in data:
            src=''
            dst=''
            if len(link.split("/")) == 2:
                if link.split(":")[0] == 'host':            
                    src = getIpByMac(link.split("host:")[1].split("/")[0].replace("[", "").replace("]", ""))
                    dst = link.split("/")[1].split(":")[1].replace("[", "").replace("]", "")
                    #print(src)
                else:                
                    src = link.split("/")[0].split(":")[1].replace("[", "").replace("]", "")
                    dst = getIpByMac(link.split("/")[1].split("host:")[1].replace("[", "").replace("]", ""))
            else:
                src = link.split(":")[1].replace("[", "").replace("]", "")
                dst = link.split(":")[2].replace("[", "").replace("]", "")
        # dst = link["destination"]["dest-tp"].encode('ascii','ignore').split(":")
        # if link["link-id"].split(":")[0] == 'host':            
        #     graph.add_edge(src,(int)(dst[1]))                
        # else:
        #     if len(link["link-id"].split("/host:")) > 1: 
        #         dst = getIpByMac((link["destination"]["dest-tp"].split("/host:")[0]).split("host:")[1])
        #         graph.add_edge((int)(src[1]),dst)
        #     else:                
        #         graph.add_edge((int)(src[1]),(int)(dst[1]))        
            graph.add_edge(src, dst)            
        #print("src: " + src + " dst:   " + dst)
    
    

def buildGraph():
    global switchPorts    
    switchPorts = dict()
    global graph
    graph = nx.Graph()    
    for link in links:
        src=''
        if link["link-id"].split(":")[0] == 'host':            
            src = getIpByMac(link["source"]["source-tp"].split("host:")[1])            
        else:
            src = link["link-id"].encode('ascii','ignore').split(":")
    
        dst = link["destination"]["dest-tp"].encode('ascii','ignore').split(":")
    
        
        if link["link-id"].split(":")[0] == 'host':
            #ip = getIpByMac(link["source"]["source-tp"].split("host:")[1])
            graph.add_edge(src,(int)(dst[1]))    
            #print("src:" + src + "   dst: " + (int)(dst[1]))
        else:
            if len(link["link-id"].split("/host:")) > 1: 
                #print(len(link["link-id"].split("/host:")))
            #link["link-id"].split("/")[1]).split(":")[0] == 'host':
                #print("------------------------")
                dst = getIpByMac((link["destination"]["dest-tp"].split("/host:")[0]).split("host:")[1])
                #dst = getIpByMac(link["destination"]["dest-tp"].split("host:")[0])
                
                #print("src:" + src + "   dst: " + (int)(dst))
                graph.add_edge((int)(src[1]),dst)
            else:
                #print("src:" + src[1] + "   dst: " + dst[1])  `                                 
                        switchPorts[str((int)(src[1])) + str((int)(dst[1]))] = str(src[2]) + ":" + str(dst[2])                
                        graph.add_edge((int)(src[1]),(int)(dst[1]))       
                        


def buildGraphByControllers(controllers):
        global switchPorts    
        switchPorts = dict()
        global graph
        graph = nx.Graph()    
        for link in links:
           src=''
           if link["link-id"].split(":")[0] == 'host':            
               src = getIpByMac(link["source"]["source-tp"].split("host:")[1])            
           else:
               src = link["link-id"].encode('ascii','ignore').split(":")

           dst = link["destination"]["dest-tp"].encode('ascii','ignore').split(":")


           if link["link-id"].split(":")[0] == 'host':
               #ip = getIpByMac(link["source"]["source-tp"].split("host:")[1])
               graph.add_edge(src,(int)(dst[1]))    
               #print("src:" + src + "   dst: " + (int)(dst[1]))
           else:
               if len(link["link-id"].split("/host:")) > 1: 
                   #print(len(link["link-id"].split("/host:")))
               #link["link-id"].split("/")[1]).split(":")[0] == 'host':
                   #print("------------------------")
                   dst = getIpByMac((link["destination"]["dest-tp"].split("/host:")[0]).split("host:")[1])
                   #dst = getIpByMac(link["destination"]["dest-tp"].split("host:")[0])

                   #print("src:" + src + "   dst: " + (int)(dst))
                   graph.add_edge((int)(src[1]),dst)
               else:
                   #print("src:" + src[1] + "   dst: " + dst[1])  `
                   for controller, v in controllers.items():
                           if v.isSwitchInMyDomain(src[1]) and v.isSwitchInMyDomain(dst[1]):            
                               switchPorts[str((int)(src[1])) + str((int)(dst[1]))] = str(src[2]) + ":" + str(dst[2])                
                               graph.add_edge((int)(src[1]),(int)(dst[1]))       
                               break
    #print("------------------------------------")
    #print(switchPorts)
    #print(graph.edges) 
    #graph.add_edges_from(links)
    


def getShortestPathFor(src, des):
    global graph
    global switchPorts
    src = settings.getIpByLastSection(str(src));
    des = settings.getIpByLastSection(str(des));
    paths = nx.all_shortest_paths(graph, source=src, target=des)  
    #print(graph.edges)             
    
    tempPaths = paths
    #for path in tempPaths:
    #    ui.drawPath(path)
    
    
    
    
    
    
    #pushPath(tempPaths)     
    

    
    return paths


def pushPath(paths):
    global switchPorts
    for path in paths:
        host1 = path[0].split(".")
        host2 = path[-1].split(".")
        host2Ip = path[-1]
        del path[0]
        del path[-1]
        sws = len(path)
        sw = 0
        while sw + 1 < sws:
            sw1 = path[sw]
            sw2 = path[sw + 1]
            print("--------------------------------")
            print(path)
            print(host1)
            print(host2)
            print(sw1)
            print(sw2)
            print(switchPorts[str(sw1)+str(sw2)])
            print("--------------------------------")
            lports = switchPorts[str(sw1)+str(sw2)].split(":")
            desMac = "00:00:00:00:00:" + '{:02d}'.format(int(host2[3]))
            desIp = "00:00:00:00:00:" + '{:02d}'.format(int(host2[3]))
            content = generateJsonForPush(str(lports[1]), desMac, desIp + "/24")
            #print(content)
            print(pushFlow(content))
            sw = sw+1
        
        
        



def createTopology():    
    for address in settings.topologyAddresses:
        getTopologyFromController(address)    

def reset():
    global hosts
    global switches
    global links
    hosts = []
    switches = []
    links = []




def getEdges():
    global graph
    edges = []
    for edge in graph.edges:
        #print(edge[1])
        edges.append({ "edge": [ edge[0], edge[1]] })
    return edges

def applyLayerTwoLinks():
    global graph
    global switchPorts    
    for link in settings.layerTwoLinks:      
        #switchPorts[str(link['first']) + str(link['second'])] = "44"
        graph.add_edge(link['first'], link['second'])

def getSwitches():
    switchData = []
    for switch in switches:
        switchData.append([switch["node-id"], len(switch["termination-point"])])
    return switchData

def getHosts():
    hostData = []    
    for host in hosts:
        hostData.append([host["host-tracker-service:addresses"][0]["mac"], host["host-tracker-service:addresses"][0]["ip"]])        
    return hostData

def generateXmlForPush(sourceMac, destinationMac):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory">'
        '<strict>false</strict><instructions><instruction><order>0</order><apply-actions><action>'
        '<order>0</order><dec-mpls-ttl/></action></apply-actions></instruction></instructions><table_id>0</table_id>'
        '<id>1</id><cookie_mask>255</cookie_mask><installHw>false</installHw><match><ethernet-match><ethernet-type>'
        '<type>0x8847</type></ethernet-type><ethernet-destination><address>' + destinationMac + '</address></ethernet-destination>'
        '<ethernet-source><address>' + sourceMac + '</address></ethernet-source></ethernet-match></match><hard-timeout>12</hard-timeout>'
        '<cookie>4</cookie><idle-timeout>34</idle-timeout><flow-name>MYMACFLOW</flow-name><priority>2</priority><barrier>false</barrier>'
        '</flow>')

def pushFlow(content):
    path = settings.pushPath
    result = requests.put(path, headers=settings.pushHeader, auth=settings.auth, data=content)
    return result


def generateJsonForPush(portNumber, destinationIp, destinationSubnet):
    #bodyToPush = '{ "flow": { "instructions": { "instruction": { "order": "0", "apply-actions":{ "action":[{"order": "0", "output-action": {"output-node-connector": "' + portNumber +'"}}]}}}, "table_id": "0", "id": "1", "match": { "ethernet-match": { "ethernet-type": {"type": "2048"}, "ethernet-destination": {"address": "' + destinationMac +'"} }, "ipv4-destination": "' + destinationSubnet + '"}, "flow-name": "path"}}'
    bodyToPush = '{ "flow": { "instructions": { "instruction": { "order": "0", "apply-actions":{ "action":[{"order": "0", "output-action": {"output-node-connector": "' + portNumber +'"}}]}}}, "table_id": "0", "id": "1", "match": { "ethernet-match": { "ethernet-type": {"type": "2048"}}, "ipv4-destination": "' + destinationIp + '/24"}, "flow-name": "path"}}'
    return bodyToPush




# return ('\'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>'
#         '<flow xmlns=\"urn:opendaylight:flow:inventory\"><priority>32767</priority><flow-name>flow1</flow-name><match>'
#         '<in-port>' + sourceP + '</in-port><ipv4-destination>' + destination + '/32</ipv4-destination>'
#         '<ipv4-source>' + source +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type>'
#         '</ethernet-match></match><id>2</id><table_id>0</table_id>'
#         '<instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action>'
#         '<output-node-connector>' + destinationP + '</output-node-connector></output-action></action>'
#         '</apply-actions></instruction></instructions></flow>\'')