topologyPath = ':8181/restconf/operational/network-topology:network-topology'
#pushPath = 'http://10.2.2.128:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/table/0/flow/1'
pushPath_1 = 'http://'
pushPath_2 = ':8181/restconf/config/opendaylight-inventory:nodes/node/openflow:'
pushPath_3 = '/table/0/flow/'




tcsDbName = 'CONTROLLER_TOPOLOGY_DATABASE'
tcsDbPath ='/home/tcs/sdni/database/'
topologyAddresses = ['10.2.2.128', '10.2.2.129', '10.2.2.130', '10.2.2.131']
ipBase = '192.168.'
header = {'content-type': 'application/json'}
pushHeader = {'content-type': 'application/json'}

layerTwoLinks = [
    dict(first= 2, second= 5),
    dict(first= 6, second= 7),
    dict(first= 8, second= 12),
    dict(first= 10, second= 3)  
]


#output from switch 2 (port 4) to switch 5 (port 4)

layerTwoLinkPorts = [
    "25",
    "67",
    "812",
    "310"
]




auth=('admin', 'admin')

def getTopologyPath(ip):
    return 'http://' + ip + topologyPath
def getIpByLastSection(last):
    return ipBase + last



