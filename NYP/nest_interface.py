# -*- coding: utf-8 -*-
import nest
import nest.topology
import numpy as np
from . import auxillary_functions as af
import copy
import os
import sys

def reset(p,path_to_temp,path_to_output):
    # Function for resetting NEST after simulations to save system memory. To save disk space as well, use reset=True.
    # Input: path to experiment folder, parameters from YML files, and optionally reset=True)

    files = os.listdir(path_to_temp)
    
    for f in files:
        try:
            os.remove(path_to_temp + "/" + f)
        except Exception as e:
            print(e)
            
    files = os.listdir(path_to_output)
    out = path_to_output + "/" + p["simulation"]["output"]["data"]["save"]["name"] + "/"
    if not os.path.isdir(out):
        os.makedirs(out)
    for f in files:
        try:
            if os.path.isfile(os.path.join(path_to_output,f)):
                os.rename(path_to_output + "/" + f,out + f)
        except Exception as e:
            print(e)
    
    nest.ResetKernel()
    nest.ResetNetwork()


def initialize(p,path_to_temp,path_to_output):
    # Function for initializing the NEST engine for simulation, including setting randomization seed
    # Input: input parameters from YML files, path to experiment folder

    if not os.path.isdir(path_to_temp):
        os.makedirs(path_to_temp)

    if not os.path.isdir(path_to_output):
        os.makedirs(path_to_output)
        
    reset(p,path_to_temp,path_to_output)

    p["nest_parameters"]["nest_initialization"]["data_path"] = path_to_temp
    nest.SetKernelStatus(p["nest_parameters"]["nest_initialization"])
    
    if p["nest_parameters"]["nest_other"]["randomize"]:
        msd = np.random.randint(100000,999999)
    else:
        msd = p["nest_parameters"]["nest_other"]["rand_seed"]
        
    N_vp = nest.GetKernelStatus(["total_num_virtual_procs"])[0]
    pyrngs = [np.random.RandomState(s) for s in range(msd,msd+N_vp)]
    nest.SetKernelStatus({"grng_seed":msd+N_vp, "rng_seeds":range(msd+N_vp+1,msd+2*N_vp+1)})
    
def copy_neurons(p):
    # Function for copying new models from network/neurons.yml into NEST engine
    # Input: input parameters from YML files
    # Output: list of new models
    
    models = []
    
    for i in p["network"]["neurons"]:
        models.append((i["type"], i["name"], i["parameters"]))
        nest.CopyModel(i["type"], i["name"], i["parameters"])
        
    return models

def generate_layers(p):
    # Function for creating layers as specified in network/layers.yml
    # Input: input parameters from YML files
    # Output: list of layers
    
    layers = {}
    
    for i in p["network"]["layers"]:
        try:
            layers[i["name"]] = [nest.topology.CreateLayer(i["parameters"]),i["parameters"]["elements"]]
        except:
            print("There's something wrong with the following layer definition:")
            print("{}".format(i))

    return layers

def copy_synapses(p):
    # Function for copying synapse models into NEST engine, from network/synapses.yml
    # Input: input parameters from YML files
    # Output: list of layers
    
    for i in p["network"]["synapses"]:
            nest.CopyModel(i["type"],i["name"],i["parameters"])
                
def generate_connections(p,layers):
    # Function for connecting nodes of the network
    # Input: input parameters from YML files, list of layers
    # Ouput: list of connections
    
    conns = []
    
    
    for c in p["network"]["connections"]:
        for z in range(len(c["source_area"])):
            prefix_source = c["source_area"][z] if not c["source_area"][z] ==  "none" else ""
            prefix_target = c["target_area"][z] if not c["target_area"][z] ==  "none" else ""
            for x in c["source_layer"]:
                for y in c["target_layer"]:
                    conns.append((prefix_source + x, prefix_target + y, c["params"]))
                        
    for i in conns:
        try:
            nest.topology.ConnectLayers(layers[i[0]][0],layers[i[1]][0],i[2])
        except:
            print("There's something wrong with the following connection definition: ")
            print("{}".format(i))
            sys.exit()
        
    return conns

def print_net_information():
    # Function for printing information about network size
    
    print("***************")
    print("Network size: ", nest.GetKernelStatus(["network_size"]))
    print("Num connections: ", nest.GetKernelStatus(["num_connections"]))
    print("Min delay: ", nest.GetKernelStatus(["min_delay"]))
    print("Max delay: ", nest.GetKernelStatus(["max_delay"]))
    print("***************")

def generate_recorders(p,layers):
    # Function for creating and connecting recorders to the network
    # Input: input parameters from YML files
    # Output: list of recorders
    
    recorders = []
    
    for i in p["network"]["recorders"]["types"]:
        i["params"]["to_file"] = True if "file" in i["params"]["record_to"] else False
        i["params"]["to_memory"] = True if "memory" in i["params"]["record_to"] else False
        
        nest.CopyModel(i["type"],i["name"],i["params"])
        
    for i in p["network"]["recorders"]["record_from"]:
        r = nest.Create(i["recorder"])
        a = p["network"]["recorders"]["types"]
        b=None
        for z in a:
            b = z["params"]["record_from"] if z["name"] == i["recorder"] else b
        
        if not b:
            print("Recordername not recognized. Check the recorders of the input files for consistency.")
            sys.exit()
        
        recorders.append([r, i["layer"],i["population"],b])
        nest.Connect(r,nest.GetLeaves(layers[i["layer"]][0],properties={"model":i["population"]})[0])
    
    return recorders
        
def simulate(p, layers,recorders):
    # Function for running simulations, and updating states of the network when needed
    # Input: input parameters from YML files, list of layers, list of recorders
    
    for state in p["simulation"]["simulation_params"]["sim_sequence"]:
        
        t = p["simulation"]["states"][state]
        print("")
        print("Setting up sequence: '{}' with length {} ms".format(state,t["state_length"]))
        
        changes = []
        objects = []
        
        if "neurons" in t.keys():
            
            for i in t["neurons"]:
                
                
                ls = list(set([layers[x][0] for x in layers.keys() for y in i["layers"] if y in x]))
                ps = list(set([x if isinstance(layers[z][1],list) else layers[z][1] for z in layers.keys() for x in layers[z][1] for y in i["populations"] if y in x]))
                
                temp = []
                
                for x in ls:
                    for y in ps:
                        a=nest.GetLeaves(x,properties={"model":y})
                        if a[0]:
                            temp.extend(a[0])
                
                temp=af.select_pops(temp,nest.GetStatus(temp),i)

                changes.append(copy.deepcopy(i["change"]))
                objects.append(copy.deepcopy(temp))
   
        if "synapses" in t.keys():
            
            for i in t["synapses"]:
                sources = []
                targets = []
                temp = []
                
                ls = list(set([layers[x][0] for x in layers.keys() for y in i["sources"]["layers"] if y in x]))
                ps = list(set([x if isinstance(layers[z][1],list) else layers[z][1] for z in layers.keys() for x in layers[z][1] for y in i["sources"]["populations"] if y in x]))
                lt = list(set([layers[x][0] for x in layers.keys() for y in i["targets"]["layers"] if y in x]))
                pt = list(set([x if isinstance(layers[z][1],list) else layers[z][1] for z in layers.keys() for x in layers[z][1] for y in i["targets"]["populations"] if y in x]))
                
                for x in ls:
                    for y in ps:
                        a=nest.GetLeaves(x,properties={"model":y})
                        if a[0]:
                            sources.extend(a[0])
                for x in lt:
                    for y in pt:
                        a=nest.GetLeaves(x,properties={"model":y})
                        if a[0]:
                            targets.extend(a[0])

                temp = [nest.GetConnections(source=sources,target=targets,synapse_model=i["synapse_type"] if i["synapse_type"] else None)]
                temp = af.select_syns(temp[0],nest.GetStatus(temp[0]),i)
                
                changes.append(copy.deepcopy(i["change"]))
                objects.append(copy.deepcopy(temp))
           
        print("Simulating sequence: '{}' with length {} ms".format(state,t["state_length"]))
        for step in range(t["steps"]):
            print("")
            if t["discard"]:
                for r in recorders:
                    nest.SetStatus(r[0],{"start":nest.GetKernelStatus("time")+t["state_length"]})
            
            for i in range(len(objects)):
                for z in changes[i].keys():
                    temp = af.change_func(nest.GetStatus(list(objects[i]),keys=z),changes[i][z][0],t["steps"],step,changes[i][z][1])
                    temp = [{z:i} for i in temp]
                    nest.SetStatus(list(objects[i]),temp)
            for i in range(100):
                nest.Simulate(t["state_length"]/(t["steps"]*100))
                af.progress_print(i+1,100)