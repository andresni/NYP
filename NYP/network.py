# -*- coding: utf-8 -*-
from . import nest_interface as nint
import yaml
import glob
from . import auxillary_functions as af
from . import output_functions as of

class network:
       
    def __init__(self,path):
        # Establishing object specific variables
        
        self.path = path
        self.path_to_network = "{}/network/".format(path)
        self.path_to_simulation = "{}/simulation/".format(path)
        self.path_to_output = "{}/output/".format(path)
        self.path_to_temp = "{}/temp/".format(path)
        
        self.parameters = dict
        self.synapses = dict
        self.layers = dict
        self.neuron_models = dict
        self.connections = dict  
        self.recorders = dict
        
        self.readYML()
        
    #######################
    # Get & Set functions #
    #######################
    def getLayers(self):
        return self.layers
    
    def getNeuronModels(self):
        return self.neuron_models
    
    def getConnections(self):
        return self.connections
    
    def getRecorders(self):
        return self.recorders
    
    def setLayers(self,dct):
        self.parameters["network"]["layers"] = dct
        
    def setSynapses(self,dct):
        self.parameters["network"]["synapses"] = dct
        
    def setNeuronModels(self,dct):
        self.parameters["network"]["neurons"] = dct
        
    def setConnections(self,dct):
        self.parameters["network"]["connections"] = dct
    
    def readYML(self):
        # Function for reading YML files, and putting them in a easy to use dictionary
        # Input: path to experiment folder containing "network" and "simulation" folders
        # Output: dictionary containing all the information from all the YML files

        yml_dict ={}
    
        config = map(lambda x: yaml.load_all(open(x)), glob.glob("{}/**/*.yml".format(self.path),recursive=True))
        
        for maps in config:
            for items in maps:
                af.merge_dicts(yml_dict,items)
                
        self.parameters = yml_dict
        
    def resetNest(self):
        nint.reset(self.parameters,self.path_to_temp,self.path_to_output)

    def initNest(self):
        nint.initialize(self.parameters,self.path_to_temp,self.path_to_output)

    def buildNetwork(self):
        self.neuron_models = nint.copy_neurons(self.parameters)
        self.layers = nint.generate_layers(self.parameters)
        self.synapses = nint.copy_synapses(self.parameters)
        self.connections = nint.generate_connections(self.parameters,self.layers)
        self.recorders = nint.generate_recorders(self.parameters,self.layers)
        
    def simulateNetwork(self):
        nint.simulate(self.parameters,self.layers,self.recorders)
        
    def produceOutput(self):
        of.output_data(self.parameters,self.layers,self.recorders,self.path_to_temp,self.path_to_output)
