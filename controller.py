import variables as settings
import requests
import json
import networkx as nx
import ui
import network as network

class Controller:

    

    

    def __init__(self, ip):
        self.ip = ip;
        self.controllerAddress = ip
        self.init()        
        self.id =55
        self.neighbours = [];
        self.borderGateways = [];
        



    def init(self):            
        self.switchPorts = dict()            
        self.domainSwitchPorts = dict()            
        self.hosts = []
        self.switches = []
        self.links = []
        self.routeTable = dict()        
        self.graph = ""
        self.getTopologyForThisController(self.controllerAddress)
        self.controllerGraph()


    def calculateBorderGateways(self):
        
        for neighbour in self.neighbours:            
            
            ns = self.identifyBorderSwitch(neighbour)
            
            s1, s2 = ns['switch'].split("|")                    
            if self.isSwitchInMyDomain(s1):
                self.borderGateways.append(s1)                
            if self.isSwitchInMyDomain(s2):
                self.borderGateways.append(s2)                
                


    def setNeighbours(self, neighbours):
        self.neighbours = neighbours
        self.calculateBorderGateways()
        

    def getNeighbours(self):
        return self.neighbours;



    def internalShortestPath(self, switchInCharge, source, destination):
        paths = self.localShortestPathFor(source, destination)
        for path in paths:
            print(path)


    def resolvePathByDomain(self, initiator, domainInCharge, source, destination, accumulatedPath=[], nd = 0):      
                            
        if self.isHostInMyDomain(settings.getIpByLastSection(destination)):
            
            
            
            
            if self.isHostInMyDomain(settings.getIpByLastSection(destination)) and self.isHostInMyDomain(settings.getIpByLastSection(source)):
                for path in initiator.localShortestPathFor(source, destination):
                   initiator.resolvePathDone(initiator, initiator, source, destination, accumulatedPath + path);
                   
                
            else:                          
                switch = self.identifyBorderSwitch(domainInCharge)

                s1, s2 = switch['switch'].split("|")
                paths = ""
                if self.isSwitchInMyDomain(s1):
                    paths = self.localShortestPathForSwitchToHost(int(s1), destination)
                if self.isSwitchInMyDomain(s2):
                    paths = self.localShortestPathForSwitchToHost(int(s2), destination)
                for path in paths:                         
                    initiator.resolvePathDone(initiator, initiator, source, destination, accumulatedPath + path, nd)   
                

                #return self.internalShortestPath("", source, destination)
        else:
            
            
            
                

                

            
                
            for neighbour in self.neighbours:
                
                if self.isHostInMyDomain(settings.getIpByLastSection(source)):
                        accumulatedPath = [] 
                        switch = self.identifyBorderSwitch(neighbour)
                        paths = ""
                        s1, s2 = switch['switch'].split("|")
                        if self.isSwitchInMyDomain(s1):
                            paths = self.localShortestPathForSwitchToHost(int(s1), source)                    
                        if self.isSwitchInMyDomain(s2):
                            paths = self.localShortestPathForSwitchToHost(int(s2), source)                    
                        for path in paths:
                            accumulatedPath = path[::-1] + accumulatedPath
                            break;
                
                
            
                if domainInCharge.controllerAddress != neighbour.controllerAddress and neighbour.controllerAddress!=initiator.controllerAddress:                    


                    




                    if neighbour.isHostInMyDomain(settings.getIpByLastSection(destination)):
                        
                        neighbour.resolvePathByDomain(initiator, self, source, destination, accumulatedPath, nd + 1)
                        
                    

                    else:
                        ns = self.identifyBorderSwitch(neighbour)['switch'].split("|")[0]
                        
                        nx = -1
                        for b in neighbour.borderGateways:
                            if b != ns:
                                nx=b
                                break
                        
                        paths = neighbour.localShortestPathForSwitchToSwitch(int(nx), int(ns))                    
                                             
                        for path in paths:
                            
                            neighbour.resolvePathByDomain(initiator, self, source, destination, accumulatedPath + path[::-1], nd +1)
                            #accumulatedPath + path[::-1]
                            break;
                        
                        
                
        
    def resolvePathDone(self, initiator, domainInCharge, source, destination, accumulatedPath=[], nd=0):                      
        
        print(accumulatedPath)
        print("domain(s): " + str(nd) + ", no of switche(s): " + str(len(accumulatedPath) - 2))  
        print("========================================================")      
        #return accumulatedPath 

  

    def identifyBorderSwitch(self, domainOfInterest):    
        
        for s1, v1 in self.domainSwitchPorts.items():  
            p1, p2 = s1.split("|")          
            s3 = p2 + "|" + p1
            for s2, v2 in domainOfInterest.domainSwitchPorts.items():                                                
                if s1 == s2 or s2==s3:
                    return {
                        "switch": s1,
                        "link": v1
                }




    def receiveForPush(self, paths):  
        print(ui.green("Controller " + self.controllerAddress))
        print(self.ip + ": received for push.")
        print(paths)
        pathOfInterest = self.identifyThisControllerPart(paths)
        print(pathOfInterest)
        source = paths[0][0]
        destination = paths[0][-1]
        print("Source: " + source)
        print("Destination: " + destination)


        for poi, v in pathOfInterest.items():
            self.checkRouteAndPush(source, destination, v);



        

    
    
    
    
    def checkRouteAndPush(self, source, destination, path):
        counter = 1
        while counter < len(path):
            routeKey = str(path[counter-1]) + "-" + str(path[counter]) + "-" + destination # e.g. 1-8-192.180.7.9 
            if(self.checkRoute(routeKey) != True):
                ui.green("route is being added...")
                self.addRoute(routeKey)
                self.pushPath(routeKey)

            else:
                ui.red("route currently exists")
                
            counter = counter + 1

        
        #self.queryRoutes()
        #self.pushPath(pathOfInterest, destination)
        print(self.switchPorts)
        print(ui.red("--------------------------------------"))



    def getPushPath(self, switch, id):
        return settings.pushPath_1 + self.getControllerAddress() + settings.pushPath_2 + switch + settings.pushPath_3 + str(id)

    def queryRoutes(self):      
        print(ui.green("-----current route table------"))  
        for route in self.routeTable:
            print(route)
        

    def getControllerAddress(self):
        return self.controllerAddress

    def identifyThisControllerPart(self, paths):
        switches = dict()        
        counter = 1;
        #print(self.switches)        
        
        for path in paths:
            s = [];
            flag = False
            for switch in path:                
                if self.isSwitchInMyDomain(str(switch)) or flag == True:
                    s.append(switch)
                    flag = True
                    if not self.isSwitchInMyDomain(str(switch)):
                        flag = False
                else:
                    flag = False

            switches[counter] = s;
            counter = counter + 1            
        return switches    
        


    def checkRoute(self, route):        
        for currentRoute in self.routeTable.keys():
            if route  == currentRoute:
                return True
        return False

    def addRoute(self, routeKey):        
        #source = route.split('-')[0]
        #destination = route.split('-')[1]
        self.routeTable[routeKey] = { "source" : "", "destination": "" }


    def updateRoute(self, route):         
        for currentRoute in self.routeTable.keys():
            if route  == currentRoute:
                source = route.split('-')[0]
                destination = route.split('-')[1]
                self.routeTable[route] = { "source" : source, "destination": destination }
                return True

        return False;



    def isHostInMyDomain(self, address):
        
        for host in self.hosts:        
            if host["host-tracker-service:addresses"][0]["ip"] == address:            
                return True
        return False



    def isSwitchInMyDomain(self, switch):        
        
        for sw in self.switches:          
            if sw["node-id"].split(":")[1] ==  switch:
                return True
        return False




    def removeRoute(self, route):        
        del self.routeTable[route]

    

    def recognizePortConfiguration(self, switch1, switch2):
        config = "";
        comb1 = switch1 +  switch2
        comb2 = switch2 +  switch1
        for k, v in self.switchPorts.items():
            if k == comb1:
                config = v.split(":")[0]
                break
            if k == comb2:
                config= v.split(":")[1]
                break
        return config


    def pushPath(self, path):
        switch1 = path.split("-")[0]
        switch2 = path.split("-")[1] 
        destination = path.split("-")[2]  
        linkConfig = self.recognizePortConfiguration(switch1, switch2)

        #print("-----------------------" + str(self.ipToMac(destination)))
        json = self.generateJsonForPush(linkConfig, destination, path, self.id, str(self.ipToMac(destination)))
        #print(json)
        #print("ports are =================== > >" + linkConfig + "----------------" + switch1)
        print(self.pushFlow(switch1, json, self.id))



       
        return True;
    

    def linkForPush():
        print()

    #this will be modified and customized later on based on the requirement(s)
    def spannigTreeHendler(self, route):
        return True


    def pushFlow(self, switch, content, id):
        path = self.getPushPath(switch, id)
        print("push path -----------" + path)
        result = requests.put(path, headers=settings.pushHeader, auth=settings.auth, data=content)
        return result


    def generateJsonForPush(self, portNumber, destinationIp, pathName, id, destinationMac):
        priority = 54200        
        if self.isHostInMyDomain(str(destinationIp)):            
            bodyToPush = '{ "flow": { "instructions": { "instruction": { "order": "0", "apply-actions":{ "action":[{"order": "1", "output-action": {"output-node-connector": "' + portNumber +'"}},{"order": 0, "set-dl-dst-action": {"address": "' + destinationMac +'"}}]}}}, "table_id": "0", "id": "' + str(id) + '", "match": { "ethernet-match": { "ethernet-type": {"type": "2048"}}, "ipv4-destination": "' + destinationIp + '/32"}, "priority": "' + str(priority) + '", "flow-name": "' + pathName + '"}}'
        else:
            bodyToPush = '{ "flow": { "instructions": { "instruction": { "order": "0", "apply-actions":{ "action":[{"order": "0", "output-action": {"output-node-connector": "' + portNumber +'"}}]}}}, "table_id": "0", "id": "' + str(id) + '", "match": { "ethernet-match": { "ethernet-type": {"type": "2048"}}, "ipv4-destination": "' + destinationIp + '/32"}, "priority": "' + str(priority) + '", "flow-name": "' + pathName + '"}}'
        return bodyToPush



    def getTopologyForThisController(self, ip):            
        path = settings.topologyPath
        result = requests.get(settings.getTopologyPath(ip), headers=settings.header, auth=settings.auth)        
        topologies = result.json()['network-topology']['topology']
        for topology in topologies:        
            if 'node' in topology:
                for node in topology['node']:
                    if node['node-id'].split(':')[0] == 'host':
                        self.hosts.append(node)
                    if node['node-id'].split(':')[0] == 'openflow':
                        self.switches.append(node)
            if 'link' in topology:
                for link in topology['link']:
                    self.links.append(link)



    def macToIp(self, macAddress):        
        for host in self.hosts:        
            if host["host-tracker-service:addresses"][0]["mac"] == macAddress:            
                return host["host-tracker-service:addresses"][0]["ip"]

    def ipToMac(self, ipAddress):        
        for host in self.hosts:        
            if host["host-tracker-service:addresses"][0]["ip"] == ipAddress:            
                return host["host-tracker-service:addresses"][0]["mac"]




    def controllerGraph(self):          
        self.switchPorts = dict()        
        self.domainSwitchPorts = dict()        
        self.graph = nx.Graph()    
        for link in self.links:
            src=''
            if link["link-id"].split(":")[0] == 'host':           
                #this needs to be changed 
                src = self.macToIp(link["source"]["source-tp"].split("host:")[1])            
            else:
                src = link["link-id"].encode('ascii','ignore').split(":")

            dst = link["destination"]["dest-tp"].encode('ascii','ignore').split(":")


            if link["link-id"].split(":")[0] == 'host':
                
                self.graph.add_edge(src,(int)(dst[1]))    

            else:
                if len(link["link-id"].split("/host:")) > 1: 
                    
                    #this needs to be changed
                    dst = self.macToIp((link["destination"]["dest-tp"].split("/host:")[0]).split("host:")[1])                

                    self.switchPorts[str((int)(src[1])) + str(dst)] = str(src[2]).split("/")[0] + ":" + str(0)                
                    self.domainSwitchPorts[str((int)(src[1])) + "|" + str(dst)] = str(src[2]).split("/")[0] + ":" + str(0)                

                    self.graph.add_edge((int)(src[1]),dst)
                else:

                    self.switchPorts[str((int)(src[1])) + str((int)(dst[1]))] = str(src[2]) + ":" + str(dst[2])                
                    self.domainSwitchPorts[str((int)(src[1])) + "|" + str((int)(dst[1]))] = str(src[2]) + ":" + str(dst[2])                
                    self.graph.add_edge((int)(src[1]),(int)(dst[1]))       





    def validatePath(self, path):
        pathOfInterest = self.identifyControllerPath(path)  
        
        if len(pathOfInterest) == 0:
            return True    
        counter = 1
        nextSwitch = 0
        previousSwitch = 0
        for switch in pathOfInterest:
            if len(str(switch).split(".")) != 1:                
                return True

            #a pth can not be started from a switch in other domain    
            
            if previousSwitch == 0 and not self.isSwitchInMyDomain(str(switch)):                             
                return False

            
            if len(pathOfInterest) >= counter:
                nextSwitch = pathOfInterest[counter]            
                counter = counter + 1
            else:
                return True            
            if len(str(nextSwitch).split(".")) != 1:                
                return True

            if not self.isSwitchInMyDomain(str(nextSwitch)):
                if self.isPathBetweenDomains(switch, nextSwitch):
                    return True
                else:                                  
                    return False
            previousSwitch = switch
        
                   


    def isPathBetweenDomains(self, switch1, switch2):
        comb1 = str(switch1) + str(switch2)
        comb2 = str(switch2) + str(switch1)
        for combinations in settings.layerTwoLinkPorts:
            if combinations == comb1 or combinations == comb2:
                return True
        return False

    def identifyControllerPath(self, path):
        

        
        s = [];
        flag = False
        for switch in path:                
                if self.isSwitchInMyDomain(str(switch)) or flag == True:
                    s.append(switch)
                    flag = True
                    if not self.isSwitchInMyDomain(str(switch)):
                        flag = False
                else:
                    flag = False           
            
        return s

    

    def localShortestPathFor(self, src, des):        
        src = settings.getIpByLastSection(str(src));
        des = settings.getIpByLastSection(str(des));
        return nx.all_shortest_paths(self.graph, source=src, target=des)  


    def localShortestPathForSwitchToHost(self, source, des):                
        des = settings.getIpByLastSection(str(des));
        return nx.all_shortest_paths(self.graph, source=source, target=des) 

    def localShortestPathForSwitchToSwitch(self, source, des):                        
        return nx.all_shortest_paths(self.graph, source=source, target=des)  

    def getHosts(self):        
        return self.hosts

    def getLinks(self):        
        return self.links

    def getSwitches(self):        
        return self.switches


    def getSwitchPorts(self):
        return self.switchPorts
    
    