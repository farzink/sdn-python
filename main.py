import variables as settings
import ui as ui
import db
import network
import controller as c
import copy
import wx
import face
import collections



controllers = dict()


def inittializeControllers():
    for address in settings.topologyAddresses:         
         controllers[address] = c.Controller(address)
    
    counter = 0
    totalControllers = 4
    for controller, v in collections.OrderedDict(sorted(controllers.items())).items():
        n1 = counter - 1
        n2 = counter + 1
        if n2 >= totalControllers:
            n2 = 0
        # print(n1, n2)
        # print(v.controllerAddress)
        v.setNeighbours([
             controllers[settings.topologyAddresses[n1]], controllers[settings.topologyAddresses[n2]]
         ])
        counter = counter + 1
        #v.calculateBorderGateways()
        #v.resolvePathByDomain(controllers["10.2.2.130"], "3.5", "4.7")
        
        #print(v.getSwitchPorts())
        #print(controllers[settings.topologyAddresses[n1]].getSwitchPorts())
        #print(v)
        #print(settings.topologyAddresses[n1], settings.topologyAddresses[n2])
        #print("|||||||||||||||||||||||||||||||||||||||||||||||||") 
        
    print("neighbours...")
    paths = controllers["10.2.2.128"].resolvePathByDomain(controllers["10.2.2.128"], controllers["10.2.2.128"], "2.1", "3.6", [])
    #print(paths)
    #print(controllers["10.2.2.128"].neighbours)
    #print(controllers["10.2.2.128"].borderGateways)
    #for path in paths:
     #  print(path)


def checkControllerSwitches():    
    for controller, v in controllers.items():                 
         ui.drawTableForSwitches(v.getSwitches())  


def checkControllerHosts():    
    for controller, v in controllers.items():         
         ui.drawTableForHosts(v.getHosts())                                  


def distributePathForPush(paths):    
    for controller, v in controllers.items():                      
        v.receiveForPush(paths)  
     
    # print(type(p))       
    # controllers["10.2.2.128"].receiveForPush(p)
    # controllers["10.2.2.129"].receiveForPush(p)
    return True


def eligiblePaths(paths):
    p = []
    pp = []
    for path in paths:
        
        p.append(path)
    #del p[0]
    #del p[-1]
    
    for path in p:            
        counter = 0
        
        for controller, v in controllers.items():
            
            print(path)
            if v.validatePath(path):                
                counter = counter + 1
            
            if counter == 4:
                
                pp.append(path)
        counter = 1

    return pp


def init():    





    ui.clearScreen()
    print(ui.blue("-------------application start-------------"))





    l = inittializeControllers();
    
    
    #checkControllerSwitches();
    
    
    #network.createTopology()

    



    ui.pc("...Getting Topology Info...")      


    network.createTopology()
    #network.buildGraphByControllers(controllers)
    network.buildGraph()
    
    #network.drawNetwork()
    
    #network.applyLayerTwoLinks()    


    #paths = network.getShortestPathFor("3.6", "2.1")
    
    
    paths = network.getShortestPathFor("2.1", "2.2")
    eps = eligiblePaths(paths)
    ui.drawPaths(eps)
    
    
    
    #ui.drawPaths(network.getShortestPathFor("2.1", "3.4"))

    #distributePathForPush(eps)




    # paths = network.getShortestPathFor("2.1", "4.8")
    # ui.drawPaths(network.getShortestPathFor("2.1", "4.8"))

    # distributePathForPush(paths)



    # paths = network.getShortestPathFor("2.1", "4.8")
    # ui.drawPaths(network.getShortestPathFor("2.1", "4.8"))

    # distributePathForPush(paths)






    #ui.drawTableForSwitches(network.switches)
    #ui.drawTableForHosts(network.hosts)
    
    
    
    
    #db.prepareConnection()    
    #network.buildGraphByTable()
    #ui.drawEdges(network.getEdges())
    
    #network.applyLayerTwoLinks()    
    #ui.drawEdges(network.getEdges())
    #ui.pc("...Calculating Shortest Paths...")
    #for path in network.getShortestPathFor("2.1", "2.3"):
        #   print(path)
    
    

#init()

def test():
    content = network.generateJsonForPush("2", "00:00:00:00:00:06", "255.255.255.0/24")
    print(content)
    print(network.pushFlow(content))



#init();














class Application(face.Frame): 
   def __init__(self,parent): 
      face.Frame.__init__(self,parent)  
      self.init()


   def init(self):
        self.m_button1.Bind(wx.EVT_BUTTON, self.button1Clicked)
        self.m_button2.Bind(wx.EVT_BUTTON, self.button2Clicked)

   def button1Clicked(self, sender):
        #print(self.m_comboBox1.GetValue())
        ui.clearScreen()
        print(ui.blue("-------------application start-------------"))

        l = inittializeControllers(); 
        #checkControllerSwitches()
        
        ui.pc("...Getting Topology Info...")
        network.createTopology()        
        network.buildGraph()    
        
        
        paths = network.getShortestPathFor(self.m_comboBox2.GetValue(), self.m_comboBox1.GetValue())
        eps = eligiblePaths(paths)
        ui.drawPaths(eps)
        distributePathForPush(eps)


   def button2Clicked(self, sender):
        l = inittializeControllers(); 
        network.createTopology()        
        network.buildGraph()    
        network.drawNetwork()


inittializeControllers()
app = wx.App(False) 
frame = Application(None) 
frame.Show(True) 
#start the applications 
app.MainLoop() 