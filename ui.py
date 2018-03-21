import os
from terminaltables import SingleTable
from colorclass import Color, Windows

def pc(message):
    print('{:{align}{width}}'.format(message, align='^', width='10'))


def drawTableForSwitches(switches):
    switchData = []
    switchData.append([Color('{autocyan}Switch(s){/autocyan}'), Color('{autoyellow}Termination Point(s){/autoyellow}')])
    for switch in switches:
        switchData.append([switch["node-id"], len(switch["termination-point"])])    
    table = SingleTable(switchData)
    print(table.table)


def drawTableForHosts(hosts):
    hostData = []
    hostData.append([Color('{autogreen}MAC{/autogreen}'), Color('{autoblue}IP{/autoblue}')])
    for host in hosts:
        hostData.append([host["host-tracker-service:addresses"][0]["mac"], host["host-tracker-service:addresses"][0]["ip"]])    
    table = SingleTable(hostData)
    print(table.table)

def drawPath(path):
    finalPath = Color('{autored} (START) => {/autored}')    
    for node in path:
        finalPath = finalPath + str(node) + Color('{autoyellow} => {/autoyellow}')
    finalPath = finalPath + Color('{autogreen} (END) {/autogreen}')
    print(finalPath)


def red(message):
    return Color('{autored}' + message + '{/autored}')    

def green(message):
    return Color('{autogreen}' + message + '{/autogreen}')    









def blue(message):
    return Color('{autoblue}' + message + '{/autoblue}')    

def drawPaths(paths):
    for path in paths:
        drawPath(path)


def clearScreen():
    os.system('clear')
    

def drawEdges(edges):
    edgeData = []
    count = 1
    edgeData.append([Color('{autogreen}Index{/autogreen}'), Color('{autoblue}Source{/autoblue}'), Color('{autoblue}Destination{/autoblue}')])
    for edge in edges:
        if str(edge[0]) != "None" and str(edge[1]) != "None":        
            edgeData.append([count, edge[0], edge[1]])    
            count +=1
    table = SingleTable(edgeData)
    print(table.table)
