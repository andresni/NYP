# -*- coding: utf-8 -*-
import collections
import numpy as np
import pandas
import os

def merge_dicts(org, new):
    # Function for merging dictionary trees, and updating them where necessary.
    # Input: an old dictionary, a new dictionary
    # Output: merged dictionary
    # Note: Will in certain instances fail if for example {"hello": "world"} is to be merged with {"hello": {"hi":"world"}}
    #       while {"hello":{"hi":"world"}} can be merged with {"hello":{"yo":"Earth"}} and {"hello":{"hi":"Earth"}}
    
    for k, v in new.items():
        if isinstance(v, collections.Mapping) and not k == "trash":
            org[k] = merge_dicts(org.get(k, {}), v)
        elif not k == 'trash':
            if k not in org:
                org[k] = v 
            else:
                v.extend(org[k])
                org[k] = v
    return org

def read_data(rec,p,path_to_temp,path_to_output):
    # Function for reading data stored by NEST during simulations (if saving to file)
    # Input: a list of recorders, path to experiment folder, and dictionary of parameters from YML files
    # Output: the data read from disk
    
    files = os.listdir(path_to_temp)

    newdata = pandas.concat([pandas.read_csv(path_to_temp + "/" + f,sep=r'\t',header=None,engine='python') for f in files if str(rec[0][0]) in f])
    
    return newdata

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