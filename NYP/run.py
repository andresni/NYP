# -*- coding: utf-8 -*-
from . import network
from . import nest_interface as nint

########################
# Various Sub routines #
########################
        
def mainAll(path):
    net = mainBuild(path)
    mainSim(net)
    mainOutput(net)
    mainClean(net)
    
    return net

def mainBuild(path):
    net = network.network(path)
    net.initNest()
    net.buildNetwork()
    nint.print_net_information()
    
    return net

def mainSim(net):
    net.simulateNetwork()

def mainOutput(net): 
    net.produceOutput()
    
def mainClean(net):
    net.resetNest()