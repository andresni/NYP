# -*- coding: utf-8 -*-
import collections
import yaml
import glob
import os
import numpy as np
import pandas
import nest_interface as ni

def merge_dicts(org, new):
    # Function for merging dictionary trees, and updating them where necessary.
    # Input: an old dictionary, a new dictionary
    # Output: merged dictionary
    # Note: Will in certain instances fail if for example {"hello": "world"} is to be merged with {"hello": {"hi":"world"}}
    #       while {"hello":{"hi":"world"}} can be merged with {"hello":{"yo":"Earth"}} and {"hello":{"hi":"Earth"}}
    
    for k, v in new.items():
        if isinstance(v, collections.Mapping) and not k == "trash":
            org[k] = merge_dicts(org.get(k, {}), v)
        else:
            org[k] = v
    return org   

def read_yml_input(full_path_to_folder):
    # Fucntion for reading YML files, and putting them in a easy to use dictionary
    # Input: path to experiment folder containing "network" and "simulation" folders
    # Output: dictionary containing all the information from all the YML files

    yml_dict ={}

    config = map(lambda x: yaml.load_all(open(x)), glob.glob(full_path_to_folder + "network/*.yml"))
    
    for maps in config:
        for items in maps:
            merge_dicts(yml_dict,items)
            
    config = map(lambda x: yaml.load_all(open(x)), glob.glob(full_path_to_folder + "simulation/*.yml"))
    
    for maps in config:
        for items in maps:
            merge_dicts(yml_dict,items)
    
    return yml_dict

def read_data(rec,p):
    # Function for reading data stored by NEST during simulations (if saving to file)
    # Input: a list of recorders, path to experiment folder, and dictionary of parameters from YML files
    # Output: the data read from disk
    
    files = os.listdir(p["paths"]["temp_path"])

    newdata = pandas.concat([pandas.read_csv(p["paths"]["temp_path"] + "/" + f,sep=r'\t',header=None,engine='python') for f in files if str(rec[0][0]) in f])
    
    return newdata

def reset(p,reset=False):
    # Function for resetting NEST after simulations to save system memory. To save disk space as well, use reset=True.
    # Input: path to experiment folder, parameters from YML files, and optionally reset=True)
    
    if p["simulation"]["output"]["data"]["reset"] or reset:

        files = os.listdir(p["paths"]["temp_path"])
        
        for f in files:
            try:
                os.remove(p["paths"]["temp_path"] + "/" + f)
            except Exception as e:
                print(e)
        
        if not reset:
            ni.initialize(p)