# NEST YAML PLATFORM - NYP - v0.1

This is the initial release of the NEST YAML Platform (NYP). Please see "NYP_Documentation_v02.pdf" for more detailed information regarding the NYP platform.

***Installation:***

Download repository to a folder of your choice.

***Usage:***

In terminal, navigate to the folder you downloaded this platform to (the folder containing "main.py".

Then type 'python main.py "your_experiment_folder"' in terminal.

For example: 

python main.py "example" <- this runs the attached "example" network.

***Dependencies:***

Python 3.x

NEST 2.12

  Python packages:  
  YAML
  Numpy
  Matplotlib
  Scipy
  Pandas
  Collections

***You want to use the platform or attached ht_model for your project?***

Excellent! If the current platform or ht_model version is to be used in scientific or commercial work, please contact *sevenius.nilsen@gmail.com* for possible collaboration.

***Thanks to:***

Thierry Nieus (2), Ricardo Murphy (1), Hans E. Plesser (3,4), Sean Hill (5,6), Will G. Mayner (7), Tom Bugnon (7), Bjørn Juel (1), and Johan Storm (1).


(1) Brain Signalling Group, Department of Physiology, Institute of Basic Medical Sciences, University of Oslo, Oslo, Norway
(2) Department of Biomedical and Clinical Sciences "Luigi Sacco" University of Milan, Milan, Italy
(3) Faculty of Science and Technology, Norwegian University of Life Sciences, Ås, Norway
(4) Institute for Neuroscience (INM-6), Jülich Research Centre, Jülich, Germany
(5) Krembil Centre for Neuroinformatics, CAMH, Toronto, Canada 
(6) Blue Brain Project, EPFL, Geneva, Switzerland
(7) Wisconsin Institute for Sleep and Consciousness, University of Wisconsin-Madison, USA

***Addendum:***
To use certain neuron models necessary for succesfully running the attached "ht_model" you'll need to add certain neuron models to your local NEST installation.
Step 1: copy&replace the contents of the "NEST_neuron_models" folder into your pre-compiled NEST folder structure. That is, the "models" and "nestkernel" subfolders should be copied into your NEST source folder. Accept any prompts for replacement. Then run your standard installation routine.
To verify that everything has worked corretly (in python):
import nest
nest.GetDefaults("ht_neuron_sh") -> should print a range of neuron parameters.





