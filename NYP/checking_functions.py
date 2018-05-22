# -*- coding: utf-8 -*-

def file_folder_integrity(full_path_to_folder):
    #Function that checks if input folder contains all files and folders
    #required by the platform.
    # Input: full pathname of the folder (ex. /run/media/john/platform/sleep_test/)
    # Output: True if everything checks out, false if otherwise
    
    import os
    import glob
    
    check = 1
    
    if not os.path.isdir(full_path_to_folder):
        print(full_path_to_folder + " does not exist.")
        check = 0
    if not os.path.isdir(full_path_to_folder + "network"):
        print(full_path_to_folder + "network" + " does not exist.")
        check = 0
    if not os.path.isdir(full_path_to_folder + "simulation"):
        print(full_path_to_folder + "simulation" + " does not exist.")
        check = 0
    if not os.path.isdir(full_path_to_folder+ "output"):
        os.makedirs(full_path_to_folder + "output")
        
    temp_a = [os.path.basename(x) for x in glob.glob(full_path_to_folder + "network/*")]
    temp_b = [os.path.basename(x) for x in glob.glob(full_path_to_folder + "simulation/*")]
    
    required_net_files = ["synapses","neurons","layers"]
    required_sim_files = ["outputs","states","nest_parameters"]
    
    for i in required_net_files:
        if not any(f.startswith(i) for f in temp_a):
            print(full_path_to_folder + "network/" + i + " does not exist.")
            check = 0
            
    for i in required_sim_files:
        if not any(f.startswith(i) for f in temp_b):
            print(full_path_to_folder + "simulation/" + i + " does not exist.")
            check = 0
 
    return check

def file_type_check(full_path_to_folder):
    # Function that checks filetype (yml or txt)
    # Input: full pathname of the folder (ex. /run/media/john/platform/sleep_test/)
    # Output: txt, yml
    
    import os
    import sys
    
    if os.path.exists(full_path_to_folder + "/network/" + "neurons.txt"):
        return "txt"
    if os.path.exists(full_path_to_folder + "/network/" + "neurons.yml"):
        return "yml"
    
    print("Filetype is neither txt or yml. Make sure it's either txt or yml")
    sys.exit()

    
    