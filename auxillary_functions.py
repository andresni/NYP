# -*- coding: utf-8 -*-
import numpy as np

def path_info(p,full_path_to_folder):
    # Function for setting path variables correctly for later use
    # Input: parameters from YML files
    # Ouput: parameters from YML files plus path variables
    
    p["paths"] = {
            "main_path": full_path_to_folder,
            "experiment_path": full_path_to_folder,
            "temp_path": full_path_to_folder + p["simulation"]["nest_initialization"]["data_path"],
            "output_path": full_path_to_folder + "/output/" +  p["simulation"]["output"]["data"]["save"]["name"]
            }
    p["simulation"]["nest_initialization"]["data_path"] = p["paths"]["temp_path"]
    
    return p

def select_pops(pops,statuses,p):
    # Function for selecting specific neurons from a long list possible neurons, given specific parameters
    # Input: list of neuron IDs, a list the neuron IDs status's, inpur parameters from YML files
    # Output: list of neuron IDs
    
    
    pop = [i for i in pops]
    pops = []
    stat = [i for i in statuses]

    if "modulators" in p.keys():
        if "properties" in p["modulators"].keys():
            
            for i in range(len(pop)):
                b = True
                for z in p["modulators"]["properties"].keys():
                    if p["modulators"]["if"] == 1:
                        if stat[i][z] != p["modulators"]["properties"][z]:
                            b = False
                    elif p["modulators"]["if"] == 0:
                        if stat[i][z] != p["modulators"]["properties"][z]:
                            b = False
                    elif p["modulators"]["if"] == 2:
                        if stat[i][z] > p["modulators"]["properties"][z]:
                            b = False
                    elif p["modulators"]["if"] == 3:
                        if stat[i][z] < p["modulators"]["properties"][z]:
                            b = False
                if b:
                    pops.extend(pop[i])       
        else:
            pops = pop
                    
        if "probability" in p["modulators"].keys():
            n = int(len(pop)*p["modulators"]["probability"])
            pops = np.random.choice(pop,n,replace=False)
            
    else:
        pops = pop
    
    
    return pops
    
def select_syns(syns,statuses,p):
    # Function for selecting specific synapses from a long list possible synapses, given specific parameters
    # Input: list of synapse IDs, a list the synapse IDs status's, inpur parameters from YML files
    # Output: list of synapse IDs
        
    syn = [i for i in syns]
    syns = []

    stat = [i for i in statuses]
    
    for i in range(len(syn)):
        
        syns.extend(syn[i] if stat[i]["target"] else [])
    
    if "modulators" in p.keys():
        if "properties" in p["modulators"].keys():
            
            for i in range(len(syn)):
                b = True
                for z in p["modulators"]["properties"].keys():
                    if p["modulators"]["if"] == 1:
                        if stat[i][z] != p["modulators"]["properties"][z]:
                            b = False
                    elif p["modulators"]["if"] == 0:
                        if stat[i][z] != p["modulators"]["properties"][z]:
                            b = False
                    elif p["modulators"]["if"] == 2:
                        if stat[i][z] > p["modulators"]["properties"][z]:
                            b = False
                    elif p["modulators"]["if"] == 3:
                        if stat[i][z] < p["modulators"]["properties"][z]:
                            b = False
                if b:
                    syns.extend(syn[i])
        else:
            syns = syn
                    
        if "probability" in p["modulators"].keys():
            n = int(len(syn)*p["modulators"]["probability"])
            syns = np.random.choice(syn,n,replace=False)
            
    else:
        syns = syn
    
    
    return syns

def change_func(value1,value2,steps,step,mode):
    # Function that calculates the updated values of every given neuron/synapse ID sent to it, incrementally (if necessary)
    # Input: a list of original values of parameter from neurons/synapses, value to update with, number of steps update should happen over, which calculation to use
    # Output: a list of updated values
    
    if mode == "c":
        step = steps - step
        return [value1[i]+((value2-value1[i])/step) for i in range(len(value1))]
    if mode == "p":
        return [value1[i] * value2**(1/steps) for i in range(len(value1))]
    if mode == "a":
        return [value1[i] + value2/steps for i in range(len(value1))]
    if mode == "r":
        return np.random.uniform(value2[0],value2[1],len(value1))
    if mode == "code":
        return eval(value2,{"value1":value1,"value2":value2,"steps":steps,"step":step,"mode":mode})
    

def progress_print(a,length):
    # Function for printing progress bars
    # Input: iterator, total
    
    print("\r  --Progress: {}%".format(int(a/length*100)),end="",flush=True)