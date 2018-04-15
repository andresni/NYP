# -*- coding: utf-8 -*-

# INTRODUCTION (HELP)
    # Run using python main.py "foldername" i.e. python main.py "example" (from the folder of these files)

# Acknowledgements:
    # Written by: André Sevenius Nilsen (1)
    # Thanks to Thierry Nieus (2), Ricardo Murphy (1), Hans E. Plesser (3,4), Sean Hill (5,6), Will G. Mayner (7), Tom Bugnon (7), Bjørn Juel (1), and Johan Storm (1).
    # (1) Brain Signalling Group, Department of Physiology, Institute of Basic Medical Sciences, University of Oslo, Oslo, Norway
    # (2) Department of Biomedical and Clinical Sciences "Luigi Sacco" University of Milan, Milan, Italy
    # (3) Faculty of Science and Technology, Norwegian University of Life Sciences, Norway
    # (4) Institute for Neuroscience (INM-6), Jülich Research Centre, Jülich, Germany
    # (5) Krembil Centre for Neuroinformatics, CAMH, Toronto, Canada 
    # (6) Blue Brain Project, EPFL, Geneva, Switzerland
    # (7) Wisconsin Institute for Sleep and Consciousness, University of Wisconsin-Madison, USA

# Imports
import sys
import os
import checking_functions as cf
import io_functions as iof
import nest_interface as ni
import output_functions as of
import auxillary_functions as af

# Read input arguments
path_current = os.path.dirname(os.path.abspath("main.py"))
folder = sys.argv[1] 
full_path_to_folder = path_current + "/" + folder + "/"
    
# Read all input files and sort them into dictionaries
file_extension = cf.file_type_check(full_path_to_folder)    
 
if file_extension == "yml":
    input_parameters = iof.read_yml_input(full_path_to_folder)
    
# Create path information
input_parameters = af.path_info(input_parameters,full_path_to_folder)

# Initialize NEST
ni.initialize(input_parameters)

# Copy neuron models into NEST
neuron_models = ni.copy_neurons(input_parameters)

# Generate layers
layers = ni.generate_layers(input_parameters)

# Print information about network size.
ni.print_net_information()

# Copy synapse models into NEST
ni.copy_synapses(input_parameters)

# Generate connections to be established & and connect model
ni.generate_connections(input_parameters,layers)

# Print information about network size.
ni.print_net_information()

# Generate recorders
recorders = ni.generate_recorders(input_parameters,layers)

# Simulate
ni.simulate(input_parameters,layers,recorders)

# Generate and produce required outputs
of.output_data(input_parameters,layers,recorders)

# Reset NEST
iof.reset(input_parameters)

data = []